# Extension Trust-before-Activation 规范

> 文档编号：`CR-EXTENSION-TRUST-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 1. ExtensionDescriptor

字段：`kind/name/source/scope/trust_level/provenance_hash/manifest/capabilities/executable_hooks`。

## 2. Trust Levels

`bundled / managed / user / project / mcp` 是 source-trust taxonomy，不直接等于 allow。Policy 还需考虑 workspace trust、管理员策略、签名/hash、server URL/auth 与 capability。

## 3. Activation

```text
Discover → Parse → Descriptor → Trust Resolve → Validate → Collision Check → Activate → Register
```

任何 project-level executable hook/shell/MCP server 在 workspace 未信任时，不允许 activation side effect。

## 4. Collision

同名 extension 不得 silent overwrite。候选政策：

1. exact duplicate hash → dedupe；
2. higher-precedence managed/bundled 可 shadow，但记录 provenance；
3. same-precedence conflict → reject；
4. project attempting to replace managed/bundled → deny unless explicit policy。

## 5. Rollback

Activation 中途失败必须撤销已注册 commands/tools/hooks/MCP resources。
