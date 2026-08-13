#!/usr/bin/env python3
"""ClaudeRuntime Wave 0 sourcemap generator.

Scans ``src/`` top-level modules, extracts an AST-level inventory (files,
classes, functions, imports), maps each module to candidate R7/R5/CCR-14
nodes, renders a per-module markdown report, converts it to a self-contained
HTML file with a collapsible sidebar (via the markdown-to-html skill script),
and builds a navigation index page.

Inputs:
    --src   source root (default: <repo>/src)
    --out   output root (default: <repo>/docs/sourcemap)
    --ts    timestamp override YYYYMMDD_HHMM (default: now)
    --only  comma-separated module names to process (default: all)

Outputs (one snapshot run):
    docs/sourcemap/NN-<module>-<ts>.html      per-module report
    docs/sourcemap/markdown/NN-<module>-<ts>.md  markdown source of each report
    docs/sourcemap/index.html                  navigation index

Naming rule: NN-<module>-<YYYYMMDD_HHMM>.html (number fixed by alphabetical
module order; timestamp identifies the snapshot run).

Design notes:
- Pure stdlib (ast) so the scanner runs anywhere without project deps.
- R7/R5/CCR-14 mappings are heuristic first-pass guesses, always stamped
  UNVERIFIED per B3 rule "unconfirmed items stay UNKNOWN".
- The markdown renderer deliberately avoids GFM tables, bold-led list items
  and nested lists — the md2html_sidebar converter does not support them.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MD2HTML_SCRIPT = (
    Path.home()
    / ".hermes/skills/creative/markdown-to-html/scripts/md2html_sidebar.py"
)
BASELINE_COMMIT = "def709361a86900920bf1d6b75134fdc9bc59def"
REFERENCE_COMMIT = "a8a678cb6244e6770e1e421767ff0987a1d95549"
REFERENCE_VERSION = "2.1.88"
REFERENCE_REPO = "ChinaSiro/claude-code-sourcemap"
PAPER = "arXiv:2604.14228v2"
SHIM_LINES = 60  # 小模块/占位判定阈值（总行数）

# ---------------------------------------------------------------------------
# 启发式映射表：模块名 → (R7 候选, R5 候选, CCR 候选)
# 全部为 UNVERIFIED 初版，仅供 Wave 0 起步；后续逐项核实后升级。
# ---------------------------------------------------------------------------
HEURISTIC_MAP: dict[str, tuple[list[str], list[str], list[str]]] = {
    "agent": (["R7-03"], ["R5-02"], ["CCR-11"]),
    "assistant": (["R7-02"], ["R5-01"], []),
    "auth": (["R7-04"], ["R5-03"], ["CCR-02", "CCR-13"]),
    "background": ([], [], ["CCR-11", "CCR-10", "CCR-14"]),
    "bootstrap": (["R7-02"], ["R5-01"], ["CCR-14"]),
    "bridge": (["R7-02"], ["R5-01"], ["CCR-14"]),
    "buddy": (["R7-02"], ["R5-01"], []),
    "cli_backup": (["R7-02"], ["R5-01"], []),
    "cli_core": (["R7-02"], ["R5-01"], []),
    "command_system": (["R7-02"], ["R5-01"], []),
    "compact_service": ([], [], ["CCR-03"]),
    "components": (["R7-02"], ["R5-01"], []),
    "constants": ([], [], ["CCR-14"]),
    "context_system": ([], [], ["CCR-03", "CCR-04"]),
    "coordinator": ([], [], ["CCR-06"]),
    "eco": ([], [], []),
    "entrypoints": (["R7-02"], ["R5-01"], []),
    "execution": (["R7-07"], ["R5-05"], ["CCR-12"]),
    "goals": (["R7-03"], ["R5-02"], []),
    "hooks": ([], [], ["CCR-01"]),
    "keybindings": (["R7-02"], ["R5-01"], []),
    "knowledge": ([], ["R5-04"], []),
    "memdir": ([], ["R5-04"], []),
    "memory": ([], ["R5-04"], []),
    "migrations": ([], [], ["CCR-10"]),
    "models": ([], [], ["CCR-14"]),
    "moreright": ([], [], []),
    "native_ts": ([], [], []),
    "outputStyles": ([], [], ["CCR-14"]),
    "permissions": (["R7-04"], ["R5-03"], ["CCR-02", "CCR-13"]),
    "plan": (["R7-03"], ["R5-02"], []),
    "plugins": ([], [], ["CCR-05"]),
    "providers": ([], ["R5-05"], []),
    "query": (["R7-03"], ["R5-02"], ["CCR-03", "CCR-04", "CCR-08", "CCR-14"]),
    "reference_data": ([], [], ["CCR-14"]),
    "remote": ([], ["R5-05"], ["CCR-12"]),
    "scheduled_tasks": ([], [], ["CCR-14"]),
    "schemas": ([], [], []),
    "screens": (["R7-02"], ["R5-01"], []),
    "server": (["R7-02"], ["R5-01"], ["CCR-14"]),
    "services": ([], [], ["CCR-06", "CCR-14"]),
    "settings": ([], [], ["CCR-14"]),
    "skills": ([], [], ["CCR-05"]),
    "state": (["R7-06"], ["R5-04"], ["CCR-10"]),
    "tasks": ([], [], ["CCR-06"]),
    "tool_system": (["R7-05"], ["R5-03"], ["CCR-05", "CCR-06", "CCR-07", "CCR-09"]),
    "transports": (["R7-02"], ["R5-01"], []),
    "types": ([], [], ["CCR-14"]),
    "upstreamproxy": ([], ["R5-05"], ["CCR-12"]),
    "utils": ([], [], []),
    "vim": (["R7-02"], ["R5-01"], []),
    "voice": (["R7-02"], ["R5-01"], []),
    "wiki": ([], ["R5-04"], []),
    "workflow": (["R7-05"], ["R5-03"], []),
    # core 单文件组
    "core-single-files": (["R7-02"], ["R5-01"], ["CCR-14"]),
}

# 单文件组内每个文件 → (R7, R5, CCR) 细分映射
SINGLE_FILE_MAP: dict[str, tuple[list[str], list[str], list[str]]] = {
    "cli.py": (["R7-02"], ["R5-01"], []),
    "config.py": ([], [], ["CCR-14"]),
    "costHook.py": ([], [], ["CCR-01"]),
    "cost_tracker.py": ([], [], ["CCR-09"]),
    "deferred_init.py": ([], [], ["CCR-14"]),
    "history.py": ([], [], ["CCR-10"]),
    "init.py": (["R7-03"], ["R5-02"], []),
    "prefetch.py": ([], [], ["CCR-07"]),
    "projectOnboardingState.py": ([], [], ["CCR-14"]),
    "secret_store.py": ([], [], ["CCR-13"]),
    "task_registry.py": ([], [], ["CCR-06"]),
    "tasks_core.py": ([], [], ["CCR-06"]),
    "token_estimation.py": ([], [], ["CCR-03"]),
}

# 与 B3 04 矩阵一致的正式坐标
R7_LABELS = {
    "R7-01": "User",
    "R7-02": "Interfaces",
    "R7-03": "Agent Loop",
    "R7-04": "Permission System",
    "R7-05": "Tools",
    "R7-06": "State & Persistence",
    "R7-07": "Execution Environment",
}
R5_LABELS = {
    "R5-01": "Surface Layer",
    "R5-02": "Core Layer",
    "R5-03": "Safety / Action Layer",
    "R5-04": "State Layer",
    "R5-05": "Backend Layer",
}
CCR_LABELS = {
    "CCR-01": "Hook Runtime",
    "CCR-02": "Authorization Pipeline",
    "CCR-03": "Context Shaping Pipeline",
    "CCR-04": "Context Assembly / Injection",
    "CCR-05": "Tool Pool / Capability Assembly",
    "CCR-06": "Tool Orchestration",
    "CCR-07": "Streaming Tool Execution",
    "CCR-08": "Recovery / Resilience Controller",
    "CCR-09": "Result Normalization / Result Budget",
    "CCR-10": "Session / Transcript Runtime",
    "CCR-11": "Subagent Orchestration",
    "CCR-12": "Isolation Runtime",
    "CCR-13": "Trust Lifecycle",
    "CCR-14": "Runtime Config / Feature Gate Control Plane",
}

# ---------------------------------------------------------------------------
# Reference 侧（restored-src）盘点配置
# ---------------------------------------------------------------------------
# reference 模块 → python 候选模块（启发式初版，全部 UNVERIFIED）
REF_TO_PY_MAP: dict[str, list[str]] = {
    "assistant": ["assistant"],
    "bootstrap": ["bootstrap"],
    "bridge": ["bridge"],
    "buddy": ["buddy"],
    "cli": ["cli_core", "entrypoints", "core-single-files"],
    "commands": ["command_system"],
    "components": ["components"],
    "constants": ["constants"],
    "context": ["context_system", "compact_service"],
    "coordinator": ["coordinator"],
    "entrypoints": ["entrypoints"],
    "hooks": ["hooks"],
    "ink": ["transports", "screens"],
    "keybindings": ["keybindings"],
    "memdir": ["memdir"],
    "migrations": ["migrations"],
    "moreright": ["moreright"],
    "native-ts": ["native_ts"],
    "outputStyles": ["outputStyles"],
    "plugins": ["plugins"],
    "query": ["query"],
    "remote": ["remote"],
    "schemas": ["schemas"],
    "screens": ["screens"],
    "server": ["server"],
    "services": ["services"],
    "skills": ["skills"],
    "state": ["state"],
    "tasks": ["tasks"],
    "tools": ["tool_system"],
    "types": ["types"],
    "upstreamproxy": ["upstreamproxy"],
    "utils": ["utils"],
    "vim": ["vim"],
    "voice": ["voice"],
    "top-level-files": ["core-single-files", "entrypoints"],
}

# python 侧存在但 reference 无同名模块 → 待定位的缺口（UNKNOWN）
PY_ONLY_MODULES = [
    "auth", "background", "compact_service", "eco", "execution", "goals",
    "knowledge", "memory", "models", "permissions", "plan", "providers",
    "reference_data", "scheduled_tasks", "settings", "workflow",
]

REF_TS_EXT = (".ts", ".tsx", ".js", ".mjs", ".cjs", ".jsx")
# TS/JS 顶层符号启发式正则（行号由文本前缀计数推算）
TS_CLASS_RE = re.compile(
    r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)", re.MULTILINE
)
TS_FUNC_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)", re.MULTILINE
)
TS_EXPORT_CONST_RE = re.compile(
    r"^\s*export\s+(?:const|let|var|async\s+function)\s+(\w+)", re.MULTILINE
)
TS_IMPORT_FROM_RE = re.compile(
    r"import[^'\"]*?from\s+['\"]([^'\"]+)['\"]", re.MULTILINE
)
TS_REQUIRE_RE = re.compile(r"require\(\s*['\"]([^'\"]+)['\"]")


@dataclass
class SymbolInfo:
    """AST 符号：类或顶层函数，含定义行号。"""

    name: str
    line: int


@dataclass
class FileInventory:
    """单文件盘点结果。"""

    rel_path: str
    lines: int
    classes: list[SymbolInfo] = field(default_factory=list)
    funcs: list[SymbolInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


@dataclass
class ModuleSpec:
    """模块定义：编号、名称、路径、类型。"""

    index: int
    name: str
    path: Path
    kind: str  # "package" | "group"


@dataclass
class ModuleReport:
    """模块盘点报告（markdown 渲染的输入）。"""

    spec: ModuleSpec
    files: list[FileInventory] = field(default_factory=list)
    total_lines: int = 0
    src_internal_imports: list[str] = field(default_factory=list)
    r7: list[str] = field(default_factory=list)
    r5: list[str] = field(default_factory=list)
    ccr: list[str] = field(default_factory=list)
    file_map: dict[str, tuple[list[str], list[str], list[str]]] = field(
        default_factory=dict
    )
    py_candidates: list[str] = field(default_factory=list)  # reference 侧专用

    @property
    def is_shim(self) -> bool:
        """总行数低于阈值且文件数很少 → 占位/小模块。"""
        return self.total_lines <= SHIM_LINES and len(self.files) <= 2


def module_name_regex() -> re.Pattern[str]:
    """命名规则：NN-模块名-YYYYMMDD_HHMM.html。"""
    return re.compile(r"^\d{2}-[a-z0-9_-]+-\d{8}_\d{4}\.html$")


def discover_modules(src_root: Path) -> list[ModuleSpec]:
    """扫描 src 顶层：目录模块（字母序编号）+ core 单文件组。"""
    specs: list[ModuleSpec] = []
    for path in sorted(src_root.iterdir()):
        if not path.is_dir() or path.name in ("__pycache__",):
            continue
        specs.append(ModuleSpec(index=0, name=path.name, path=path, kind="package"))
    # 单文件组：src 顶层 *.py（不含 __init__.py）
    single_files = sorted(
        p for p in src_root.glob("*.py") if p.name != "__init__.py"
    )
    if single_files:
        specs.append(
            ModuleSpec(
                index=0,
                name="core-single-files",
                path=src_root,
                kind="group",
            )
        )
    specs.sort(key=lambda s: s.name)
    for i, spec in enumerate(specs, start=1):
        spec.index = i
    return specs


def scan_file(path: Path, src_root: Path) -> FileInventory:
    """AST 盘点单个 .py 文件：行数、类、顶层函数、import 目标模块。

    支持绝对导入与相对导入（level>0）：相对导入按文件所在包深度推算
    目标顶层模块（如 src/query/x.py 中 ``from ..tool_system.y import z``
    → 顶层目标 tool_system）。
    """
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        # 二进制/编码异常文件：仅登记行数，符号留空并标注
        lines = sum(1 for _ in path.open("rb"))
        return FileInventory(
            rel_path=str(path.relative_to(src_root)), lines=lines
        )
    tree = ast.parse(source, filename=str(path))
    lines = source.count("\n")
    inv = FileInventory(
        rel_path=str(path.relative_to(src_root)),
        lines=lines,
    )
    # 文件在 src 下的包深度（parts 去掉文件名）
    parts = path.relative_to(src_root).parts
    pkg_depth = max(len(parts) - 1, 0)

    def _register(top: str) -> None:
        if top and top not in inv.imports:
            inv.imports.append(top)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            inv.classes.append(SymbolInfo(node.name, node.lineno))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            inv.funcs.append(SymbolInfo(node.name, node.lineno))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                _register((alias.name or "").split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                # 相对导入：level=1 当前包；level=2 父包，依此类推
                base_depth = pkg_depth - (node.level - 1)
                if base_depth < 0:
                    continue  # 越过 src 根（如包外），忽略
                target = list(parts[:base_depth])
                if node.module:
                    target += node.module.split(".")
                _register(target[0] if target else "")
            else:
                _register((node.module or "").split(".")[0])
    return inv


def scan_module(spec: ModuleSpec, src_root: Path) -> ModuleReport:
    """扫描一个模块的全部 .py 文件并汇总。"""
    report = ModuleReport(spec=spec)
    if spec.kind == "package":
        py_files = sorted(spec.path.rglob("*.py"))
        report.file_map = {
            f.name: HEURISTIC_MAP.get(spec.name, ([], [], [])) for f in py_files
        }
    else:
        # 单文件组：每个文件单独映射
        py_files = sorted(spec.path.glob("*.py"))
        if "__init__.py" in [p.name for p in py_files]:
            py_files = [p for p in py_files if p.name != "__init__.py"]
        report.file_map = {
            f.name: SINGLE_FILE_MAP.get(f.name, ([], [], [])) for f in py_files
        }
    for f in py_files:
        inv = scan_file(f, src_root)
        report.files.append(inv)
        report.total_lines += inv.lines
    # src 内部依赖（调用边初版：模块级 import，排除自身包内引用）
    internal = set()
    for inv in report.files:
        for mod in inv.imports:
            if mod == spec.name:
                continue  # 包内自引用不是跨模块边
            if (src_root / mod).is_dir() or (src_root / f"{mod}.py").is_file():
                internal.add(mod)
    report.src_internal_imports = sorted(internal)
    report.r7, report.r5, report.ccr = HEURISTIC_MAP.get(
        spec.name, ([], [], [])
    )
    return report


# ---------------------------------------------------------------------------
# Reference 侧（restored-src）盘点
# ---------------------------------------------------------------------------
def discover_reference_modules(ref_root: Path) -> list[ModuleSpec]:
    """扫描 reference src 顶层：目录模块（字母序编号）+ top-level 单文件组。"""
    specs: list[ModuleSpec] = []
    for path in sorted(ref_root.iterdir()):
        if not path.is_dir() or path.name in ("__pycache__",):
            continue
        specs.append(ModuleSpec(index=0, name=path.name, path=path, kind="package"))
    top_files = sorted(
        p
        for p in ref_root.iterdir()
        if p.is_file()
        and p.suffix in REF_TS_EXT
        and p.name not in ("main.tsx", "index.tsx", "index.ts")
    )
    if top_files:
        specs.append(
            ModuleSpec(
                index=0, name="top-level-files", path=ref_root, kind="group"
            )
        )
    specs.sort(key=lambda s: s.name)
    for i, spec in enumerate(specs, start=1):
        spec.index = i
    return specs


def _resolve_ref_top(import_target: str, file_dir: Path, ref_root: Path) -> str | None:
    """把 TS import 目标规约为 reference 顶层模块名；外部包/越界返回 None。"""
    target = import_target.split("#")[0].split("?")[0]
    for ext in REF_TS_EXT:
        if target.endswith(ext):
            target = target[: -len(ext)]
            break
    if target.startswith("src/"):
        parts = target.split("/")
        return parts[1] if len(parts) > 1 else None
    if target.startswith("."):
        try:
            resolved = (file_dir / target).resolve()
            resolved = resolved.relative_to(ref_root)
        except (ValueError, OSError):
            return None  # 越出 ref_root（如 ../..）
        return resolved.parts[0] if resolved.parts else None
    return None  # 外部包（@anthropic-ai 等）


def scan_ts_file(path: Path, ref_root: Path) -> FileInventory:
    """启发式盘点单个 TS/JS 文件：行数、类/函数/导出符号、import 目标。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        text = path.read_text(encoding="utf-8", errors="replace")
    inv = FileInventory(
        rel_path=str(path.relative_to(ref_root)),
        lines=text.count("\n"),
    )

    seen: set[tuple[str, int]] = set()
    for m in TS_CLASS_RE.finditer(text):
        ln = text[: m.start()].count("\n") + 1
        if (m.group(1), ln) not in seen:
            seen.add((m.group(1), ln))
            inv.classes.append(SymbolInfo(m.group(1), ln))
    for m in list(TS_FUNC_RE.finditer(text)) + list(TS_EXPORT_CONST_RE.finditer(text)):
        ln = text[: m.start()].count("\n") + 1
        if (m.group(1), ln) not in seen:
            seen.add((m.group(1), ln))
            inv.funcs.append(SymbolInfo(m.group(1), ln))
    # import 目标规约（相对导入按文件目录解析）
    file_dir = path.parent
    for m in list(TS_IMPORT_FROM_RE.finditer(text)) + list(TS_REQUIRE_RE.finditer(text)):
        top = _resolve_ref_top(m.group(1), file_dir, ref_root)
        if top and top not in inv.imports:
            inv.imports.append(top)
    return inv


