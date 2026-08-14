# ClaudeRuntime B5 开发进度记录

> 文档编号：`CR-B5-DEVELOPMENT-PROGRESS`  
> 状态：**ACTIVE — Wave A0 Truth Reconciliation**  
> 启动日期：2026-08-13  
> B5 冻结基线：`95efbaec4796147657668c4947a0d2088ecc4738`  
> Reference：Claude Code recovered source `2.1.88` / `a8a678cb6244e6770e1e421767ff0987a1d95549`

## 1. 强制记录规则

1. 只记录可复现事实，不以代码数量、测试数量或文档声明代替 Source-Aligned 证明。
2. 单项测试通过只能写该单项“测试通过”，不能据此写整个阶段或整个 B5 完成。
3. `VERIFIED` 必须同时具备 reference symbol、Python symbol、调用关系、运行记录和差异测试。
4. 发现实现缺陷或证据冲突后继续修复；确有外部条件阻塞时，明确写出阻塞条件和未完成范围。
5. 没有当前 HEAD 的 GitHub workflow/status 证据时，只能写“本地测试通过”，禁止写“CI 通过”。

## 2. 当前阶段状态

| 工作项 | 工作类型 | 状态 | 测试状态 | 当前事实 |
|---|---|---|---|---|
| A0 基线资料校验 | 审计 | 完成 | 已校验、通过 | B5 原始 7 个受控文件 SHA-256 全部通过 |
| A0 机器证据冲突审计 | Bug 审计 | 完成 | 已检查 | 已确认旧基线和 Resume/Scheduler/Cross-Surface 状态冲突 |
| A0 错误完成声明降级 | Bug 修复 | 完成 | 已测试、通过 | 不满足 v6 证据字段的旧 `VERIFIED` 已降为 `PARTIAL` |
| A0 一致性检查器 | 新增 | 进行中 | 已测试、通过 | 已检查基线、无证据完成声明、状态冲突和计分卡；原子生成器未实现 |
| A1 Compact-5 修正 | Bug 修复 | 进行中 | 已测试、通过 | early-return 和 Microcompact 调用形态已修复；Snip 仍未实现 |
| A2 Context-9 修正 | Bug 修复 | 进行中 | 已测试、通过 | 项目级路径规则已接入；User/Managed 和 compact 重载未验证 |
| A3 Durable Resume | 功能补全 | 未开始 | 未测试 | 当前仅支持同进程真实恢复，进程重启后无法重建运行依赖 |
| A4 跨平台隔离 | 功能补全 | 未开始 | 未测试 | macOS 子集已测试；Linux、Windows 真实隔离未实现 |

## 3. 已确认遗留问题

1. 机器证据：`Bug、正在修复`。
   - 多数文件仍绑定 B3 提交 `4a77f06`，不是 B5 基线 `95efbae`。
   - Resume 在 callgraph/state map 中为 `BLOCKED`，在 runtime trace 中为 `VERIFIED`。
   - Scheduler 和跨入口结论在不同文件中不一致。

2. Compact-5：`Bug、未修复`。
   - Python 全局 early-return 会跳过后续压缩层，与 reference 连续调用流程不一致。
   - Snip 当前是固定空实现，不能标记为完成。
   - Microcompact 默认整个阶段不调用，不能等同于 reference 的“调用后内部判断不处理”。

3. Context-9：`Bug、未修复`。
   - `path_rules` 被错误记录到权限系统；实际应为按文件路径延迟加载的上下文指令。
   - 尚无生产链路证明读取文件后规则只注入一次。

4. Resume：`功能不完整、未修复`。
   - 同进程恢复已真实重新进入 Agent Loop。
   - `resume_run_params` 不持久化，服务重启后不能进行 durable reconstruction。

5. Isolation：`功能不完整、未修复`。
   - macOS Seatbelt 子集已实现并有本地测试。
   - Linux、Windows 仍无真实隔离后端；域名白名单也未执行。

## 4. 本轮测试记录

1. B5 文件完整性：`已测试、测试通过`。
   - `shasum -a 256 -c SHA256SUMS.txt`
   - 结果：原始 7 个受控文件全部 `OK`。

