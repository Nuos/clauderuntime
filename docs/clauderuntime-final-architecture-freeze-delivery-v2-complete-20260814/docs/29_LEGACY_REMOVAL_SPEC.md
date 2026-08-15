# Legacy / Compatibility Cleanup 规范

> 文档编号：`CR-LEGACY-CLEANUP-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

候选：`src/cli_backup`、旧 prompt/context builder、旧 background task maps、deprecated docs/pointers。

删除门：

1. import search；
2. callgraph/search production refs；
3. tests refs 分类；
4. entrypoint/package include 检查；
5. compatibility/public API 判断；
6. zero-ref evidence 或 deprecation plan。

无法证明无生产引用 → 不删，只标 deprecated/compatibility-only。