def scan_reference_module(spec: ModuleSpec, ref_root: Path) -> ModuleReport:
    """扫描 reference 模块全部 TS/JS 文件并汇总 python 候选映射。"""
    report = ModuleReport(spec=spec)
    if spec.kind == "package":
        files = sorted(
            p for p in spec.path.rglob("*") if p.suffix in REF_TS_EXT
        )
    else:
        files = sorted(
            p
            for p in spec.path.iterdir()
            if p.is_file()
            and p.suffix in REF_TS_EXT
            and p.name not in ("main.tsx", "index.tsx", "index.ts")
        )
    for f in files:
        inv = scan_ts_file(f, ref_root)
        report.files.append(inv)
        report.total_lines += inv.lines
    internal: set[str] = set()
    for inv in report.files:
        for mod in inv.imports:
            if mod == spec.name:
                continue
            if (ref_root / mod).is_dir() or (ref_root / f"{mod}.ts").is_file():
                internal.add(mod)
    report.src_internal_imports = sorted(internal)
    report.py_candidates = REF_TO_PY_MAP.get(spec.name, [])
    return report


def render_reference_markdown(report: ModuleReport, ts: str) -> str:
    """渲染 reference 模块盘点 markdown。"""
    spec = report.spec
    kind_label = {
        "package": "package（reference 目录模块）",
        "group": "group（reference 顶层单文件组）",
    }[spec.kind]
    py_label = (
        ", ".join(report.py_candidates) if report.py_candidates else "UNKNOWN（无候选）"
    )
    lines: list[str] = [
        f"# {spec.name}（reference）源码盘点",
        f"> 编号: {spec.index:02d}",
        f"> 时间戳: {ts}",
        f"> Reference: Claude Code {REFERENCE_VERSION} @ {REFERENCE_COMMIT[:12]}",
        f"> 来源: restored-src/src/{spec.name}",
        f"> 类型: {kind_label}",
        "> 盘点状态: INVENTORY_COMPLETE",
        "> 映射状态: UNVERIFIED（启发式初版，待逐项核实）",
        "",
        "## 1. 模块概况",
        "",
        "1. 模块名: " + spec.name,
        "2. 类型: " + kind_label,
        "3. TS/JS 文件数: " + str(len(report.files)),
        "4. 总行数: " + str(report.total_lines),
        "5. 依赖的 reference 内部模块: "
        + (", ".join(report.src_internal_imports) if report.src_internal_imports else "无"),
        "6. Python 侧候选映射: " + py_label + "（UNVERIFIED）",
        "7. 一句话职责: UNKNOWN（待人工核实）",
        "",
        "## 2. 文件清单",
        "",
    ]
    for inv in report.files:
        lines.append(
            f"1. `{inv.rel_path}` — {inv.lines} 行（类 {len(inv.classes)}，"
            f"函数 {len(inv.funcs)}）"
        )
    lines += ["", "## 3. 关键符号", ""]
    for inv in report.files:
        lines.append(f"1. 文件 `{inv.rel_path}`")
        for cls in inv.classes[:60]:
            lines.append(f"1. 类 {cls.name} — L{cls.line}")
        for fn in inv.funcs[:60]:
            lines.append(f"1. 函数 {fn.name} — L{fn.line}")
    lines += ["", "## 4. 依赖与调用边（import 级）", ""]
    seen: set[tuple[str, str]] = set()
    for inv in report.files:
        for mod in inv.imports:
            key = (inv.rel_path, mod)
            if key in seen:
                continue
            seen.add(key)
            tag = "内部" if mod in report.src_internal_imports else "外部"
            lines.append(f"1. {inv.rel_path} → import {mod}（{tag}）")
    if not seen:
        lines.append("1. 无内部 import（或无法解析）")
    lines += ["", "## 5. Python 侧候选映射（启发式初版）", ""]
    if report.py_candidates:
        for py_mod in report.py_candidates:
            lines.append(
                f"1. → python `{py_mod}` — 候选（启发式），状态 UNVERIFIED"
            )
    else:
        lines.append("1. 暂无候选 — 状态 UNKNOWN")
    lines += ["", "## 6. 未确认项与待核实项", ""]
    lines.append("1. ☐ 模块一句话职责待人工核实")
    lines.append("1. ☐ python 候选映射待逐符号对照核实（symbol 级 map 未生成）")
    lines.append("1. ☐ 关键 call-edge/state-edge 待逐条对照 python 实现")
    lines.append("1. ☐ 顶层符号提取为启发式正则，需人工抽样验证召回率")
    lines.append("")
    return "\n".join(lines)


