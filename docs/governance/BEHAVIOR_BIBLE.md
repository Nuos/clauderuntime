# ClaudeRuntime Behavior Bible

status: CURRENT
owner: repository-governance
created: 2026-08-15
last_verified: 2026-08-15
subject_commit: a01b089b4cef06c05a941b2c0dedaa30ba02069a
supersedes: none
superseded_by: none

> 文档编号：`CR-BEHAVIOR-BIBLE-v2.2`
> 依据交付包：`docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/docs/04_BEHAVIOR_BIBLE_v2.2.md`
> Reference：Claude Code 2.1.88 recovered source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`
> 阶段：最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试

## A. Truth Before Progress

任何"完成"声明先回答：实现在哪、是否接线、测试在哪、在哪个平台验证、是否与
Reference 一致、若不一致是否登记。

证据标签固定为：

`IMPLEMENTED / WIRED / TESTED_LOCAL / TESTED_CI / VERIFIED_PLATFORM / REFERENCE_CONFIRMED / FUNCTIONAL_ADAPTATION / PRODUCT_EXTENSION / ACCEPTED_DIFF`。

## B. Reference Law

Reference generation 固定为：Claude Code 2.1.88 **recovered source-map snapshot**，
不得称为 Anthropic 官方开源源码。论文用于架构归纳，不代替源码行为证据。

## C. One Semantic Core

一个生产语义只能有一个 authoritative owner。允许多个 surface adapter，不允许多个
prompt/context builder、permission resolver、task writer、extension activation policy。

## D. Permission Law

- `DENY > ASK > ALLOW`；
- no implicit bypass；
- bypass 必须 explicit + origin + reason；
- headless 无交互通道时 ask → deny；
- pre-trust 不执行 project executable content；
- child/subagent permission ceiling 不得高于 parent。

## E. Permission × Execution Double Boundary

Permission 决定 **是否允许**；ExecutionBoundary 决定 **允许后仍受哪些 OS/process/
filesystem/network 约束**。任何工具都不得只依赖其中一层。

## F. Turn Preparation Law

所有 surface 在进入 canonical query 前必须使用同一 TurnPreparation owner。System
prompt、workspace context、MCP/skills context、tool visibility、output style、
model capability、compaction config 不得在多个入口各自拼装。

## G. Extension Lifecycle Law

Discovery 与 Activation 分离。Project Plugin/Skill/Hook/MCP 不能因为"发现了"就执行。
Activation 必须有 provenance、trust、validation 与 deterministic collision policy。

## H. Context Law

五阶段压缩顺序固定。算法变化属于 Architecture Freeze 后禁止项，除非测试证明 contract
无法满足。压缩不能只返回 `bool`；必须留下 outcome/evidence。

## I. State / Resume Law

Persistence 保存 durable semantics，不保存 live privilege。Resume 不恢复：临时
permission、workspace trust verdict、API key 明文、MCP live session、线程/锁/OS
handle、旧 abort controller。

## J. Task Law

一个 runtime task 只能有一个 writable state owner。Legacy APIs 可以存在，但只能
投影/适配，不可双写。

## K. Subagent Law

Subagent context 隔离、permission ceiling 继承、abort/fault 不得拖死 parent。
Sidechain / transcript 必须可追踪 parent-child lineage。

## L. Tool Law

Tool descriptor 尽量作为 schema/permission/side-effect/concurrency metadata 单一
事实源。Tool executor 必须可观测：permission decision、hook decision、execution
boundary、result persistence、error classification。

## M. Hook Law

Hook failure mode、timeout、SSRF/HTTP safety、trust source 必须明确。PostSampling
additional contexts 若未注入 query context，必须明确 accepted diff，不能静默"看似支持"。

## N. MCP Law

MCP 是外部 capability boundary。连接、认证、tool namespace、server crash、
reconnect、output validation 必须测试。MCP tool 不能绕过 normal permission/execution
policy。

## O. CI/Test Law

CI deselect/quarantine 只能来自一个 machine manifest。每项必须有 reason、owner、
added_at、expiry/review date、replacement coverage。禁止 yaml 手抄与 docs 另写两个列表。

## P. Platform Evidence Law

"支持 Windows/Linux/macOS"与"已真实验证 isolation"是两个不同陈述。必须分别记录。

## Q. Eval / Completion Law

模型说"完成"不等于任务完成。长期目标固定为：

```text
Task Contract
→ Execution Trace
→ Verifier
→ Evidence Artifact
→ Completion Decision
```

## R. Project Identity Law

仓库名、distribution name、CLI name、README、project URLs 可以有兼容 alias，但必须
有明确 canonical identity 与 deprecation policy。

## S. Freeze Law

Architecture Freeze 后：不得因为目录不好看、代码太长、与 Reference 不够像而发起跨模块
重写。只有已验证 contract 无法满足时才允许 RFC 级结构变化。
