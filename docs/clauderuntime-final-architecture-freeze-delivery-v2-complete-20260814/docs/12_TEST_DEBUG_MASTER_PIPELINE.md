# Architecture Freeze 后测试/调试总 Pipeline

> 文档编号：`CR-TEST-DEBUG-PIPELINE-v2.0`  
> 项目：`Nuos/clauderuntime`  
> Subject baseline：`main@16da0cfea98d69987739a319ff6ae42cfd432d2c`  
> Reference：Claude Code 2.1.88 recovered source / source-map snapshot @ `a8a678cb6244e6770e1e421767ff0987a1d95549`  
> 论文：*Dive into Claude Code: The Design Space of Today’s and Future AI Agent Systems*，arXiv:2604.14228v2  
> 阶段：**最后一次大规模架构收口 → ARCHITECTURE_FREEZE → 测试/调试**

## T0 Baseline / Static / Import / Docs Truth

导入全部 public modules；lint/import contracts；reference lock；current truth；quarantine；packaging metadata。

## T1 Permission

模式矩阵：default / acceptEdits / plan / dontAsk / auto / bypass explicit；deny/ask/allow precedence；path gates；headless；subagent ceiling；MCP/tool differences。

## T2 Execution / Sandbox

cwd/root containment、process kill、timeout、env、network policy、symlink/path traversal、Windows Job Object、Linux bwrap、macOS sandbox/fallback。

## T3 Individual Tools

每个工具：schema、invalid input、permission contract、side effects、large result、abort、streaming、encoding、resource cleanup。

## T4 Tool Execution + Hooks

PreTool/PostTool/HTTP/prompt hooks；timeout；hook deny/modify；result persistence；concurrent read tools；aggregate budget。

## T5 Agent Loop

normal turn、multi-tool、retry、provider fallback、stream interruption、abort、budget、tool error loops、terminal conditions。

## T6 Context / Compact / Cache

五阶段顺序、hard window、snip artifact、microcompact、collapse、autocompact、多次连续 compact、prompt cache scope、additional context。

## T7 State / Persistence / Resume

append/atomicity、corruption recovery、resume/fork/rewind、missing/dirty worktree、ephemeral state drop、conversation lineage。

## T8 Subagent / Background / Task / Scheduler

permission ceiling、abort cascade、resume、name collision、task idempotency、scheduler restart/missed/duplicate fire、foreground/background policy equivalence。

## T9 MCP / Plugin / Skill / Hook Supply Chain

trust gate、auth、OAuth/token store、server crash、reconnect、namespace collision、plugin name collision、project trust、skill shell permission。

## T10 Surfaces

CLI/headless/TUI/Desktop/AgentServer：prepared turn equivalence、permission roundtrip、event envelopes、non-interactive behavior。

## T11 Cross-component Integration

长链：prompt → tool → hook → permission → execution → task → persistence → compact → resume → subagent/MCP。

## T12 Fault Injection

provider 429/500、network reset、tool hang、hook exception、disk full/readonly、partial JSONL write、MCP crash、thread cancellation、corrupt state。

## T13 Long Horizon

100+ turns、多轮 compact、多个 background tasks、scheduler restart、resume 多次、provider fallback、memory provenance/staleness。

## T14 Global Regression / RC

全量 Python + TUI + Desktop + platform smoke；freeze governance；release packaging；最终 evidence bundle。