def render_reference_index_markdown(reports: list[ModuleReport], ts: str) -> str:
    """渲染 reference index：双向映射总览 + 模块索引 + python-only 缺口。"""
    total_files = sum(len(r.files) for r in reports)
    total_lines = sum(r.total_lines for r in reports)
    mapped = sum(1 for r in reports if r.py_candidates)
    lines: list[str] = [
        "# ClaudeRuntime Reference 源码盘点索引（restored-src）",
        f"> 时间戳: {ts}",
        f"> Reference: Claude Code {REFERENCE_VERSION} @ {REFERENCE_COMMIT}",
        f"> 来源: {REFERENCE_REPO} restored-src/",
        "> 生成器: scripts/sourcemap_generator.py",
        "",
        "## 1. Reference↔Python 双向映射总览（UNVERIFIED 初版）",
        "",
        f"1. reference 模块总数: {len(reports)}（候选映射 {mapped}，无候选 {len(reports) - mapped}）",
        "2. 映射状态: 全部 UNVERIFIED（启发式同名/特表匹配，待逐项核实）",
        "3. python 侧无同名 reference 的模块（待定位，UNKNOWN）: "
        + ", ".join(PY_ONLY_MODULES),
        "4. 既有证据种子: docs/parity/source-map/*.yaml（旧基线 d29bfe/241d704，"
        "含 PKG-QUERY-001 等 5 条 symbol 映射，需在当前基线 def7093 下复核）",
        "",
        "## 2. Reference 模块索引",
        "",
    ]
    for r in reports:
        fname = f"{r.spec.index:02d}-{r.spec.name}-{ts}.html"
        cand = (
            ", ".join(r.py_candidates) if r.py_candidates else "UNKNOWN"
        )
        lines.append(
            f"1. {r.spec.index:02d} {r.spec.name} — {len(r.files)} 文件 "
            f"{r.total_lines} 行 → [{fname}](../{fname})（候选: {cand}）"
        )
    lines += [
        "",
        "## 3. 统计",
        "",
        f"1. TS/JS 文件总数: {total_files}",
        f"2. reference 源码总行数: {total_lines}",
        "3. 命名规则: NN-模块名-YYYYMMDD_HHMM.html（与 python 侧一致）",
        "",
        "## 4. 未确认项",
        "",
        "1. ☐ 全部 python 候选映射均为启发式初版，状态 UNVERIFIED",
        "2. ☐ PY_ONLY_MODULES 的 reference 落点未定位（permissions/memory/compact 等）",
        "3. ☐ 旧 yaml 证据种子需在当前基线复核（query 包 SEMANTIC_EQUIVALENT 是否仍成立）",
        "4. ☐ 顶层符号提取为启发式正则，需抽样验证召回率",
        "",
    ]
    return "\n".join(lines)


