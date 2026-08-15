# B6 Wave F1 收口补充 — Tool edge cases 测试补全

> 阶段：`B6 / Wave F1 补充（Tools 完善）`
> 日期：`2026-08-15`
> 依据：05 号文档 Tools 项"下一步：补缺失 tool edge cases"

# 1. 本轮目标

按 05 号文档对 Tools 的下一步指引，补齐缺失的工具 edge case 测试覆盖，
发现并锁定真实行为边界。

# 2. 完成内容

- 功能 A：`tests/tool_system/test_mcp_resources.py`（15 项）—— ListMcpResourcesTool /
  ReadMcpResourceTool 此前 **0 测试引用**（完全未测试）。覆盖：输入校验（空/非
  字符串 server、缺 uri）、未连接 server、server 过滤、空结果映射、单客户端
  异常不使整体失败、非列表返回跳过、无 list_resources 属性跳过、
  read_resource 返回形态归一化（contents 透传 / 普通 dict 包装 / 非 dict 转 text）、
  mapResultToApi JSON 往返。
- 功能 B：`tests/tool_system/test_notebook_edit.py`（12 项）—— NotebookEdit 三种
  编辑模式（replace/insert/delete）+ 位置 cell-id 寻址 + 输入校验（非 .ipynb、
  非法 edit_mode、insert 缺 cell_type、未知 cell_id、越界、文件不存在、未读/
  已变更拒绝、非法 JSON）。
- 功能 C：`tests/tool_system/test_web_fetch_url_validation.py`（22 项）——
  WebFetch `_validate_url`（SSRF 防护）此前无直接测试。覆盖：http→https 升级、
  非 http(s) 协议拒绝、无网络位置拒绝、内嵌凭据拒绝、单段主机名拒绝、
  localhost 系列拒绝、私网/回环/保留地址（127.x/10.x/192.168.x/172.16.x/
  169.254.x/0.0.0.0）拒绝、超长 URL 拒绝、公开主机放行。

# 3. 针对性测试

```text
tests/tool_system/test_mcp_resources.py          15 passed
tests/tool_system/test_notebook_edit.py          12 passed
tests/tool_system/test_web_fetch_url_validation.py  22 passed
tests/tool_system/ + test_tool_system_tools 等   219 passed
（3 项失败为已知环境性 PTY 问题，与基线一致）
```

# 4. 组合测试

本轮为纯测试补充（无行为改动），不涉及跨模块组合；MCP resource 工具与
MCP client 的既有测试（tests/server/test_mcp_runtime.py 等）继续通过。

# 5. Full Suite

未执行；本轮无生产代码改动。阶段收尾全量结果见
`docs/progress/2026/2026-08-14-b6-completion-checklist.md`（10212 passed）。

# 6. Reference 对照与差异

本轮无新增差异（未改动生产代码，仅补测试覆盖既有行为）。既有 registry
条目不变。

# 7. 本轮新增/关闭差异

```text
新增：0
关闭：0
```

# 8. 剩余功能缺口

- Windows/Linux 真机验证仍为 `PENDING_REAL_DEVICE`。
- mcp_resources / notebook_edit / web_fetch 的 edge cases 现已锁定，无已知缺口。

# 9. 延期 Reference 细节

不变（见前序 progress 文档）。

# 10. 当前阶段结论

```text
FUNCTIONAL_COMPLETE（Tools 边缘行为测试覆盖补齐，无行为改动）
```
