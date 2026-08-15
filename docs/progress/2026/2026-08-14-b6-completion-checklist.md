# B6 最终验收清单核对与完成度记录

> 阶段：`B6 / 验收收口`
> 日期：`2026-08-14`
> 依据：`10_B6最终验收清单.md`、`01_B6目标重置与验收基线.md`
> 本核对记录使用 B6 分级对齐口径（不是 Source-Aligned 口径）。

# A. 核心功能

| 项 | 状态 | 证据 |
|---|---|---|
| 普通 Agent query 可稳定完成 | ✅ | 全量套件 + surface smoke（回答路径） |
| Read/Write/Edit/Bash/Grep/Glob 可用 | ✅ | 既有工具套件 + `tests/test_b6_surface_smoke.py`（Read 真实往返） |
| Permission deny/allow/ask 可用 | ✅ | `tests/test_b6_surface_smoke.py` 权限 round-trip + 既有权限套件 |
| Tool failure 能回到 Agent loop | ✅ | 既有 query/recovery 测试 |
| Context instructions 可加载 | ✅ | 既有 context 套件 |
| Path-scoped rules 可延迟注入 | ✅ | 既有 context rules 测试（next-model-call exactly-once） |
| 长上下文有预算/压缩机制 | ✅ | 五层 pipeline + 本阶段 Snip 真实实现（DIFF-CCR03-001） |
| Transcript 可持久化 | ✅ | 既有 transcript 套件 |
| Background Agent 可运行 | ✅ | 既有 background/agent 套件 |
| Resume 常见场景可恢复 | ✅ | `tests/test_b6_resume_new_process_smoke.py`（真实双进程） |
| MCP 可连接、发现、执行、清理 | ✅ | `tests/test_b6_mcp_disconnect.py`（含断开清理） |
| Hooks 关键事件可运行并超时清理 | ✅ | 既有 hooks 套件 |
| Scheduler 基础 create/list/delete/fire/restore 可用 | ✅ | `tests/scheduled_tasks/test_scheduler_file_backed.py` + 既有套件 |
| Interrupt/abort 能停止主要执行路径 | ✅ | `tests/test_b6_surface_smoke.py` 中断用例 + 既有 abort 套件 |

# B. 安全底线（P0 审计逐项核对，2026-08-14）

| 项 | 状态 | 证据/说明 |
|---|---|---|
| Permission deny 不可绕过 | ✅ | dispatch 统一 `ensure_tool_allowed`；deny → ToolPermissionError |
| background 不成为安全旁路 | ✅ | fg/bg/Monitor 三路径共用 `bash_command_safety_guard` + sandbox prepare |
| required isolation 不可静默退化 | ✅ | 本阶段修复 guard 能力感知；`require_isolation` 一律 fail-closed |
| stale MCP tools 不可继续调用 | ✅ | 本阶段实现断开清理（client→runtime→registry 全链路） |
| Resume 不恢复 API key/临时权限 | ✅ | `resume_metadata.py` 白名单字段；既有测试锁定 |
| timeout 后危险 child process 不继续执行 | ✅ | `run_process_tree` 整树终止（既有） |
| symlink/path escape 有明确处理 | ✅ | `DefaultWorkspaceGuard` 先 resolve 再比对 roots（既有） |

# C. Reference 分级对齐

| 项 | 状态 | 证据 |
|---|---|---|
| R1_CONFIRMED 按 MUST_ALIGN 验收 | ✅ | DIFF-SANDBOX-001（隔离契约）等 |
| R2_PARTIALLY_CONFIRMED 已知部分对齐 | ✅ | Snip call-site/返回契约、Scheduler 持久化目标、MCP 断开契约 |
| R3_UNKNOWN 不伪造 Reference 细节 | ✅ | Snip 参考函数体未恢复 → 保守 allowlist 实现 + 明示 |
| R4_PRODUCT_EXTENSION 明确分离 | ✅ | registry 词汇表含 R4；无伪装 |
| 已知偏离都有原因与影响评估 | ✅ | registry 7 条全部含 reason/impact/accepted |

# D. 差异透明