def generate_reference(
    ref_root: Path,
    out_root: Path,
    ts: str | None = None,
    only: list[str] | None = None,
    convert: bool = True,
) -> list[Path]:
    """执行一次 reference 侧盘点快照，返回生成的 HTML 列表。"""
    ts = ts or datetime.now().strftime("%Y%m%d_%H%M")
    ref_root = ref_root.resolve()
    out_root = out_root.resolve()
    md_dir = out_root / "markdown"
    md_dir.mkdir(parents=True, exist_ok=True)

    specs = discover_reference_modules(ref_root)
    if only:
        specs = [s for s in specs if s.name in only]
    reports = [scan_reference_module(s, ref_root) for s in specs]

    html_files: list[Path] = []
    for report in reports:
        md = render_reference_markdown(report, ts)
        md_path = md_dir / f"{report.spec.index:02d}-{report.spec.name}-{ts}.md"
        html_path = out_root / f"{report.spec.index:02d}-{report.spec.name}-{ts}.html"
        md_path.write_text(md, encoding="utf-8")
        if convert:
            convert_md_to_html(md_path, html_path)
            html_files.append(html_path)

    index_md = render_reference_index_markdown(reports, ts)
    index_md_path = md_dir / f"index-{ts}.md"
    index_md_path.write_text(index_md, encoding="utf-8")
    index_html = out_root / "index.html"
    if convert:
        convert_md_to_html(index_md_path, index_html)
        html_files.append(index_html)
    return html_files


