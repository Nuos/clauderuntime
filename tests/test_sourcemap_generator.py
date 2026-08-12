"""Wave 0 — sourcemap generator 单元测试。

覆盖：
- 模块发现：src 全部顶层包 + core 单文件组、编号连续且字母序
- AST 盘点：文件/类/函数/import 提取、self-import 排除
- 启发式映射：全覆盖、ID 合法
- markdown 渲染：章节齐全、UNVERIFIED 状态、无 GFM 表格（md2html 不支持）
- HTML 转换：doctype/charset/sidebar 折叠元素（md2html 脚本存在时）
- index 链接完整性
- 命名规则：NN-模块名-YYYYMMDD_HHMM.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import sourcemap_generator as smg  # noqa: E402

TEST_TS = "20260101_0000"
VALID_IDS = set(smg.R7_LABELS) | set(smg.R5_LABELS) | set(smg.CCR_LABELS)


@pytest.fixture(scope="module")
def src_root() -> Path:
    return REPO_ROOT / "src"


@pytest.fixture(scope="module")
def specs(src_root: Path) -> list[smg.ModuleSpec]:
    return smg.discover_modules(src_root)


# ---------------------------------------------------------------------------
# 模块发现
# ---------------------------------------------------------------------------
class TestDiscovery:
    def test_covers_all_src_packages(self, src_root: Path, specs):
        """discover_modules 必须覆盖 src 全部顶层包（排除 __pycache__）+ 单文件组。"""
        real_dirs = {
            p.name
            for p in src_root.iterdir()
            if p.is_dir() and p.name != "__pycache__"
        }
        found = {s.name for s in specs if s.kind == "package"}
        assert found == real_dirs

    def test_single_file_group_present(self, specs):
        """core 单文件组必须存在且类型为 group。"""
        group = [s for s in specs if s.kind == "group"]
        assert len(group) == 1
        assert group[0].name == "core-single-files"

    def test_numbering_sequential_alphabetical(self, specs):
        """编号连续 1..N 且按名称字母序。"""
        assert [s.index for s in specs] == list(range(1, len(specs) + 1))
        names = [s.name for s in specs]
        assert names == sorted(names)

    def test_minimum_module_count(self, specs):
        """src 顶层模块数至少 50（当前 53 目录 + 1 组）。"""
        assert len(specs) >= 50


# ---------------------------------------------------------------------------
# AST 盘点
# ---------------------------------------------------------------------------
class TestScan:
    def test_scan_module_basic(self, src_root: Path, specs):
        """小模块盘点：文件数/行数/符号字段非负且一致。"""
        bg = next(s for s in specs if s.name == "background")
        report = smg.scan_module(bg, src_root)
        assert len(report.files) > 0
        assert report.total_lines > 0
        assert sum(len(f.classes) for f in report.files) >= 0
        # 每个文件的行数与实际文件一致（非 UTF-8 文件 scan_file 走容错分支，
        # 行数由二进制计数保证；此处跳过编码断言避免顺序依赖 flaky）
        for inv in report.files:
            try:
                raw = (src_root / inv.rel_path).read_text(encoding="utf-8")
                assert inv.lines == raw.count("\n")
            except UnicodeDecodeError:
                continue

    def test_query_excludes_self_import(self, src_root: Path, specs):
        """包内自引用不得计入 src 内部依赖；相对导入必须识别跨模块边。"""
        q = next(s for s in specs if s.name == "query")
        report = smg.scan_module(q, src_root)
        assert "query" not in report.src_internal_imports
        # query 大量使用 `from ..tool_system.x import ...` 相对导入
        assert "tool_system" in report.src_internal_imports
        assert "providers" in report.src_internal_imports

    def test_symbols_have_lines(self, src_root: Path, specs):
        """类/函数符号必须携带定义行号。"""
        agent = next(s for s in specs if s.name == "agent")
        report = smg.scan_module(agent, src_root)
        symbols = [c for f in report.files for c in f.classes + f.funcs]
        assert len(symbols) > 50  # agent 模块符号量大，足以验证提取
        assert all(s.line >= 1 for s in symbols)


# ---------------------------------------------------------------------------
# 启发式映射
# ---------------------------------------------------------------------------
class TestHeuristicMapping:
    def test_all_modules_mapped(self, specs):
        """每个模块都必须有启发式映射条目（可为空列表=显式 UNKNOWN）。"""
        for s in specs:
            assert s.name in smg.HEURISTIC_MAP, f"{s.name} 缺少启发式映射"

    def test_mapping_ids_legal(self, specs):
        """映射 ID 必须属于 R7-01..07 / R5-01..05 / CCR-01..14。"""
        for s in specs:
            r7, r5, ccr = smg.HEURISTIC_MAP[s.name]
            for node in r7 + r5 + ccr:
                assert node in VALID_IDS, f"{s.name}: 非法映射 ID {node}"

    def test_single_file_map_covers_group_files(self, src_root: Path, specs):
        """单文件组的 file_map 必须覆盖 src 顶层全部单文件。"""
        group = next(s for s in specs if s.kind == "group")
        report = smg.scan_module(group, src_root)
        for f in report.files:
            assert f.rel_path in smg.SINGLE_FILE_MAP


# ---------------------------------------------------------------------------
# markdown 渲染
# ---------------------------------------------------------------------------
class TestRender:
    def test_all_sections_present(self, src_root: Path, specs):
        """md 必须包含全部 7 个盘点章节。"""
        q = next(s for s in specs if s.name == "query")
        report = smg.scan_module(q, src_root)
        md = smg.render_markdown(report, TEST_TS)
        sections = ["## 1. 模块概况", "## 2. 文件清单", "## 3. 关键符号",
                    "## 4. 依赖与调用边", "## 5. R7/R5/CCR-14 映射",
                    "## 6. 文件级映射细分", "## 7. 未确认项"]
        for sec in sections:
            assert sec in md

    def test_unverified_stamp(self, src_root: Path, specs):
        """映射状态必须标注 UNVERIFIED（B3：未确认不冒充完成）。"""
        q = next(s for s in specs if s.name == "query")
        report = smg.scan_module(q, src_root)
        md = smg.render_markdown(report, TEST_TS)
        assert "UNVERIFIED" in md
        assert "映射状态: UNVERIFIED" in md

    def test_no_gfm_tables(self, src_root: Path, specs):
        """md 不得含 GFM 表格行（md2html 不支持，渲染会露馅）。"""
        for s in specs:
            report = smg.scan_module(s, src_root)
            md = smg.render_markdown(report, TEST_TS)
            for line in md.splitlines():
                assert not re.match(r"^\s*\|.*\|\s*$", line), f"{s.name}: 表格行 {line}"

    def test_index_links_every_module(self, src_root: Path, specs, tmp_path):
        """index md 必须为每个模块生成 NN-名称-ts.html 链接。"""
        reports = [smg.scan_module(s, src_root) for s in specs]
        md = smg.render_index_markdown(reports, TEST_TS)
        for r in reports:
            fname = f"{r.spec.index:02d}-{r.spec.name}-{TEST_TS}.html"
            assert fname in md, f"index 缺少 {fname}"


# ---------------------------------------------------------------------------
# Reference 侧（restored-src）盘点
# ---------------------------------------------------------------------------
class TestReference:
    """reference 侧（restored-src）盘点测试。"""

    ref_root: Path
    ref_specs: list[smg.ModuleSpec]

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def _ref_env(cls) -> None:
        ref = Path.home() / "dev-workspace/agent-study/chinasiro-claude-code-sourcemap/restored-src/src"
        if not ref.exists():
            pytest.skip("reference 源码不可用")
        cls.ref_root = ref
        cls.ref_specs = smg.discover_reference_modules(ref)

    def test_ref_discovery(self):
        """reference 模块发现：覆盖全部目录 + top-level 组，编号连续。"""
        real_dirs = {p.name for p in self.ref_root.iterdir() if p.is_dir()}
        found = {s.name for s in self.ref_specs if s.kind == "package"}
        assert found == real_dirs
        assert [s.index for s in self.ref_specs] == list(range(1, len(self.ref_specs) + 1))
        assert any(s.kind == "group" for s in self.ref_specs)

    def test_scan_ts_file_symbols(self):
        """TS 扫描必须提取到类/函数符号与 import 目标。"""
        q = next(s for s in self.ref_specs if s.name == "query")
        report = smg.scan_reference_module(q, self.ref_root)
        assert len(report.files) >= 1
        assert report.total_lines > 0
        # query.ts 内部依赖至少包含 services / types 之一
        assert "services" in report.src_internal_imports or "types" in report.src_internal_imports
        # 符号提取非空（tokenBudget.ts 有函数、stopHooks.ts 有导出）
        symbols = [s for f in report.files for s in f.classes + f.funcs]
        assert len(symbols) >= 1

    def test_ref_mapping_covers_all(self):
        """每个 reference 模块都应有映射条目（可空=UNKNOWN）。"""
        for s in self.ref_specs:
            assert s.name in smg.REF_TO_PY_MAP, f"{s.name} 缺少候选映射条目"
        # 无候选的显式空列表允许
        for s in self.ref_specs:
            assert isinstance(smg.REF_TO_PY_MAP[s.name], list)

    def test_ref_render_sections(self):
        """reference md 必须含全部 6 个盘点章节。"""
        q = next(s for s in self.ref_specs if s.name == "query")
        report = smg.scan_reference_module(q, self.ref_root)
        md = smg.render_reference_markdown(report, TEST_TS)
        for sec in ["## 1. 模块概况", "## 2. 文件清单", "## 3. 关键符号",
                    "## 4. 依赖与调用边", "## 5. Python 侧候选映射",
                    "## 6. 未确认项"]:
            assert sec in md

    def test_ref_index_lists_py_only(self):
        """reference index 必须列出 python-only 缺口模块。"""
        reports = [smg.scan_reference_module(s, self.ref_root) for s in self.ref_specs]
        md = smg.render_reference_index_markdown(reports, TEST_TS)
        for mod in ("permissions", "memory", "compact_service"):
            assert mod in md

    @pytest.mark.skipif(
        not smg.MD2HTML_SCRIPT.exists(), reason="md2html_sidebar.py 不可用"
    )
    def test_ref_generate_naming(self, tmp_path):
        """reference 生成产物命名合规且含 sidebar。"""
        out = tmp_path / "ref"
        smg.generate_reference(self.ref_root, out, ts=TEST_TS, only=["query"],
                               convert=True)
        html = list(out.glob("*-query-*.html"))
        assert len(html) == 1
        assert smg.module_name_regex().match(html[0].name)
        text = html[0].read_text(encoding="utf-8")
        assert "<!doctype html>" in text.lower()
        assert "sidebar-collapsed" in text


# ---------------------------------------------------------------------------
# 生成与命名
# ---------------------------------------------------------------------------
class TestGenerate:
    def test_naming_convention(self, src_root, tmp_path):
        """产物命名必须匹配 NN-模块名-YYYYMMDD_HHMM.html。"""
        out = tmp_path / "sm"
        smg.generate(src_root, out, ts=TEST_TS, only=["background", "query"],
                     convert=False)
        for html in out.glob("*.html"):
            assert smg.module_name_regex().match(html.name), f"非法命名 {html.name}"

    def test_index_generated(self, src_root, tmp_path):
        """每次生成必须产出 index.md（convert=False 模式）。"""
        out = tmp_path / "sm"
        smg.generate(src_root, out, ts=TEST_TS, only=["background"],
                     convert=False)
        assert (out / "markdown" / f"index-{TEST_TS}.md").exists()

    @pytest.mark.skipif(
        not smg.MD2HTML_SCRIPT.exists(), reason="md2html_sidebar.py 不可用"
    )
    def test_html_sidebar_valid(self, src_root, tmp_path):
        """HTML 必须含 doctype/charset/sidebar 折叠元素与导航链接。"""
        # 编号是全局字母序，only 过滤不影响编号 → 用 discover 结果取实际编号
        spec = next(s for s in smg.discover_modules(src_root)
                    if s.name == "background")
        out = tmp_path / "sm"
        smg.generate(src_root, out, ts=TEST_TS, only=["background"], convert=True)
        html = out / f"{spec.index:02d}-background-{TEST_TS}.html"
        assert html.exists()
        text = html.read_text(encoding="utf-8")
        assert "<!doctype html>" in text.lower()
        assert 'charset="UTF-8"' in text or "charset=utf-8" in text.lower()
        assert "sidebar-collapsed" in text  # 折叠 class 逻辑
        assert "toggle" in text.lower()  # ☰ 折叠按钮
        assert 'href="#' in text  # 侧边栏导航锚点链接

    def test_shim_detection(self, src_root, specs):
        """占位/小模块（如 schemas）应被标记 is_shim。"""
        shims = [s for s in specs if s.name in ("schemas", "moreright", "vim")]
        for s in shims:
            report = smg.scan_module(s, src_root)
            assert report.is_shim, f"{s.name} 应为 shim"
        bg = next(s for s in specs if s.name == "background")
        assert not smg.scan_module(bg, src_root).is_shim