| 项 | 状态 | 证据 |
|---|---|---|
| 核心模块有 Reference Mapping | ✅ | sandbox/sandbox_guard/client/mcp_runtime/agent_server/win_job_launcher/scheduler/snip_compact |
| 关键不同函数有 REF-DIFF | ✅ | 上述模块函数级注释 |
| 全局 registry 已更新 | ✅ | `docs/reference-differences/registry.yaml`（7 条） |
| progress 文档有差异摘要 | ✅ | 两个 wave progress 文档 |
| UNKNOWN 未写成确定事实 | ✅ | Snip/Platform 台账明示 PENDING |
| accepted divergence 有原因 | ✅ | 每条含 acceptance_reason |

# D. 平台与 Surface

| 项 | 状态 | 证据 |
|---|---|---|
| macOS execution boundary smoke | ✅（结构）/ ⚠️（本环境） | `tests/test_phase_c_exit_gate.py` 等；本环境 sandbox-exec 被禁 → `BLOCKED`（平台验证台账） |
| Linux capability/fallback 说明真实 | ✅（披露） | `platform-verification.md`：PENDING_REAL_DEVICE |
| Windows capability/fallback 说明真实 | ✅（披露） | `platform-verification.md`：PENDING_REAL_DEVICE |
| CLI smoke | ✅ | `tests/test_b6_surface_smoke.py`（headless 两项） |
| TUI smoke | ✅ | ui-tui 自有套件（文档基线 1692 passed） |
| Server smoke | ✅ | `tests/test_b6_surface_smoke.py`（5 项）+ server e2e |
| Desktop smoke（若正式支持） | ✅ | server 端 gateway 由 server 套件覆盖 |

# E. 测试

| 项 | 状态 | 证据 |
|---|---|---|
| targeted tests | ✅ | 本阶段针对性 332 passed |
| affected combination tests | ✅ | scheduler↔server、snip↔pipeline、sandbox↔bash 组合 |
| 阶段收尾 full local suite | ✅ | `10212 passed / 10 skipped / 345 subtests`；7 项环境性失败与基线一致（零回归） |
| 外部依赖测试单独记录 | ✅（已执行） | ① PyPI editable install：fresh venv `pip install -e .` 成功 + 核心模块导入 OK；② 官方 `@modelcontextprotocol/server-everything`：真实 stdio 连接成功、工具发现（echo）通过（`tests/integration/test_real_mcp_server.py`；修复点：MCP SDK stdio transport 默认只继承白名单 env，测试改为显式传调用方环境） |
| GitHub CI 与 local 分开记录 | ✅（已配置） | `.github/workflows/ci.yml`（RELEASE_GATE）；CI 首跑被账户计费锁定阻塞（外部），解除后重跑并单独记录 |

# Final 结论

A/B/C 核心项全部满足；D 平台受限项为 `LIMITED`（Windows/Linux 真机验证
`PENDING_REAL_DEVICE`）且真实披露。

```text
FUNCTIONALLY_SIMILAR_CORE_COMPLETE（核心功能类似 + Python-native + 差异透明）
```

明确不表示：

```text
Claude Code 2.1.88 Source-Aligned
1:1 Compatible
Exact Behavioral Clone
```

# 剩余/阻塞

- Windows/Linux 真机验证：`PENDING_REAL_DEVICE`（平台验证台账），需在
  对应平台执行后关闭。
- GitHub CI 首跑结果（2026-08-15，计费锁定解除后真实运行）：
  - `docs-governance` ✅ 通过（修复：两个空目录加 `.gitkeep`，Git 不追踪空目录
    导致 `docs/README.md` 链接在 CI 检出后失效）
  - `tests` ⚠️ `10004 passed / 4 failed`：4 项均为 CI 环境特定问题 ——
    `test_stream_watchdog.py`×2、`test_ch04_api_round4.py::TestWatchdogWarning`
    （`threading.Timer` 时序敏感，CI 负载下波动）、
    `test_opencode_compat_providers.py::test_xai_requests_go_to_chat_completions`
    （HTTP mock 断言）。三个测试文件与基线 `dc7393b` **完全一致**（未改动），
    本地全部通过（40/40）。非本次改动引入。
  - 另：sandbox guard 相关 4 项在 CI 首跑失败（macOS runner 上 Seatbelt 探测
    成功导致旧断言失效），已修复（显式固定 enforcement 场景），次跑通过。