def render_markdown(report: ModuleReport, ts: str) -> str:
    """渲染模块盘点 markdown（规避 md2html 不支持的语法）。"""
    spec = report.spec
    kind_label = {
        "package": "package（目录模块）",
        "group": "group（core 单文件组）",
    }[spec.kind]
    shim_note = "；占位/小模块（<={} 行）".format(SHIM_LINES) if report.is_shim else ""
    lines: list[str] = [
        f"# {spec.name} 源码盘点",
        f"> 编号: {spec.index:02d}",
        f"> 时间戳: {ts}",
        f"> 基线: {BASELINE_COMMIT[:12]}",
        f"> Reference: Claude Code {REFERENCE_VERSION} @ {REFERENCE_COMMIT[:12]}",
        f"> 类型: {kind_label}{shim_note}",
        "> 盘点状态: INVENTORY_COMPLETE",
        "> 映射状态: UNVERIFIED（启发式初版，待逐项核实）",
        "",
        "## 1. 模块概况",
        "",
        "1. 模块名: " + spec.name,
        "2. 类型: " + kind_label,
        "3. Python 文件数: " + str(len(report.files)),
        "4. 总行数: " + str(report.total_lines),
        "5. 依赖的 src 内部模块: "
        + (", ".join(report.src_internal_imports) if report.src_internal_imports else "无"),
        "6. 一句话职责: UNKNOWN（待人工核实）",
        "",
        "## 2. 文件清单",
        "",
    ]
    for inv in report.files:
        lines.append(
            f"1. `{inv.rel_path}` — {inv.lines} 行（类 {len(inv.classes)}，"
            f"函数 {len(inv.funcs)}）"
        )
    lines += ["", "## 3. 关键符号", ""]
    for inv in report.files:
        lines.append(f"1. 文件 `{inv.rel_path}`")
        for cls in inv.classes:
            lines.append(f"1. 类 {cls.name} — L{cls.line}")
        for fn in inv.funcs:
            lines.append(f"1. 函数 {fn.name} — L{fn.line}")
    lines += ["", "## 4. 依赖与调用边（import 级）", ""]
    seen: set[tuple[str, str]] = set()
    for inv in report.files:
        for mod in inv.imports:
            key = (inv.rel_path, mod)
            if key in seen:
                continue
            seen.add(key)
            tag = "内部" if mod in report.src_internal_imports else "外部"
            lines.append(f"1. {inv.rel_path} → import {mod}（{tag}）")
    if not seen:
        lines.append("1. 无 import（或无可解析 import）")
    lines += ["", "## 5. R7/R5/CCR-14 映射（启发式初版）", ""]
    for node in report.r7:
        lines.append(
            f"1. {node} {R7_LABELS.get(node, '')} — 候选（启发式），状态 UNVERIFIED"
        )
    for node in report.r5:
        lines.append(
            f"1. {node} {R5_LABELS.get(node, '')} — 候选（启发式），状态 UNVERIFIED"
        )
    for node in report.ccr:
        lines.append(
            f"1. {node} {CCR_LABELS.get(node, '')} — 候选（启发式），状态 UNVERIFIED"
        )
    if not (report.r7 or report.r5 or report.ccr):
        lines.append("1. 暂无候选映射 — 状态 UNKNOWN")
    if report.file_map:
        lines += ["", "## 6. 文件级映射细分", ""]
        for fname, (r7, r5, ccr) in sorted(report.file_map.items()):
            nodes = r7 + r5 + ccr
            label = ", ".join(nodes) if nodes else "UNKNOWN"
            lines.append(f"1. `{fname}` → {label}（UNVERIFIED）")
    lines += ["", "## 7. 未确认项与待核实项", ""]
    lines.append("1. ☐ 模块一句话职责待人工核实")
    lines.append("1. ☐ reference 侧对应文件/symbol 映射待核实")
    lines.append("1. ☐ 关键 call-edge/state-edge 待逐条对照 reference source")
    lines.append("1. ☐ 本模块 R7/R5/CCR 归属的 UNVERIFIED 状态待升级或降级")
    if report.is_shim:
        lines.append("1. ☐ 占位/小模块：确认是否仅为 shim，不承载 core 语义")
    lines.append("")
    return "\n".join(lines)


