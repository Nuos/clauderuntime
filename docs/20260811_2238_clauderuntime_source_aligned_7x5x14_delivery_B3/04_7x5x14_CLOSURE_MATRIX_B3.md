# ClaudeRuntime B3 — 7×5×14 Closure Matrix

# 1. Reference-7

| ID | Component | 关键责任 | 主要 CCR | Final Gate |
|---|---|---|---|---|
| R7-01 | User | authority, permission, interrupt, session actions | CCR-02/10/13/14 | 跨 surface user action trace 等价 |
| R7-02 | Interfaces | adapters, events, render, interaction | CCR-07/08/14 | 不拥有第二套 core semantics |
| R7-03 | Agent Loop | model→tool→result→repeat | CCR-03/04/06/08/14 | query control-flow differential |
| R7-04 | Permission System | rules/modes/classifier/human ask | CCR-01/02/12/13 | deny-first + fail-closed |
| R7-05 | Tools | descriptor/pool/orchestration/execution/results | CCR-05/06/07/09 | builtin/MCP/subagent action contract |
| R7-06 | State & Persistence | transcript/context/session/lineage | CCR-03/04/09/10/11/13 | crash/resume/fork/rewind |
| R7-07 | Execution Environment | workspace/process/sandbox/network/env | CCR-12/13/14 | isolation + abort/process lifecycle |

# 2. Reference-5

| ID | Layer | 主要内容 | Required CCR |
|---|---|---|---|
| R5-01 | Surface | CLI/Headless/SDK/TUI/Desktop/IDE | CCR-07/08/14 |
| R5-02 | Core | Agent Loop + Context/Compact | CCR-03/04/06/08/14 |
| R5-03 | Safety/Action | Permission/Hooks/Tools/Extensibility/Sandbox/Subagent | CCR-01/02/05/06/07/09/11/12/13 |
| R5-04 | State | Context/State/Transcript/Memory/Sidechains/Resume | CCR-03/04/09/10/11/13 |
| R5-05 | Backend | Process/Sandbox/MCP/Remote/External resources | CCR-06/07/12/14 |

# 3. CCR-14

| ID | Cross-Cutting Runtime Mechanism | 必须证明的核心行为 |
|---|---|---|
| CCR-01 | Hook Runtime | lifecycle event、match、execute、timeout、blocking/async、permission/stop integration |
| CCR-02 | Authorization Pipeline | deny→ask→tool check→mode/classifier/user→execution boundary |
| CCR-03 | Context Shaping | Result Budget→Snip→Microcompact→Collapse→AutoCompact |
| CCR-04 | Context Assembly | 9 context sources、scope、precedence、provenance、dedupe |
| CCR-05 | Capability Assembly | base→mode→deny prefilter→MCP/extensions→dedupe |
| CCR-06 | Tool Orchestration | concurrent-safe / serialized mutation / completion / result order |
| CCR-07 | Streaming Tool Execution | queue→executing→completed→ordered yield、fallback、abort |
| CCR-08 | Recovery / Resilience | retry、max-output、prompt-too-long、reactive compact、stream/model fallback |
| CCR-09 | Result Processing | normalization、mapping、budget、replacement、persistence、reconstruction |
| CCR-10 | Session / Transcript | append、lineage、tail recovery、compact boundary、resume/fork/rewind |
| CCR-11 | Subagent Orchestration | delegation、isolation、sidechain、background、summary return |
| CCR-12 | Isolation Runtime | filesystem/network/env/process/worktree/remote boundary |
| CCR-13 | Trust Lifecycle | source/scope/lifetime、resume trust reset、managed limits |
| CCR-14 | Runtime Config | settings/env/features/modes snapshot、precedence、gate consistency |

# 4. Legacy AUX → B3 Canonical Mapping

| Legacy obligation | B3 canonical owner |
|---|---|
| Main Agent Query Loop | R7-03 / R5-02 |
| Tool Execution Loop | CCR-06 + CCR-07 |
| Permission Escalation Loop | CCR-02 + CCR-13 |
| Retry / Model Recovery | CCR-08 |
| Compaction Loop | CCR-03 |
| Stop Hook Loop | CCR-01 + R7-03 |
| Subagent Query Loop | CCR-11 |
| Background Agent Lifecycle | CCR-11 + CCR-10 + CCR-14 |
| MCP Lifecycle | CCR-05 + CCR-06 + CCR-12 + CCR-13 |
| Scheduler / Cron | CCR-14 + CCR-10 + CCR-06 |
| Resume / Fork / Rewind | CCR-10 + CCR-13 |
| Surface Streaming / Interrupt | R7-02 + CCR-07 + CCR-08 |
| Session Persistence / Recovery | CCR-10 |
| Long-output Result Budgeting | CCR-09 + CCR-03 |

# 5. Closure Gate Template

每一行最终必须同时填写：

```yaml
reference_files: []
reference_symbols: []
reference_call_edges: []
python_files: []
python_symbols: []
runtime_trace: []
state_invariants: []
safety_invariants: []
failure_invariants: []
tests: []
status: EXACT | SEMANTIC_EQUIVALENT | PYTHON_ADAPTATION_VERIFIED
```

任一字段为空且属于该节点必要证据，则不得 complete。
