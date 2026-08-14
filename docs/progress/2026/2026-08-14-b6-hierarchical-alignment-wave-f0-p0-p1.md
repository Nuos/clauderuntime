# B6 分级 Reference 对齐 — Wave F0 + P0/P1 开发进度

> 阶段：`B6 / Wave F0 + P0/P1`
> 日期：`2026-08-14`
> Subject commit：`dc7393bb05de7dc328d5206e19ba2e15997c1656`（基线，本阶段尚未提交）

# 1. 本轮目标

不是“对齐 Reference”，而是落地 B6 的三件事：

1. **Wave F0 — 差异透明制度**：建立 `docs/reference-differences/registry.yaml`
   全局台账并把治理门禁接入，使后续每一处转译/改写都能回答 REF/PY/DIFF/WHY/STATUS。
2. **P0 — 安全旁路审计**：逐项核对验收清单 B 节，修复发现的两个真实问题
   （沙箱 guard 陈旧判断、MCP 断开后 stale 工具）。
3. **P1 — 三个最高优先级功能项**：新进程 Resume smoke、Linux/Windows 最低隔离、
   Surface smoke 套件。

# 2. 完成内容

- 功能 A：`docs/reference-differences/registry.yaml`（7 条种子差异，schema 与
  词汇表与模板一致）+ `docs/reference-differences/README.md`。
- 功能 B：`scripts/check_docs_governance.py` 更新 —— B6 交付目录与
  `reference-differences` 进入 allowlist；新增 `check_reference_differences`
  校验 registry 的 required tokens、status/reason/certainty/alignment/impact
  词汇表与 id 唯一性。
- 安全修复 C（P0）：`src/permissions/sandbox_guard.py` 改为能力感知 ——
  macOS Seatbelt 真实可用时不再误报“UNSANDBOXED”、不再错误触发 hard-gate；
  无隔离平台保持 warn / fail-closed。`MacOSSandboxBackend` 探测按进程缓存。
- 安全修复 D（P0）：MCP 断开后 stale 工具清理 —— `McpClient` 在传输关闭时触发
  disconnect handler；`McpRuntime` 移除该 server 的 tools 并回调
  `agent_server` 从 live registry `remove_tool`（含 OAuth 重连的旧 client
  迟到关闭保护）。
- 功能 E（P1）：新进程 Resume smoke —— `tests/test_b6_resume_new_process_smoke.py`，
  两个独立解释器跨进程完成 transcript + metadata 写入 → 重建 → resume → 完成。
- 功能 F（P1）：Linux bubblewrap backend（真实隔离，argv 包装）+ Windows
  Job Object backend（进程树包含，LIMITED，fail-closed）+ `win_job_launcher.py`。
- 功能 G（P1）：Surface smoke 套件 `tests/test_b6_surface_smoke.py` —— Server
  面（启动/回答/Read/权限/中断/续谈）+ CLI headless 面（启动/回答/Read）。
- 标记：本轮触及的核心模块补齐 Reference Mapping / REF-DIFF
  （sandbox.py、sandbox_guard.py、client.py、mcp_runtime.py、agent_server.py、
  win_job_launcher.py）。

# 3. 针对性测试

```text
tests/test_b6_* （5 个新文件）
+ tests/test_sandbox_guard.py / test_sandbox_backend.py / test_sandbox_policy.py
+ tests/test_resume_agent.py / test_resume_agent_contract.py
+ tests/server/test_mcp_runtime.py + ch15/r5 MCP 刷新与顺序测试
127 passed
0 failed

补充：
tests/server/test_agent_server_e2e.py 等 server 套件 58 passed
tests/test_settings.py + test_permission_settings_paths.py 33 passed
```

# 4. 组合测试

本轮涉及 sandbox↔bash、MCP↔registry、resume↔subprocess 跨模块，已分别跑
sandbox 全套（81 passed）与 MCP 全套（45+6 passed）；跨模块组合主要体现在
`tests/test_b6_surface_smoke.py`（server+CLI 真实链路）。

# 5. Full Suite

未执行，按开发阶段测试规则不要求每次小改全量测试（文档基线 10160 passed 仍可信，
阶段收尾再跑全量）。

# 6. Reference 对照与差异

## DIFF-SANDBOX-001（更新）

```text
REF Source: utils/sandbox/sandbox-adapter.ts + shouldUseSandbox.ts
REF Behavior: 命令在真实 OS sandbox 内执行；capability 必须真实。
Python File/Symbol: src/execution/sandbox.py（MacOS/Linux/Windows/NoSandbox backend）
Python Behavior: macOS Seatbelt、Linux bubblewrap、Windows Job Object（进程树包含）、
                 无后端显式 no-sandbox；require_isolation 一律 fail-closed。
Difference: OS primitive 不同；Windows 仅进程树包含，非文件系统沙箱。
Reason: OS_PLATFORM_ADAPTATION + PRODUCT_SCOPE_SIMPLIFICATION
User Impact: LOW
Safety Impact: NONE（fail-closed 保持）
Status: FUNCTIONAL_ADAPTATION（Windows 子项 LIMITED）
Accepted: true
```