def render_index_markdown(reports: list[ModuleReport], ts: str) -> str:
    """渲染 index markdown：7×5×14 总览 + 模块索引。"""
    total_py = sum(len(r.files) for r in reports)
    total_lines = sum(r.total_lines for r in reports)
    lines: list[str] = [
        "# ClaudeRuntime 源码盘点索引（Sourcemap Index）",
        f"> 时间戳: {ts}",
        f"> 基线: {BASELINE_COMMIT}",
        f"> Reference: Claude Code {REFERENCE_VERSION} @ {REFERENCE_COMMIT}",
        f"> 论文: {PAPER}",
        "> 生成器: scripts/sourcemap_generator.py",
        "",
        "## 1. 7×5×14 状态总览",
        "",
        "1. Reference-7: 0/7 COMPLETE — Wave 0 盘点中，全部 UNVERIFIED/UNKNOWN",
        "2. Reference-5: 0/5 COMPLETE — Wave 0 盘点中，全部 UNVERIFIED/UNKNOWN",
        "3. CCR-14: 0/14 COMPLETE — Wave 0 盘点中，全部 UNVERIFIED/UNKNOWN",
        "4. 完成状态词: EXACT / SEMANTIC_EQUIVALENT / PYTHON_ADAPTATION_VERIFIED",
        "5. 未完成状态词: PARTIAL / UNKNOWN / MISSING",
        "",
        "## 2. 模块索引",
        "",
    ]
    for r in reports:
        fname = f"{r.spec.index:02d}-{r.spec.name}-{ts}.html"
        lines.append(
            f"1. {r.spec.index:02d} {r.spec.name} — {len(r.files)} 文件 "
            f"{r.total_lines} 行 — [{fname}](../{fname})"
        )
    lines += [
        "",
        "## 3. 统计",
        "",
        f"1. 模块总数: {len(reports)}",
        f"2. Python 文件总数: {total_py}",
        f"3. 源码总行数: {total_lines}",
        f"4. 命名规则: NN-模块名-YYYYMMDD_HHMM.html（编号按字母序固定，时间戳标识盘点快照）",
        "",
        "## 4. 未确认项",
        "",
        "1. ☐ 全部模块的 R7/R5/CCR 映射均为启发式初版，状态 UNVERIFIED",
        "2. ☐ reference 侧（restored-src）模块级 source map 尚未生成",
        "3. ☐ 旧 AUX lifecycle obligations → R7/R5/CCR 映射尚未登记",
        "4. ☐ 模块一句话职责全部 UNKNOWN，待人工核实",
        "",
    ]
    return "\n".join(lines)


