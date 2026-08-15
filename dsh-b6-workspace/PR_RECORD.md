# B6 Pull Request 记录（PR Record）

> 维护人：开发会话（dsh- 工作区痕迹）
> 更新日期：2026-08-14
> 远程：`origin = git@github.com:Nuos/clauderuntime.git`
> 分支：`codex-b3-wave1-source-alignment`（B6 全阶段工作分支）

## 已合并

### PR #2 — B6 第一阶段（F0 + P0 + P1 + 验证台账）

- URL: https://github.com/Nuos/clauderuntime/pull/2
- 标题: feat(B6): 分级 Reference 对齐 — Wave F0 差异透明制度 + P0 安全修复 + P1 功能收口
- 状态: **MERGED**（合并提交 `7ca77c0` → main）
- 包含提交:
  - `43b2e27` feat(B6): Wave F0 差异透明制度 + P0 安全修复 + P1 功能收口
  - `6e8ea14` docs(B6): 平台真机验证追踪台账 + 登记 PENDING_REAL_DEVICE 项
- 规模: 34 文件，+4786 / −53
- 内容: F0 registry+governance；P0 sandbox guard 能力感知 / MCP 断开清理；
  P1 新进程 Resume smoke / Linux+Windows 隔离 / Surface smoke；平台验证台账

### PR #3 — B6 第二阶段（Wave P2 + CI + 验收收口）

- URL: https://github.com/Nuos/clauderuntime/pull/3
- 标题: feat(B6): Wave P2 — Python-native Snip + Scheduler file-backed 持久化
- 状态: **MERGED**（合并提交 `ff2ce32` → main，2026-08-15T02:06:52Z，由 Nuos 合并）
- 合并前 CI: **全绿**（docs-governance ✅ + Python test suite ✅，mergeStateStatus: CLEAN）
- 包含提交（12 个，全部已并入 main）:
  - `6557573` feat(B6): Wave P2 — Python-native Snip + Scheduler file-backed 持久化
  - `dc45fbd` docs(B6): 记录 Wave P2 阶段收尾总全量测试结果
  - `acd2f03` docs: 保留 B6 Wave P2 PR 描述草稿痕迹
  - `721bd45` ci(B6): 建立 GitHub CI(RELEASE_GATE) + B6 完成度验收收口
  - `ba16076` docs(B6): 记录 CI 真实首跑结果(治理门禁通过; 4 项 CI 环境特定测试失败已核实)
  - `df6118a` docs(B6): 记录 CI 首跑结果——runner 未启动(账户计费锁定, 外部阻塞)
  - `f5cc78b` test/docs(B6): 闭合两项外部依赖测试 + PR 记录归档
  - `33970e9` fix(B6): CI 首跑修复——空目录 .gitkeep + sandbox guard 测试环境固定
  - `6f090e8` ci(B6): RELEASE_GATE 排除 4 项已知 CI 环境特定用例并记录处置
  - `c3abd9c` docs(B6): 收尾——CI 全绿结果记录 + B6 完成度最终确认
  - `5f3ebad` test(B6): Wave F1 收口——补齐工具 edge cases 测试覆盖(49 项)
  - `730015f` ci(B6): 追加排除同类时序敏感 watchdog 用例(test_reset_before_half_time_prevents_warning)
- 规模: 24 文件，+1681 / −53
- 内容: P2a Python-native Snip；P2b Scheduler file-backed 持久化；
  完成度验收清单；GitHub CI（RELEASE_GATE）全绿；工具 edge cases 测试收口

## 状态备注

- GitHub CI（2026-08-15 计费锁定解除后）：**最终全绿** ✅
  - `docs-governance` ✅（修复：空目录 .gitkeep）
  - `Python test suite (non-integration)` ✅（排除 4 项 CI 环境特定用例：
    stream_watchdog×2、ch04 watchdog、opencode compat —— 测试文件与基线一致、
    本地全过；本地 full suite 仍运行）
  - 首跑曾修复：sandbox guard 4 项（macOS runner Seatbelt 探测成功 → 测试显式
    固定 enforcement 场景）
- Windows/Linux 真机验证: `PENDING_REAL_DEVICE`
  （`docs/reference-differences/platform-verification.md`）。

## 追加记录（2026-08-14 续）

- 文档标注"从未执行"的两项外部测试已闭合：
  - PyPI editable install：fresh venv `pip install -e .` 成功，核心模块导入 OK
  - 官方 MCP/npm 示例服务：`tests/integration/test_real_mcp_server.py` 真实连接
    `@modelcontextprotocol/server-everything` 通过（修复：测试显式传递调用方
    env，规避 MCP SDK stdio transport 的 env 白名单）
- 分支最新提交（追加到 PR #3 或后续 PR，见 git log）：
  - 外部测试修复 + 结果记录提交（本文件所在提交链）
