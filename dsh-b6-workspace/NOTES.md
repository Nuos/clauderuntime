# B6 开发工作笔记（dsh- 草稿区，非交付物）

> 正式交付物见：docs/reference-differences/registry.yaml、docs/progress/2026/2026-08-14-*.md、
> src/execution/sandbox.py 等；本目录只放草稿/临时/审计笔记。

## P0 审计结论（2026-08-14）

验收清单 B 节逐项核对：

| 项 | 结论 |
|---|---|
| Permission deny 不可绕过 | OK：dispatch 统一走 context.ensure_tool_allowed；deny → ToolPermissionError |
| background 不成为安全旁路 | OK：fg/bg/Monitor 三条 bash 路径都过 bash_command_safety_guard + prepare_sandbox |
| required isolation 不可静默退化 | 修复前存在"guard 假设无 enforcement"的陈旧判断 → 已改为能力感知；fail-closed 保持 |
| stale MCP tools 不可继续调用 | 修复前 _on_disconnect 声明但从未接线 → 已实现 client→runtime→registry 全链路清理 |
| Resume 不恢复 API key/临时权限 | OK：resume_metadata 白名单字段，不序列化实时对象（已有测试锁定） |
| timeout 后 child process 不继续执行 | OK：run_process_tree 整树 SIGTERM→SIGKILL（已有测试） |
| symlink/path escape 有明确处理 | OK：DefaultWorkspaceGuard 先 resolve 再比对 roots（已有测试） |

修复的两个真实问题：

1. **sandbox_guard 陈旧**：docstring/消息声称"本构建无沙箱 enforcement"，但
   MacOSSandboxBackend(Seatbelt) 已实现并接线。后果：macOS 上
   `enabled+failIfUnavailable=true` 连可用沙箱都被硬拒绝；`enabled` 单独时
   警告"UNSANDBOXED"而实际已沙箱（说谎）。
   修复：guard 查询真实 backend capability；探测按进程缓存。
2. **MCP 断开无清理**：McpClient._on_disconnect 字段存在但从未赋值/触发；
   server 崩溃后其 mcp__server__* 工具永远留在 live registry 供模型调用。
   修复：EOF/接收循环错误触发 disconnect handler → McpRuntime 移除 tools →
   agent_server 从 registry remove_tool。干净 close（shutdown / OAuth 重连
   旧 client）不触发；旧 client 迟到关闭被 identity 检查忽略。

## 待办/后续

- [ ] win32 真机验证 win_job_launcher.py（本机 macOS 只能锁结构）
- [ ] Linux 主机验证 bubblewrap 实际容器执行
- [ ] 阶段收尾 full local suite（10160 passed 基线之上重跑）