def convert_md_to_html(md_path: Path, html_path: Path) -> None:
    """调用 md2html_sidebar.py 将 markdown 转为自包含 HTML。"""
    if not MD2HTML_SCRIPT.exists():
        raise FileNotFoundError(f"md2html script missing: {MD2HTML_SCRIPT}")
    cmd = [sys.executable, str(MD2HTML_SCRIPT), str(md_path), str(html_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(
            f"md2html failed for {md_path.name}: {proc.stderr[-2000:]}"
        )


def generate(
    src_root: Path,
    out_root: Path,
    ts: str | None = None,
    only: list[str] | None = None,
    convert: bool = True,
) -> list[Path]:
    """执行一次完整盘点快照，返回生成的 HTML 文件列表。"""
    ts = ts or datetime.now().strftime("%Y%m%d_%H%M")
    src_root = src_root.resolve()
    out_root = out_root.resolve()
    md_dir = out_root / "markdown"
    md_dir.mkdir(parents=True, exist_ok=True)

    specs = discover_modules(src_root)
    if only:
        specs = [s for s in specs if s.name in only]
    reports = [scan_module(s, src_root) for s in specs]

    html_files: list[Path] = []
    for report in reports:
        md = render_markdown(report, ts)
        md_path = md_dir / f"{report.spec.index:02d}-{report.spec.name}-{ts}.md"
        html_path = out_root / f"{report.spec.index:02d}-{report.spec.name}-{ts}.html"
        md_path.write_text(md, encoding="utf-8")
        if convert:
            convert_md_to_html(md_path, html_path)
            html_files.append(html_path)

    index_md = render_index_markdown(reports, ts)
    index_md_path = md_dir / f"index-{ts}.md"
    index_md_path.write_text(index_md, encoding="utf-8")
    index_html = out_root / "index.html"
    if convert:
        convert_md_to_html(index_md_path, index_html)
        html_files.append(index_html)
    return html_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", default=str(REPO_ROOT / "src"))
    parser.add_argument("--out", default=str(REPO_ROOT / "docs" / "sourcemap"))
    parser.add_argument("--ref-src", default=None,
                        help="reference 源码根（restored-src/src），设置后生成 reference 侧盘点")
    parser.add_argument("--ref-out", default=None,
                        help="reference 盘点输出目录（默认 <out>/reference）")
    parser.add_argument("--ts", default=None, help="YYYYMMDD_HHMM override")
    parser.add_argument("--only", default=None, help="comma-separated module names")
    args = parser.parse_args(argv)
    only = [m.strip() for m in args.only.split(",")] if args.only else None
    html_files: list[Path] = []
    if args.ref_src:
        ref_out = Path(args.ref_out) if args.ref_out else (
            Path(args.out) / "reference"
        )
        html_files = generate_reference(
            Path(args.ref_src), ref_out, ts=args.ts, only=only
        )
    else:
        html_files = generate(
            Path(args.src), Path(args.out), ts=args.ts, only=only
        )
    for f in html_files:
        print(f"generated: {f}")
    print(f"total: {len(html_files)} html files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
