"""检查仓库文档目录、链接、证据结构和唯一分类规则。

脚本只依赖 Python 标准库，确保 CI 在安装可选依赖前也能执行治理门禁。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path


ROOT_MARKDOWN_ALLOWLIST = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
}

DOCS_TOP_LEVEL_ALLOWLIST = {
    "20260811_2238_clauderuntime_source_aligned_7x5x14_delivery_B3",
    "20260813_0140_clauderuntime_B4_core_closure_delivery",
    "20260813_0843_clauderuntime_B5_source_aligned_final_closure_delivery",
    "20260813_1824_B4修复反馈建议_v2_交付包",
    "20260814_0817_clauderuntime_B6_hierarchical_alignment_delivery_v1.1",
    "README.md",
    "architecture",
    "archive",
    "assets",
    "guides",
    "history",
    "i18n",
    "parity",
    "plans",
    "progress",
    "reference",
    "reference-differences",
    "status",
    "sourcemap",
}

DATE_DOC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-.+\.(?:md|html)$")
TODO_FEATURE_RE = re.compile(r"(?:^|[-_])(TODO|TODOS|FEATURE|FEATURES)(?:[-_.]|$)", re.I)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

EXPECTED_COMPONENT_NAMES = {
    "User",
    "Interfaces",
    "Agent Loop",
    "Permission System",
    "Tools",
    "State & Persistence",
    "Execution Environment",
}
EXPECTED_LAYER_IDS = {f"R5-{n:02d}" for n in range(1, 6)}
EXPECTED_CCR_IDS = {f"CCR-{n:02d}" for n in range(1, 15)}
EXPECTED_AUX_IDS = {f"AUX-{n:02d}" for n in range(1, 15)}
EXPECTED_RUNTIME_PATH_IDS = {f"RP-{n:02d}" for n in range(1, 13)}

ALLOWED_PARITY_STATUSES = {
    "EXACT",
    "SEMANTIC_EQUIVALENT",
    "PYTHON_ADAPTATION",
    "PRODUCT_EXTENSION",
    "INTENTIONAL_DIVERGENCE",
    "PARTIAL",
    "MISSING",
    "UNKNOWN",
    "DONE",
    "BLOCKED",
    "VERIFIED",
}

B6_CERTAINTY_VOCABULARY = {
    "R1_CONFIRMED",
    "R2_PARTIALLY_CONFIRMED",
    "R3_UNKNOWN",
    "R4_PRODUCT_EXTENSION",
}

B6_ALIGNMENT_POLICY_VOCABULARY = {
    "MUST_ALIGN",
    "ALIGN_KNOWN_PART",
    "FUNCTIONAL_CORE_ONLY",
    "PRODUCT_EXTENSION",
}

B6_STATUS_VOCABULARY = {
    "FUNCTIONAL_COMPLETE",
    "FUNCTIONAL_ADAPTATION",
    "LIMITED",
    "DEFERRED_REFERENCE_DETAIL",
    "UNKNOWN_REFERENCE",
    "MISSING",
}

B6_REASON_VOCABULARY = {
    "PYTHON_RUNTIME_ADAPTATION",
    "PYTHON_ECOSYSTEM_ADAPTATION",
    "OS_PLATFORM_ADAPTATION",
    "RECOVERED_SOURCE_GAP",
    "PRODUCT_SCOPE_SIMPLIFICATION",
    "SAFETY_STRENGTHENING",
    "MAINTAINABILITY_SIMPLIFICATION",
    "PERFORMANCE_OPTIMIZATION",
    "LEGACY_COMPATIBILITY",
    "DEFERRED_REFERENCE_DETAIL",
    "UNKNOWN",
}

B6_IMPACT_VOCABULARY = {"NONE", "LOW", "MEDIUM", "HIGH"}

REFERENCE_DIFFERENCES_REGISTRY = "docs/reference-differences/registry.yaml"

REFERENCE_DIFFERENCES_REQUIRED_TOKENS = {
    "schema_version:",
    "purpose:",
    "strategy:",
    "items:",
    "id:",
    "area:",
    "feature:",
    "reference_certainty:",
    "alignment_policy:",
    "reference:",
    "python:",
    "difference:",
    "reason:",
    "user_impact:",
    "safety_impact:",
    "compatibility_impact:",
    "status:",
    "accepted:",
}

PARITY_SCHEMA_REQUIRED_TOKENS = {
    "docs/parity/source-map/reference-component-map.yaml": {
        "schema_version:",
        "reference_target:",
        "subject_commit:",
        "components:",
        "id:",
        "name:",
        "status:",
        "primary_paths:",
        "tests:",
    },
    "docs/parity/source-map/reference-package-map.yaml": {
        "schema_version:",
        "reference_target:",
        "packages:",
        "id:",
        "reference:",
        "clauderuntime:",
        "status:",
    },
    "docs/parity/source-map/reference-symbol-map.yaml": {
        "schema_version:",
        "reference_target:",
        "symbols:",
        "id:",
        "reference:",
        "clauderuntime:",
        "status:",
        "criticality:",
    },
    "docs/parity/runtime/reference-aux-loop-map.yaml": {
        "schema_version:",
        "reference_target:",
        "auxiliary_mechanisms:",
        "id:",
        "name:",
        "primary_component:",
        "secondary_component:",
        "status:",
        "runtime_paths:",
        "tests:",
    },
    "docs/parity/runtime/reference-runtime-path-map.yaml": {
        "schema_version:",
        "reference_target:",
        "runtime_paths:",
        "id:",
        "name:",
        "status:",
        "python_entry:",
        "tests:",
    },
}


def repo_files(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
    )
    paths: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        path = repo / raw.decode("utf-8", errors="surrogateescape")
        if path.exists() and path.is_file():
            paths.append(path.relative_to(repo))
    return sorted(paths)


def read_allowlist(path: Path) -> set[str]:
    if not path.exists():
        return set()
    allowed: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            allowed.add(line)
    return allowed


def is_external_link(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(
        (
            "http://",
            "https://",
            "mailto:",
            "tel:",
            "ftp://",
            "data:",
            "javascript:",
        )
    )


def split_markdown_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    elif re.search(r'\s+"[^"]*"\s*$', target):
        target = re.sub(r'\s+"[^"]*"\s*$', "", target)
    elif re.search(r"\s+'[^']*'\s*$", target):
        target = re.sub(r"\s+'[^']*'\s*$", "", target)
    return urllib.parse.unquote(target.strip())


def local_link_exists(repo: Path, source: Path, target: str) -> bool:
    target = split_markdown_target(target)
    if not target or target.startswith("#") or is_external_link(target):
        return True

    path_part = target.split("#", 1)[0].split("?", 1)[0]
    if not path_part:
        return True

    candidate = repo / path_part.lstrip("/") if path_part.startswith("/") else repo / source.parent / path_part
    return candidate.exists()


def check_markdown_links(repo: Path, files: list[Path], allowlist: set[str]) -> list[str]:
    failures: list[str] = []
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        text = (repo / path).read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in MARKDOWN_LINK_RE.finditer(line):
                target = match.group(1)
                if local_link_exists(repo, path, target):
                    continue
                record = f"{path}:{lineno} -> {split_markdown_target(target)}"
                if record not in allowlist:
                    failures.append(record)
    return failures


def is_archive_link(target: str) -> bool:
    target = split_markdown_target(target)
    path_part = target.split("#", 1)[0].split("?", 1)[0]
    normalized = path_part.replace("\\", "/").lstrip("/")
    return normalized == "archive" or normalized.startswith("archive/") or "/archive/" in normalized


def archive_policy_exempt(path: Path) -> bool:
    parts = path.parts
    if path == Path("docs/README.md"):
        return True
    return len(parts) >= 2 and parts[0] == "docs" and parts[1] in {
        "archive",
        "history",
        "progress",
    }


def check_archive_link_policy(files: list[Path], repo: Path) -> list[str]:
    failures: list[str] = []
    for path in files:
        if path.suffix.lower() != ".md" or archive_policy_exempt(path):
            continue
        text = (repo / path).read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in MARKDOWN_LINK_RE.finditer(line):
                target = match.group(1)
                if is_archive_link(target):
                    failures.append(f"current doc links to archive fact source: {path}:{lineno} -> {split_markdown_target(target)}")
    return failures


def check_structure(files: list[Path]) -> list[str]:
    failures: list[str] = []
    root_markdown = {path.name for path in files if len(path.parts) == 1 and path.suffix == ".md"}
    for name in sorted(root_markdown - ROOT_MARKDOWN_ALLOWLIST):
        failures.append(f"root markdown is not allowlisted: {name}")
    for name in sorted(root_markdown):
        if TODO_FEATURE_RE.search(name):
            failures.append(f"root TODO/FEATURE markdown is forbidden: {name}")

    docs_entries = {path.parts[1] for path in files if len(path.parts) >= 2 and path.parts[0] == "docs"}
    for name in sorted(docs_entries - DOCS_TOP_LEVEL_ALLOWLIST):
        failures.append(f"docs top-level entry is not allowlisted: docs/{name}")
    for name in sorted(docs_entries):
        if DATE_DOC_RE.match(name):
            failures.append(f"dated docs must not live directly under docs/: docs/{name}")
    return failures


def check_expected_tokens(repo: Path, relpath: str, expected: set[str], label: str) -> list[str]:
    path = repo / relpath
    if not path.exists():
        return [f"missing {label} map: {relpath}"]
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = sorted(token for token in expected if token not in text)
    return [f"{label} missing {token} in {relpath}" for token in missing]


def extract_yaml_ids(text: str) -> list[str]:
    return re.findall(r"^\s+- id:\s+([A-Za-z0-9_.:-]+)\s*$", text, flags=re.MULTILINE)


def check_yaml_id_set(repo: Path, relpath: str, expected: set[str], label: str) -> list[str]:
    path = repo / relpath
    if not path.exists():
        return [f"missing {label}: {relpath}"]
    ids = extract_yaml_ids(path.read_text(encoding="utf-8", errors="replace"))
    actual = set(ids)
    failures: list[str] = []
    for item_id in sorted(expected - actual):
        failures.append(f"{label} missing id {item_id} in {relpath}")
    for item_id in sorted(actual - expected):
        failures.append(f"{label} has unexpected id {item_id} in {relpath}")
    for item_id in sorted({item_id for item_id in ids if ids.count(item_id) > 1}):
        failures.append(f"{label} has duplicate id {item_id} in {relpath}")
    return failures


def check_parity_schema(repo: Path) -> list[str]:
    failures: list[str] = []
    status_re = re.compile(r"^\s+status:\s+([A-Z_]+)\s*$", flags=re.MULTILINE)
    for relpath, required_tokens in PARITY_SCHEMA_REQUIRED_TOKENS.items():
        path = repo / relpath
        if not path.exists():
            failures.append(f"missing parity schema file: {relpath}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in sorted(required_tokens):
            if token not in text:
                failures.append(f"parity schema missing token {token} in {relpath}")
        for status in status_re.findall(text):
            if status not in ALLOWED_PARITY_STATUSES:
                failures.append(f"parity schema has unknown status {status} in {relpath}")
    return failures


def check_parity_maps(repo: Path) -> list[str]:
    failures: list[str] = []
    failures.extend(check_parity_schema(repo))
    failures.extend(
        check_expected_tokens(
            repo,
            "docs/parity/source-map/reference-component-map.yaml",
            EXPECTED_COMPONENT_NAMES,
            "Reference-7 component map",
        )
    )
    failures.extend(
        check_expected_tokens(
            repo,
            "docs/parity/README.md",
            EXPECTED_LAYER_IDS,
            "Reference-5 layer index",
        )
    )
    failures.extend(
        check_expected_tokens(
            repo,
            "docs/parity/coverage-ledger.yaml",
            EXPECTED_CCR_IDS,
            "CCR-14 index",
        )
    )
    failures.extend(
        check_expected_tokens(
            repo,
            "docs/parity/runtime/reference-aux-loop-map.yaml",
            EXPECTED_AUX_IDS,
            "AUX map",
        )
    )
    failures.extend(
        check_expected_tokens(
            repo,
            "docs/parity/runtime/reference-runtime-path-map.yaml",
            EXPECTED_RUNTIME_PATH_IDS,
            "Runtime path map",
        )
    )
    failures.extend(
        check_yaml_id_set(
            repo,
            "docs/parity/runtime/reference-aux-loop-map.yaml",
            EXPECTED_AUX_IDS,
            "AUX map",
        )
    )
    failures.extend(
        check_yaml_id_set(
            repo,
            "docs/parity/runtime/reference-runtime-path-map.yaml",
            EXPECTED_RUNTIME_PATH_IDS,
            "Runtime path map",
        )
    )
    return failures


def collect_parity_unknowns(repo: Path) -> list[str]:
    records: list[str] = []
    parity_root = repo / "docs" / "parity"
    for path in sorted(parity_root.rglob("*.yaml")):
        relpath = path.relative_to(repo)
        current_id = "GLOBAL"
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            id_match = re.match(r"^\s+- id:\s+(.+?)\s*$", line)
            if id_match:
                current_id = id_match.group(1)
            if "UNKNOWN" in line:
                records.append(f"{relpath} -> {current_id} -> {line.strip()}")
    return records


def check_parity_unknowns(repo: Path, allowlist: set[str]) -> list[str]:
    return [
        f"unallowlisted parity UNKNOWN: {record}"
        for record in collect_parity_unknowns(repo)
        if record not in allowlist
    ]


def check_reference_differences(repo: Path) -> list[str]:
    """Validate the B6 difference registry schema and controlled vocabulary.

    The registry is the global ledger for Reference vs Python differences. It
    must exist, carry the required fields, use only the B6 vocabulary for
    certainty / alignment policy / status / reason / impact, and keep item ids
    unique. Mirroring the parity maps, a regex-based scan keeps the gate
    stdlib-only.
    """
    failures: list[str] = []
    path = repo / REFERENCE_DIFFERENCES_REGISTRY
    if not path.exists():
        return [f"missing reference differences registry: {REFERENCE_DIFFERENCES_REGISTRY}"]
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in sorted(REFERENCE_DIFFERENCES_REQUIRED_TOKENS):
        if token not in text:
            failures.append(
                f"reference differences registry missing token {token} in {REFERENCE_DIFFERENCES_REGISTRY}"
            )

    def _check_vocabulary(pattern: str, vocabulary: set[str], label: str) -> None:
        for value in re.findall(pattern, text):
            if value not in vocabulary:
                failures.append(
                    f"reference differences registry has unknown {label} {value!r} in {REFERENCE_DIFFERENCES_REGISTRY}"
                )

    _check_vocabulary(
        r"^\s+reference_certainty:\s+([A-Z0-9_]+)\s*$",
        B6_CERTAINTY_VOCABULARY,
        "reference_certainty",
    )
    _check_vocabulary(
        r"^\s+alignment_policy:\s+([A-Z0-9_]+)\s*$",
        B6_ALIGNMENT_POLICY_VOCABULARY,
        "alignment_policy",
    )
    _check_vocabulary(
        r"^\s+status:\s+([A-Z_]+)\s*$",
        B6_STATUS_VOCABULARY,
        "status",
    )
    _check_vocabulary(
        r"^\s+reason:\s+([A-Z_]+)\s*$",
        B6_REASON_VOCABULARY,
        "reason",
    )
    for impact_label in ("user_impact", "safety_impact", "compatibility_impact"):
        _check_vocabulary(
            rf"^\s+{impact_label}:\s+([A-Z]+)\s*$",
            B6_IMPACT_VOCABULARY,
            impact_label,
        )

    ids = extract_yaml_ids(text)
    for item_id in sorted({item_id for item_id in ids if ids.count(item_id) > 1}):
        failures.append(
            f"reference differences registry has duplicate id {item_id} in {REFERENCE_DIFFERENCES_REGISTRY}"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allowlist",
        default="docs/status/markdown-link-allowlist.txt",
        help="Known broken Markdown links that predate this governance gate.",
    )
    parser.add_argument(
        "--parity-unknown-allowlist",
        default="docs/status/parity-unknown-allowlist.txt",
        help="Known parity UNKNOWN records that must be resolved over time.",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    files = repo_files(repo)
    failures = check_structure(files)
    failures.extend(check_parity_maps(repo))
    failures.extend(check_reference_differences(repo))
    failures.extend(check_markdown_links(repo, files, read_allowlist(repo / args.allowlist)))
    failures.extend(check_archive_link_policy(files, repo))
    failures.extend(
        check_parity_unknowns(repo, read_allowlist(repo / args.parity_unknown_allowlist))
    )

    if failures:
        print("Documentation governance check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Documentation governance check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