## DIFF-MCP-001（本轮新增/关闭）

```text
REF Source: useManageMCPConnections — server 断开时移除其工具。
Python File/Symbol: src/services/mcp/client.py::set_disconnect_handler /
                    src/server/mcp_runtime.py::_handle_client_disconnect /
                    src/server/agent_server.py::_make_mcp_disconnect_handler
Python Behavior: 传输关闭（EOF/错误）→ 从 runtime 与 live registry 移除
                 mcp__<server>__* 工具；干净 close()（shutdown/OAuth 重连）不触发。
Difference: 参考传输细节不复刻；"断开后无 stale 工具" 契约对齐。
Reason: PYTHON_RUNTIME_ADAPTATION
User Impact: LOW
Safety Impact: NONE
Status: FUNCTIONAL_ADAPTATION
Accepted: true
```

## DIFF-RESUME-002（本轮关闭）

```text
REF Source: resumeAgent.ts — 服务重启后重建后台 Agent。
Python File/Symbol: src/agent/resume_agent.py::resume_agent_background
Python Behavior: 跨两个真实进程完成 transcript+metadata 重建、provider/tool
                 registry 当前进程重解析、单赢认领、stub run_agent 驱动到终态。
Difference: 不再有"新进程未验证"缺口 —— 该 P1 项已闭合。
Reason: PYTHON_RUNTIME_ADAPTATION
User Impact: NONE（验证项闭合）
Safety Impact: NONE
Status: FUNCTIONAL_ADAPTATION
Accepted: true
```

# 7. 本轮新增/关闭差异

```text
新增：DIFF-MCP-001（MCP 断开清理，功能新增）
关闭：DIFF-RESUME-002（新进程 Resume 从"未验证"到"已 smoke 验证"）
继续接受：DIFF-CCR03-001/002、DIFF-RESUME-001、DIFF-SCHED-001、
          DIFF-SANDBOX-001、DIFF-SURFACE-001、DIFF-PERM-001
```

# 8. 剩余功能缺口

- Windows Job Object 的 `win_job_launcher.py` 只能在 win32 真机验证；当前
  macOS 上仅锁定 capability/prepare/fail-closed 与 argv 结构。
- Linux bubblewrap 实际容器执行需 Linux 主机验证（本机为 macOS）。
- TUI/Desktop Surface smoke 未在本套件重复（ui-tui 自带 1692 测试；Desktop
  走 server 端 gateway）。

> 平台真机验证逐项登记见
> `docs/reference-differences/platform-verification.md`（`PENDING_REAL_DEVICE`），
> 禁止在真机验证前把“代码已写”写成“平台已验证”。

# 9. 延期 Reference 细节

- Snip 历史裁剪（DIFF-CCR03-001）：`RECOVERED_SOURCE_GAP`，保持 no-op，
  由 Tool Result Budget / Microcompact / AutoCompact 覆盖核心长上下文功能。
- Resume content replacement / worktree auto-recovery（DIFF-RESUME-001）：
  `PRODUCT_SCOPE_SIMPLIFICATION`，缺失 worktree 明确失败即可。
- Scheduler file watcher / owner takeover（DIFF-SCHED-001）：
  snapshot/restore 满足当前功能目标。
- Reference 全 Surface 逐字段 differential（DIFF-SURFACE-001）：
  每 Surface smoke compatibility 替代。

# 10. 当前阶段结论

```text
FUNCTIONAL_ADAPTATION
```

Wave F0 制度落地；P0 审计发现并修复 2 个真实问题；P1 三项（Resume smoke /
Linux+Windows 隔离 / Surface smoke）完成。Windows 隔离按平台限制为 `LIMITED`，
真实披露，未谎报 provides_isolation。

# Reference 分级对齐记录

```text
REFERENCE_CERTAINTY:
  DIFF-SANDBOX-001: R1_CONFIRMED（隔离契约可确认，MUST_ALIGN）
  DIFF-MCP-001:     R2_PARTIALLY_CONFIRMED（call-site/契约可确认）
  DIFF-RESUME-002:  R2_PARTIALLY_CONFIRMED
ALIGNMENT_POLICY: MUST_ALIGN / ALIGN_KNOWN_PART
Reference 是否可确定：是（隔离与断开契约）/ 部分（传输细节）
已确定部分是否完成对齐：是
未确定部分是否只做核心功能一致：是（Windows 进程树包含 + fail-closed）
差异是否已记录到代码附近：是（REF-DIFF / Reference Mapping）
差异是否已记录到全局 registry：是（docs/reference-differences/registry.yaml）
```
