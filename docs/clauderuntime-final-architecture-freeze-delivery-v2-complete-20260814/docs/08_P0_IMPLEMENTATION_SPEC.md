# P0 Implementation Spec

> 文档编号：`CR-P0-IMPLEMENTATION-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## P0-A Repository Truth Reset

### 修改
1. 建立 canonical `reference-lock.yaml`；
2. baseline/status/plan/registry/scorecard 都写同一 `subject_commit`；
3. governance script 检查所有 CURRENT 资产；
4. README 只指向 canonical current docs；
5. historical docs 加 superseded banner。

### 测试
- stale SHA → fail；
- missing reference generation → fail；
- current doc points archive → fail；
- registry accepted diff 缺 evidence → fail。

## P0-B Permission Safe Default

推荐优先方案：`ToolContext.permission_context` **不提供默认值**。如果兼容性要求必须有 default，则只能是 `mode="default"` + fail-closed ask semantics，绝不能是 bypass。

所有 bypass 构造必须类似：

```python
ToolPermissionContext(
    mode="bypassPermissions",
    bypass_origin="trusted_internal_test_or_explicit_cli",
    bypass_reason="...",
)
```

禁止仅凭 bool 打开 bypass。

## P0-C Canonical Turn Preparation

创建 `PreparedTurn` typed object。迁移顺序：

1. characterization tests 固定两个旧 builder 当前输出；
2. 新 service 先内部调用现有 helpers；
3. headless/server/TUI adapters 切换；
4. QueryEngine 改为 facade；
5. 删除重复 assembly；
6. 增加 surface-equivalence tests。

## P0-D Extension Activation Gate

Activation 输入至少包含：kind、name、source_path/server、scope、trust_level、workspace_trusted、manifest hash、requested capabilities。

结果：`ALLOW / DENY / REQUIRE_TRUST / INVALID / COLLISION`。任何结果必须可审计。

## P0-E Task Single Writer

任何 runtime task lifecycle 状态变更只能调用 RuntimeTaskRegistry。Legacy `tasks` / `background_bash_tasks` 只能读 projection 或通过 adapter 转发到 registry。

## P0-F CI Truth

CI 不再直接写 5 个 `--deselect`。改为脚本读取 `machine/ci-quarantine.yaml`，生成参数并验证每项仍存在。过期 quarantine 自动 fail 或至少 warning + release gate fail。
