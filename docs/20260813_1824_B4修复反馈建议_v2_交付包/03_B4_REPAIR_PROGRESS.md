# B4 最新反馈修复进度

更新时间：2026-08-13

## 1. 工作进度

1. Machine Evidence：`优化完成、已测试、测试通过`。
   - 已使用 `subject_commit`，不再把证据提交自身当作验收对象。
   - 生成器可一次更新全部证据提交号、派生计分卡并最后写入哈希清单，不再要求手工同步台账。
   - 证据对象：`7619ff2886160de3409acd1d4e87880d04da6e9e`。
   - 证据提交：`cc264e5`。
   - 测试结果：生成器与检查器 `3 passed`；14 个受控文件校验通过。

2. Compact：`Bug 修复完成、已测试、测试通过`。
   - Microcompact 默认值已改为关闭，保持 60 分钟阈值和 5 条近期记录。
   - Snip 不再错误宣称参考实现是空函数；当前明确记录为“参考调用点已确认、函数体未完整恢复、Python 暂为无操作占位”。
   - 当前限制：Snip 真实参考函数体仍未恢复，因此该子项保持 `部分完成`，禁止标记完全等价。

3. Context Rules：`优化完成、已测试、测试通过`。
   - 已支持 Managed、User、Project CWD 和 Project 子目录规则。
   - 已验证匹配、不匹配、重复读取、并发去重、符号链接越界拒绝。
   - 已验证 Read 产生的规则会进入下一次模型调用且只进入一次。
   - 已验证压缩成功后清除登记，后续 Read 可重新加载规则。
   - 相关组合测试：`94 passed`。

4. Durable Resume：`优化完成、已测试、测试通过、整体部分完成`。
   - 已持久化安全恢复元数据；不保存 provider 对象、API key、工具实例和临时权限。
   - 进程内注册表丢失后，可从 transcript 和元数据重建任务，并使用当前 provider、工具注册表和 Agent 定义。
   - 已验证敏感字段不落盘、临时权限不恢复、缺失 worktree 明确失败、并发恢复只有一个成功者。
   - Resume 与 SendMessage 相关测试：`44 passed`。
   - 当前限制：真实进程替换、content replacement 和 worktree 自动恢复尚无完整证明，因此不声明 Durable Resume 全部完成。

5. Scheduler：`Bug 修复完成、已测试、测试通过、整体部分完成`。
   - 已增加并持久化 `last_fired_at`。
   - 普通一次任务离线错过后丢弃；durable 一次任务恢复后只补执行一次。
   - Scheduler 专项测试：`28 passed`。
   - 当前限制：独立文件任务、文件监听、跨进程 owner 接管仍未实现。

6. Agent 服务数据隔离：`新增 Bug 修复、已测试、测试通过`。
   - 标准输入和 WebSocket 服务不再写死 `~/.clawcodex/server-sessions.json`。
   - 会话索引统一遵循 `CLAWCODEX_CONFIG_DIR`，测试子进程不会污染真实用户目录。
   - 服务与索引专项测试：`13 passed`；本机端口相关测试：`177 passed`。

7. Cross-platform Isolation：`进行中、当前平台测试通过、跨平台未完成`。
   - macOS 本机系统隔离与内存目录测试：`6 passed`。
   - Linux、Windows 原生隔离必须在对应系统实现和验证，当前 macOS 不能伪造通过结果。

8. Full Surface：`未完成`。
   - Core 与 Server 已有测试；CLI、TUI、Desktop、IDE 尚无同一输入下的完整运行差异证明。

9. Current-HEAD CI：`未开始远端测试`。
   - 当前只完成本地测试，没有推送本轮提交，也没有 GitHub CI 结果。
   - 禁止把本地测试通过写成 GitHub CI 通过。

## 2. 全项目测试结果

1. 受限环境首轮：`10089 passed, 73 failed, 10 skipped`。
   - 其中大部分失败是受限环境禁止监听 `127.0.0.1` 临时端口。
   - 另发现两个真实问题：全局 transcript 测试隔离影响路径断言；Agent 服务会话索引写死用户目录。

2. 修复结果：`已修复、已回归`。
   - 路径隔离与恢复回归：`14 passed`。
   - Agent 服务与会话索引：`13 passed`。
   - 本机端口测试：`177 passed`。
   - macOS 系统隔离与内存目录：`6 passed`。

3. 最终不联网全项目测试：`10160 passed, 10 skipped, 1 deselected, 3 warnings, 345 subtests passed`。
   - 失败数：`0`。
   - 未执行外部测试：PyPI editable install 1 项；官方 MCP/npm 示例服务 1 项。
   - 未执行原因：两项都会访问外部服务，当前未获得相应外联授权。

## 3. 当前结论

1. 本轮可在 macOS 本地完成的 R1、R2、R3 修复已完成并通过测试。
2. R4、R5 已有实质修复，但仍存在文中列明的功能缺口，状态保持 `部分完成`。
3. R6、R7、R8 未满足最终验收条件，禁止声明 B4 全部完成。
4. 本轮没有推送 GitHub；远端 CI 状态为 `未测试`。
