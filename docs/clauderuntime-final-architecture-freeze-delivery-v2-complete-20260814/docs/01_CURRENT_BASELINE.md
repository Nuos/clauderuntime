# 当前项目基线与状态词汇

> 文档编号：`CR-BASELINE-B7-FREEZE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## 1. Baseline

```yaml
project: ClaudeRuntime
repository: Nuos/clauderuntime
subject_entry_commit: 16da0cfea98d69987739a319ff6ae42cfd432d2c
functional_status: FUNCTIONALLY_SIMILAR_CORE_COMPLETE
architecture_status: FINAL_CLOSURE_REQUIRED
reference_alignment: HIERARCHICAL_REFERENCE_ALIGNMENT
reference_parity_status: PARTIAL_NOT_RELEASE_GATE
evidence_status: REBASE_REQUIRED
next_gate: ARCHITECTURE_FREEZE
```

## 2. 当前已经可以认为“主体成熟”的部分

- canonical Query 主循环已经成为生产主路径；
- Permission 具有 deny-first / ask / allow 规则与 headless fail-closed 逻辑；
- Tool execution、hooks、结果持久化与 streaming 主路径已经成型；
- 五阶段 Context/Compact 次序已经固定；
- MCP、Skill、Hook、Plugin、Subagent、Task、State/Resume 均不是“缺模块”；
- B6 仓库记录已有 10k+ 本地测试与 CI green 证据，但应重新绑定最终 Freeze SHA。

## 3. 不能写成“已完成”的部分

- Windows/Linux isolation 未取得最终真实设备证据；
- strict Source-Aligned / 1:1 parity 不成立，也不作为 Freeze Gate；
- CURRENT docs / scorecard / registry 的 subject commit 仍有 generation drift；
- `ToolContext` 仍有隐式 bypass 默认值；
- Turn preparation 仍存在两个语义 owner；
- extension activation trust 还没有统一前置边界；
- task runtime state 仍存在 legacy mirrors / 双写风险；
- CI quarantine 没有真正的单一机器清单。

## 4. 以后所有状态必须是二维的

不要再用一个“完成度百分比”混合功能、parity、安全、平台与证据：

| 轴 | 示例状态 |
|---|---|
| Functional | `COMPLETE / PARTIAL / MISSING` |
| Wiring | `WIRED / ISOLATED / LEGACY_ONLY` |
| Evidence | `NONE / LOCAL / CI / PLATFORM` |
| Reference | `CONFIRMED / ADAPTATION / ACCEPTED_DIFF` |
| Risk | `P0 / P1 / TEST_ONLY` |

## 5. Architecture Freeze 的意义

Freeze 不是“没有 bug”，而是：**runtime 主脊柱、owner、security boundary、extension activation boundary、persistence owner 与 CURRENT truth 均不再移动**。后续 bug fix 应在这些 contract 内完成。
