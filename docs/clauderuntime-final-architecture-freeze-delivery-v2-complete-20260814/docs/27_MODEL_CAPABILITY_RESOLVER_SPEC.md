# ModelCapabilityResolver 规范

> 文档编号：`CR-MODEL-CAPS-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

Query 只能消费 capability snapshot，不直接维护 provider/model allowlist。

Capability 示例：adaptive thinking、interleaved thinking、prompt cache、tool choice/schema quirks、max context、stream events、image support、system prompt shape。

Resolver 输入：provider id + model id + provider config/version。输出 immutable `ModelCapabilities`。Fallback 时必须重新 resolve，不可沿用前一个 provider snapshot。
