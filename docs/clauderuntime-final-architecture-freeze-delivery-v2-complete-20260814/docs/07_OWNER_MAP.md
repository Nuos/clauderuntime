# Owner Map 与依赖方向

> 文档编号：`CR-OWNER-MAP-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 1. Owner 原则

Owner 不是“目录在哪”，而是“谁对最终语义负责”。一个 package 可以有很多 helper，但不可出现两个可以独立给出最终答案的 owner。

## 2. 推荐 owners

- `RuntimeSession`：会话级依赖与 capability references；
- `SessionLifecycle`：start/resume/fork/rewind/end；
- `TurnPreparationService`：进入 query 前的全部输入准备；
- `Query`：模型/工具轮次状态机；
- `PermissionResolver`：allow/ask/deny 最终裁决；
- `ExecutionBoundary`：OS/process/filesystem isolation；
- `ToolExecutionService`：tool 调度与结果映射；
- `RuntimeTaskRegistry`：后台 runtime tasks；
- `ExtensionActivationGate`：extension activation；
- `ModelCapabilityResolver`：model/provider capability snapshot；
- `CompletionVerifier`：任务完成的可验证判定；
- `EvidenceRegistry`：测试/平台/差异证据元数据。

## 3. 依赖方向

高层 surface 可以依赖 runtime facades；核心 policy 不得反向依赖 TUI/Desktop。Bootstrap state 仍作为 DAG leaf，不应反向 import feature subsystems。

## 4. 需要删除的 owner 重叠

- `QueryEngine._build_system_prompt_parts` vs `agent_loop_compat.build_effective_system_prompt`；
- `runtime_tasks` vs legacy background task dict 的写权限；
- plugin loader register vs trust decision；
- CI workflow 手工 deselect vs docs 手工 quarantine list。
