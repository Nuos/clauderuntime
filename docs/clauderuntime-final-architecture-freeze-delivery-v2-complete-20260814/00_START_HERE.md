# ClaudeRuntime 最终大改总交付包 — START HERE

> 文档编号：`CR-FINAL-PACK-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 0. 这次交付解决什么问题

本包不是继续扩功能，而是把 ClaudeRuntime 在 **Architecture Freeze 前最后需要统一的 owner、安全默认值、真值、生命周期与验证规则** 一次性收口。完成本包定义的 P0/P1 后，项目必须停止跨模块重写，进入逐模块与全局测试调试。

### 本包完整度

本包分成 8 类资产：

1. `docs/`：完整开发、架构、实施、测试、验收、发布文档；
2. `machine/`：Reference lock、SSOT、owner map、quarantine、test matrix、freeze gates 等机器可读配置；
3. `blueprints/`：关键新 owner / boundary 的 Python 参考骨架与 patch 说明；
4. `tests/`：Architecture Freeze 前应新增的 contract test / governance test 骨架；
5. `scripts/`：真值、quarantine、reference lock、freeze gate 校验脚本；
6. `templates/`：Issue、PR、差异登记、平台验证、Freeze、RC 记录模板；
7. `references/`：用户提供的源码链接、论文、七组件资料与本轮证据摘要；
8. `archive/`：上一阶段 B6 审计/基线，仅作为历史证据。

## 1. 推荐阅读顺序

```text
00_START_HERE
  ↓
docs/01_CURRENT_BASELINE
  ↓
docs/02_FINAL_ARCHITECTURE_DIAGNOSTIC
  ↓
docs/03_FINAL_ARCH_CLOSURE_MASTER_PLAN
  ↓
docs/04_BEHAVIOR_BIBLE_v2.2
  ↓
docs/06_RUNTIME_SPINE_SPEC
  ↓
docs/08_P0_IMPLEMENTATION_SPEC
  ↓
docs/09_P1_IMPLEMENTATION_SPEC
  ↓
docs/11_ACCEPTANCE_AND_FREEZE_GATE
  ↓
docs/12_TEST_DEBUG_MASTER_PIPELINE
```

## 2. 本轮只允许 6 类大改

- Repository Truth / Evidence SSOT；
- Permission Safe Default；
- Canonical Turn Preparation；
- Extension Trust-before-Activation；
- Runtime Task / Session Lifecycle / Persistence owner 收口；
- CI/Test/Platform Truth 收口。

## 3. 明确禁止重写

本轮不得以“更漂亮”“更像 Reference”为理由重写：

- canonical `query()` 状态机；
- Permission classifier 主算法；
- 五阶段 compact pipeline；
- MCP transport/auth 主体；
- TUI/Desktop wire protocol；
- Sandbox 主设计；
- Scheduler watcher/跨进程 owner takeover；
- Provider 大规模重构；
- Subagent orchestration 主体。

## 4. 最终状态机

```text
FINAL_ARCH_CLOSURE_REQUIRED
  → P0_CLOSURE_COMPLETE
  → P1_CLOSURE_COMPLETE
  → ARCHITECTURE_FREEZE
  → MODULE_VERIFICATION
  → INTEGRATION_VERIFICATION
  → FAULT_INJECTION
  → LONG_HORIZON
  → RELEASE_CANDIDATE
```

## 5. 证据口径

本包区分：`IMPLEMENTED / WIRED / TESTED_LOCAL / TESTED_CI / VERIFIED_PLATFORM / REFERENCE_CONFIRMED / ACCEPTED_DIFF`。仓库文档记录的测试结果不等于本包独立复现；如未在当前环境运行，不得写成“本次独立验证通过”。
