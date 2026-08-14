# B4 最新反馈修复进度

更新时间：2026-08-13

## 1. 当前工作状态

1. R1 Machine Evidence：`优化、进行中、已测试通过`。
   - 已移除机器证据与当前 HEAD 自引用的 baseline 模型，改为明确的 `subject_commit`。
   - 已新增原子生成脚本，计分卡由覆盖台账计算，清单记录 14 个受控文件 SHA-256。
   - 已新增清单哈希校验；测试结果：`2 passed`。
   - 待完成：本轮生产代码形成独立 subject commit 后，重新生成最终证据提交。

2. R2 Compact：`Bug 修复、已测试通过`。
   - Microcompact 默认值已从错误的启用改为关闭，保持 `60` 分钟阈值和 `5` 条近期记录。
   - Snip 注释已纠正：只确认参考调用点，参考函数体未完整恢复；Python 保持 UNKNOWN/PARTIAL 无操作占位。
   - Compact 相关组合测试已通过。

3. R3 Context Rules：`功能优化、已测试通过`。
   - 已支持 Managed、User、Project CWD 和 Project nested-directory 条件规则。
   - 已验证匹配、不匹配、并发单次注入、符号链接逃逸防护。
   - 已验证规则进入下一次模型调用且只出现一次。
   - 自动压缩成功后会清空路径规则登记，后续 Read 可重新加载。
   - 本轮相关组合测试：`94 passed`。

4. R4 Durable Resume：`功能优化、已测试通过`。
   - 已新增不含 provider、API key、工具实例和临时权限的安全恢复元数据。
   - 进程重启后可从 transcript 与元数据重建任务，并使用当前 provider、工具注册表和 Agent 定义。
   - 已验证敏感字段不落盘、临时权限不恢复、缺失 worktree 明确失败和并发单赢。
   - Resume 与 SendMessage 相关测试：`44 passed`。

5. R5 Scheduler：`进行中、未完成`。
   - 当前已有 session snapshot/restore，但 file-backed task、owner takeover、文件监听和完整 source lifecycle 尚未完成。

6. R6 Cross-platform Isolation：`未完成、需要真实平台测试`。
   - macOS 已有 Seatbelt 子集。
   - Linux、Windows 原生隔离不能在当前 macOS 环境伪造测试通过。

7. R7 Full Surface：`未完成`。
   - Core 与 Server 之外的 CLI、TUI、Desktop、IDE 完整 runtime differential 尚未完成。

8. R8 Current-HEAD CI：`未完成`。
   - 本轮代码尚未提交，因此没有 current-HEAD GitHub CI 结果。

## 2. 测试问题与解决策略

1. 首次 Compact 专项测试：`未启动`。
   - 原因：系统 `python3` 环境没有 pytest。
   - 解决：改用项目 `.venv/bin/python`；结果通过。

2. Durable Resume 首轮测试：`3 failed`。
   - 原因一：旧测试把 transcript 写入用户目录，当前沙箱拒绝。
   - 解决：测试使用独立临时配置目录，不污染用户数据。
   - 原因二：旧断言仍要求返回“尚不支持恢复”。
   - 解决：保留明确依赖错误并提示创建新 Agent；重新测试结果 `44 passed`。

## 3. 完成声明限制

1. 当前 B4 修复总状态：`进行中`。
2. 本文件只记录已经执行的本地测试，不代表 GitHub CI 通过。
3. Scheduler、跨平台隔离、全 Surface 和 current-HEAD CI 未完成前，禁止声明 B4 全部完成。
