# Canonical TurnPreparationService 详细规范

> 文档编号：`CR-TURN-PREPARATION-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## Input

`TurnRequest(surface, user_messages, custom_system_prompt, append_system_prompt, output_style, provider/model overrides, session flags)` + `RuntimeSession`。

## Output: PreparedTurn

- `system_prompt_blocks`；
- `messages`；
- `visible_tools`；
- `mcp_context`；
- `skill_context`；
- `workspace_context`；
- `model_capabilities`；
- `compact_config`；
- `prompt_cache_scope`；
- `query_params`；
- `provenance`（哪些输入来自 config/workspace/plugin/skill）。

## Invariants

- 同一 session/request 在不同 surface 下，除明确 surface-specific fields 外应得到等价 PreparedTurn；
- pre-trust 阶段不读取/执行不安全 project executable context；
- tool visibility 在 query 前固定 snapshot，动态 refresh 必须走明确 refresh hook；
- builder 不执行 model call；
- query 不重新拼 full system prompt。