2. A0 机器证据检查：`测试中`。
   - 首次结果：`1 failed, 1 passed`，检查器发现 `32` 项旧基线、无证据完成声明和状态冲突问题。
   - 修复后结果：`2 passed`。
   - 命令行检查：14 个受控机器证据文件通过，基线统一为 `95efbae`。

3. A1 Compact-5 第一批修复：`进行中、已测试、测试通过`。
   - Bug：早层节省 token 达到阈值后直接返回，导致后续 shaping 层不执行。
   - 修复：生产默认 `source_aligned=True` 时连续执行全部层；旧 early-exit 仅保留为显式产品扩展。
   - Bug：Microcompact 默认在 pipeline 外层完全跳过。
   - 修复：每轮调用 Microcompact，由内部关闭的 feature gate 返回空操作。
   - 测试：压缩专项 `63 passed in 18.04s`。
   - 未完成：Snip 仍是固定空实现；在 reference 实现证据恢复前不制造模拟实现，也不标记 A1 完成。

4. A2 Context-9 项目级路径规则：`进行中、已测试、测试通过`。
   - Bug：带 `paths:` 的规则会被生产 `get_memory_files()` 排除，机器证据还错误映射到权限系统。
   - 修复：成功读取匹配的项目文件后加载 `.clawcodex/rules/*.md`，作为 meta user context 注入。
   - 优化：同一规则在单个会话只注入一次；并发 Read 使用锁保证不重复。
   - 安全：规则符号链接逃逸到项目外部时拒绝注入。
   - 测试：新增 E2E 覆盖匹配注入、重复读取不重复注入和不匹配不加载；相关测试 `160 passed`。
   - 未完成：User/Managed 路径规则、compact/resume 后的重载语义尚未验证，A2 不标完成。

5. A0 唯一分类与文档治理：`进行中、已测试、测试通过`。
   - 旧 `5 Parity Layers` 和 `AUX-01..14` 已标为历史辅助映射，不再参与完成度计分。
   - 正式分类改为 Reference-7、Reference-5、CCR-14。
   - 首次文档治理检查失败 `8` 项；修复目录白名单、旧字段和旧分类检查后通过。
   - 综合检查：功能和机器证据测试 `104 passed`；Documentation governance check passed。
   - 未完成：受控机器证据仍为手工维护，尚未实现同一命令原子生成全部文件，因此 A0 整体保持进行中。

6. 全项目测试：`已测试、测试通过`。
   - 结果：`10151 passed, 10 skipped, 3 warnings, 345 subtests passed`。
   - 用时：`278.11s`。
   - 结论范围：仅证明当前工作区本地 Python 测试通过；没有当前 HEAD GitHub workflow/status 证据，不宣称 CI 通过。
   - B5 总状态：`进行中`。A0 原子生成器、A1 Snip、A2 剩余作用域、A3 Durable Resume、A4 跨平台隔离均未完成。

## 5. GitHub 提交记录

1. B5 本轮功能提交：`完成、已推送`。
   - 提交：`4126dd5`（`fix: 启动 B5 事实校正与语义修复`）。
   - 目标仓库：`github.com/Nuos/clauderuntime.git`。
   - 目标分支：`main`。
   - 推送结果：`95efbae..4126dd5  HEAD -> main`。
   - 提交范围：37 个正式文件；未提交缓存、临时文件、API key 或个人信息。

2. B5 当前开发状态：`进行中`。
   - 本次提交不代表 B5 全部完成。
   - 未完成范围保持不变：A0 原子生成器、A1 Snip、A2 剩余作用域、A3 Durable Resume、A4 跨平台隔离。

## 6. 后续代码注释规则

1. 模块注释规则：`新增、已写入长期开发规范`。
   - 所有代码模块的模块级注释、模块级文档字符串必须使用简体中文；新增或修改代码时必须执行本规则。
   - 注释必须结合模块真实生产业务，说明业务对象、关键流程、边界条件或失败处理，禁止空泛占位描述。
   - 标准协议名、API 名和代码标识符可以保留英文，但必须用简体中文说明其业务含义。
   - 未实现或未测试的能力必须明确标注真实状态，禁止注释写成已经完成。

2. 执行要求：`后续持续执行`。
   - 新增模块必须满足该规则。
   - 修改现有模块时，必须同步修正该模块中过期、错误或不符合真实业务的模块注释。
   - 代码评审与完成状态检查必须包含该规则；不符合时不得标记为开发完成。
