# B6 分级 Reference 对齐 — Wave P2 开发进度（Snip + Scheduler file-backed）

> 阶段：`B6 / Wave P2`
> 日期：`2026-08-14`
> Subject commit：`43b2e27`（上一阶段）；本阶段待提交

# 1. 本轮目标

补齐 B6 剩余两个可选 P2 功能项（02 号计划文档 Wave F2 / Wave F4 的“推荐后续”）：

1. **Python-native 安全 Snip**（方案 B）：只裁剪“可重建”的旧工具结果，
   标记 `FUNCTIONAL_ADAPTATION`，不再是无操作占位。
2. **Scheduler file-backed 持久化增强**：任务每次变更原子写盘，服务重启后
   可由新进程跨进程恢复，不再依赖会话 resume 文件。

# 2. 完成内容

- 功能 A（P2a）：`src/services/compact/snip_compact.py` 从 no-op 占位改为
  Python-native 保守 Snip —— 只裁剪可重建（只读工具 allowlist：
  Read/Glob/Grep/ListDir/WebFetch/TaskOutput）的旧工具结果；对话文本、
  tool_use 块、变更类工具（Write/Edit/Bash 等）结果、最近 `keep_recent`
  条可裁剪结果一律保留；来源工具无法确定的 tool_result 保守保留。
  修复 `[-0:]` 切片边界（keep_recent=0 时不得保留全部）。
- 功能 B（P2b）：`SessionCronScheduler` 新增 `persist_path` 可选持久化 ——
  `_persist_locked`（临时文件 + fsync + 原子 replace）、`persist`、
  `restore_persisted`、`from_persisted`；create/delete/set_wakeup/
  clear_wakeup/pop_due 变更即落盘；`agent_server._AgentSession` 的
  `cron_scheduler` 默认挂到 `~/.clawcodex/scheduled_tasks.json`，resume
  恢复后主动 `persist()` 同步文件。
- 测试更新：`tests/test_snip_compact.py`（10 项，从锁定 no-op 改为锁定新行为）；
  `tests/test_compression_pipeline.py` Layer 2 用例更新（真实 Snip 生效 +
  变更类工具不被裁剪）；新增 `tests/scheduled_tasks/test_scheduler_file_backed.py`
  （12 项：落盘/跨进程恢复/durable 补执行/过期丢弃/wakeup 恢复/失败非致命）。

# 3. 针对性测试

```text
tests/test_snip_compact.py                    10 passed
tests/test_compression_pipeline.py + parity   64 passed（含 Snip Layer 2 新用例）
tests/scheduled_tasks/test_scheduler_file_backed.py  12 passed
```

# 4. 组合测试

```text
tests/scheduled_tasks/ + test_background_scheduler.py +
test_agent_server_e2e.py + test_sandbox_guard.py   118 passed
（覆盖 scheduler 文件持久化 ↔ 会话/后台调度 ↔ server e2e 组合）
```

# 5. Full Suite

未执行，阶段收尾前按规则只跑针对性/组合测试；最后总全量测试单独记录。

# 6. Reference 对照与差异

## DIFF-CCR03-001（状态更新：DEFERRED → FUNCTIONAL_ADAPTATION）

```text
REF Source: query.ts::snipCompactIfNeeded（HISTORY_SNIP 下调用；函数体未恢复）
REF Behavior: 按 HISTORY_SNIP 语义裁剪过旧历史工具结果。
Python File/Symbol: src/services/compact/snip_compact.py::snip_compact
Python Behavior: 只裁剪可重建（只读 allowlist）的旧工具结果；其余一律保留。
Difference: 参考实现体未恢复，Python 用保守 allowlist 界定“可重建”。
Reason: RECOVERED_SOURCE_GAP + PYTHON_RUNTIME_ADAPTATION
User Impact: LOW
Safety Impact: NONE（变更类工具结果绝不裁剪）
Status: FUNCTIONAL_ADAPTATION
Accepted: true
```

## DIFF-SCHED-001（更新：file-backed 已实现）

```text
REF Source: cronScheduler.ts（file-backed scheduled_tasks.json + watcher + owner takeover）
Python File/Symbol: SessionCronScheduler.persist / restore_persisted / from_persisted
Python Behavior: 每次变更原子写盘；新进程从文件恢复；无 watcher / owner takeover。
Difference: 原子写而非 watcher；单进程 scope。
Reason: PRODUCT_SCOPE_SIMPLIFICATION
User Impact: LOW
Safety Impact: NONE
Status: FUNCTIONAL_ADAPTATION
Accepted: true
```

# 7. 本轮新增/关闭差异

```text
新增：0
关闭：DIFF-CCR03-001 从 DEFERRED_REFERENCE_DETAIL → FUNCTIONAL_ADAPTATION
继续接受：其余 7 条（含 DIFF-SCHED-001 更新为 file-backed 实现）
```

# 8. 剩余功能缺口

- Windows Job Object / Linux bubblewrap 真机验证仍为 `PENDING_REAL_DEVICE`
  （见 `docs/reference-differences/platform-verification.md`）。
- Scheduler file watcher / 跨进程 owner takeover 仍为
  `DEFERRED_REFERENCE_DETAIL`（Python 单进程 scope 内不需要）。
- P3（Reference 细节 parity / callgraph / full differential）明确不要求。

# 9. 延期 Reference 细节

- Snip 参考函数体：`RECOVERED_SOURCE_GAP`，Python 保守实现覆盖功能目标。
- Scheduler file watcher / owner takeover：`PRODUCT_SCOPE_SIMPLIFICATION`。
- Resume content replacement / worktree auto-recovery：维持
  `DEFERRED_REFERENCE_DETAIL`。

# 10. 当前阶段结论

```text
FUNCTIONAL_ADAPTATION
```

B6 两项 P2 功能完成：Snip 从占位升级为安全 Python-native 实现；
Scheduler 获得 file-backed 跨进程持久化。至此 B6 计划文档中全部可执行
开发项（P0–P2）完成。

# Reference 分级对齐记录

```text
REFERENCE_CERTAINTY:
  DIFF-CCR03-001: R2_PARTIALLY_CONFIRMED（call-site/返回契约可确认，函数体未恢复）
  DIFF-SCHED-001: R2_PARTIALLY_CONFIRMED
ALIGNMENT_POLICY: ALIGN_KNOWN_PART
Reference 是否可确定：部分（契约可确认，实现体未恢复）
已确定部分是否完成对齐：是（tokensFreed/boundaryMessage 契约、持久化目标）
未确定部分是否只做核心功能一致：是（保守 allowlist / 原子写文件）
差异是否已记录到代码附近：是（Reference Mapping / REF-DIFF）
差异是否已记录到全局 registry：是
```
