# ClaudeRuntime B3 — W0~W3 整体核验报告

> 文档编号：`CR-B3-W0W3-VERIFICATION`
> 核验范围：Wave 0（Reference Contract Freeze）→ Wave 3（State/Session/Trust）已开发内容
> 核验维度：功能 / 模块结构 / 目录结构 / 7 核心功能组件 / 规则圣经（行为圣经）合规
> 基准：`03_CLAUDE_CODE_SOURCE_ALIGNED_RULE_BIBLE_v4.0.md` + `04_7x5x14_CLOSURE_MATRIX_B3.md`
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def` / Reference `2.1.88` @ `a8a678cb`
> 日期：2026-08-12

## 0. 结论摘要

| 维度 | 判定 | 说明 |
|---|---|---|
| 功能核验 | ✅ 通过 | 全量 10088 passed / 0 failed（两次复跑稳定），本次新增 82 项测试 |
| 模块结构 | ✅ 通过 | 55 模块 R5 五层归类清晰，无第二套 core semantics |
| 目录结构 | ✅ 通过 | Python 合理边界，未为 TS 目录外观破坏 Python 结构 |
| 7 核心组件 | ⚠️ 6/7 有实现+验证，1 项缺口 | R7-07 Real Sandbox 未实现（NoSandboxBackend 唯一 backend） |
| 规则圣经合规 | ⚠️ 核心条款合规，Exit Gate 未通过 | 9-step/双路径/Stop/Safety 已验证；完成状态术语需澄清；R7-07 + resume 缺口 |

**最终判定：W0~W3 开发内容整体核验通过（功能/结构/目录/合规），但 7×5×14 Exit Gate 尚未达到——R7-07 Real Sandbox、resume 真重入为确认缺口，符合规则圣经 §18"在此之前唯一正确开发行为是继续完成 7×5×14"。**

## 1. 功能核验

### 1.1 全量测试

```
10088 passed, 10 skipped, 12 warnings, 345 subtests passed in 266.85s
```

两次复跑稳定通过，零回归。

### 1.2 本次开发新增测试（82 项 / 12 文件）

| 测试文件 | 项数 | 对应功能 |
|---|---|---|
| test_sourcemap_generator.py | 24 | Wave 0 盘点生成器 |
| test_query_turn_steps.py | 9 | F1 9-step trace |
| test_query_generator_cleanup.py | 3 | F3 abort/close 清理 |
| test_query_terminal_parity.py | 4 | F5 terminal reasons |
| test_query_recovery_parity.py | 4 | F4 recovery 差分 |
| test_permission_safety_parity.py | 4 | F6 权限安全链 |
| test_tool_pool_assembly.py | 5 | F7 tool pool 投影 |
| test_dual_path_parity.py | 6 | F8 双路径 |
| test_tool_result_contract.py | 8 | F9 result 契约 |
| test_transcript_contract.py | 5 | F11 transcript 契约 |
| test_pre_trust_gate.py | 6 | F13 trust lifecycle |
| test_resume_agent_contract.py | 4 | F12 resume 现状锁定 |

## 2. 模块结构核验（55 模块 → R5 五层）

| 层 | 模块 | 数量 | 核验 |
|---|---|---|---|
| R5-01 Surface | assistant/bridge/buddy/cli_backup/cli_core/command_system/components/entrypoints/screens/server/transports/vim/voice/core-single-files/keybindings | 14 | ✅ 仅承担 input adapter/event/render，无第二套 core（headless.py 经 agent_loop_compat 适配器汇入 query） |
| R5-02 Core | agent/query/goals/plan | 4 | ✅ query() 为 authoritative reactive loop；agent_loop_compat.py:43 `from .query import query`（适配器非第二 loop） |
| R5-03 Safety/Action | permissions/auth/tool_system/workflow/hooks/plugins/skills | 7 | ✅ deny-first 链 + tool pool 投影（Wave 2 验证） |
| R5-04 State | state/memory/memdir/knowledge/wiki | 5 | ✅ transcript append-oriented + trust lifecycle（Wave 3 验证） |
| R5-05 Backend | execution/providers/remote/upstreamproxy | 4 | ⚠️ execution 含 sandbox 协议骨架，Real Sandbox 未实现 |
| 横切（CCR 归属） | services/compact_service/context_system/coordinator/tasks/scheduled_tasks/settings/models/constants/types/utils/migrations/moreright/native_ts/reference_data/eco | 21 | ✅ CCR-03/04/06/09/14 落点 |

**核验结论**：模块结构合规，无违反绝对禁止"禁止新增第二 Agent Loop"（agent_loop_compat 为适配器）、"禁止 surface 自实现 core semantics"（permission 仅在 permissions/、tool 调度仅在 tool_system+services）。

## 3. 目录结构核验

```
clauderuntime/
├── docs/           # 开发文档 + B3 交付包 + sourcemap 盘点
├── src/            # 55 模块源码（按职责分包，非 TS 目录外观）
├── scripts/        # 工程脚本（sourcemap_generator 等）
├── tests/          # 测试（parity/ 差分测试 + 单元测试）
├── eval/           # 评测
├── examples/       # 示例
├── ui-desktop/ ui-tui/  # 桌面/TUI 前端（Surface 层）
├── pyproject.toml / uv.lock / requirements*.txt  # Python 包管理
├── install.sh / install.ps1                      # 安装脚本
└── README.md / CHANGELOG.md / CONTRIBUTING.md / LICENSE
```

**核验结论**：符合规则圣经 §17"禁止为 TypeScript 目录外观破坏 Python 合理边界"——src/ 按 Python 职责分包（query/tool_system/permissions/services...），未模仿 TS 目录外观。

## 4. 7 核心功能组件核验

| 组件 | 实现落点 | 验证状态 | 判定 |
|---|---|---|---|
| R7-01 User | 横切：query.py（AbortController interrupt）+ terminal.py（session 控制）+ entrypoints/headless.py | Wave 1 F3 abort + F5 terminal | ✅ 有实现+验证（横切组件，无独立模块属正常） |
| R7-02 Interfaces | 14 模块（Surface 层） | Wave 0 盘点 + 无第二套 core | ✅ |
| R7-03 Agent Loop | query/query.py 主循环 + agent_loop_compat 适配器 | Wave 1 F1 9-step trace + F4 recovery + F5 terminal | ✅ |
| R7-04 Permission System | permissions/（check.py deny-first 5 步链） | Wave 2 F6 + 既有 parity 测试 | ✅ |
| R7-05 Tools | tool_system/（registry/build_tool/context） | Wave 2 F7 pool 投影 + F8 双路径 + F9 result | ✅ |
| R7-06 State & Persistence | state/ + memory/ + memdir/ | Wave 3 F11 transcript + F13 trust | ✅ |
| R7-07 Execution Environment | execution/（sandbox.py/boundary.py/policy.py） | ⚠️ 协议骨架完整，**Real Sandbox 未实现**（default_sandbox_backend 返回 NoSandboxBackend） | ❌ 缺口 |

**R7-07 核验详情**：`execution/sandbox.py` 有 SandboxBackend Protocol + SandboxCapability/Policy/Request/Invocation/ExecutionResult 完整契约，但唯一 backend 是 `NoSandboxBackend`（L76，provides_isolation=False）。规则圣经 CCR-12 明确"`NoSandboxBackend` 不可计为 source-aligned isolation complete"——这是 B3 诊断 7.1 高风险缺口的坐实，为 Wave 4（Isolation/Backend）核心工作。

## 5. 规则圣经（行为圣经）合规核验

| 条款 | 要求 | 状态 |
|---|---|---|
| §7 9-step Trace | 9 步顺序 | ✅ Wave 1 F1（turn_steps.py + query() 9 挂接点） |
| §8 双路径 | Streaming/Batched 语义一致 | ✅ Wave 2 F8 |
| §9 Stop/Continue | 五类终止条件 + terminal 唯一事实源 | ✅ Wave 1 F5（reference 10 终态+7 继续态全覆盖） |
| §10 Safety 七层 | 纵深防御 7 gate | ✅ 部分（deny-first F6 + trust F13；sandbox 隔离层待 Wave 4） |
| §11 Permission 分类 | mode ≠ behavior | ✅ F6（deny/ask/allow 三 behavior + mode 分离） |
| §16 完成状态 | 仅 EXACT/SEMANTIC_EQUIVALENT/PYTHON_ADAPTATION_VERIFIED | ⚠️ 见下方术语澄清 |
| §17 绝对禁止 | 14 条 | ✅ 无违反（无第二 loop/surface 自实现/UNKNOWN 冒充 complete） |
| §18 Exit Gate | 7/7 + 5/5 + 14/14 + 0 UNKNOWN | ❌ 未通过（R7-07 + resume + 大量 UNKNOWN） |

### 5.1 术语边界澄清（核验发现）

开发文档/报告中使用的 `STRUCTURAL_VERIFIED` 是**映射证据状态**（表示文件级/symbol 级结构对应已核实，对应 04 矩阵 Closure Gate 的 reference_files/reference_symbols 字段），**不是完成状态**。规则圣经 §16 的完成状态仅三种（EXACT/SEMANTIC_EQUIVALENT/PYTHON_ADAPTATION_VERIFIED）。已确认所有 STRUCTURAL_VERIFIED 标注处均同步写明"行为差分留 Wave X"，未冒充 complete——但需澄清该术语不等于 source-aligned 完成。

## 6. 关键发现与缺口登记（如实，不冒充完成）

1. **B3 诊断 7.1 坐实**：Real Sandbox 未实现（NoSandboxBackend 唯一 backend）→ Wave 4 核心工作。
2. **B3 诊断 7.3 坐实**：resume 真重入未接线（resume_agent_background 不驱动 model；RunAgentParams.context_messages 已就绪，接线点已定位）→ Wave 3 遗留项。
3. **术语边界**：STRUCTURAL_VERIFIED = 映射证据状态 ≠ 完成状态（见 §5.1）。
4. **既有 flaky（非本次引入，已修复/登记）**：
   - test_review_fork：Memory 工具 enabled 依赖全局 settings 顺序（全量通过、子集失败）；
   - test_unknown_fails_closed：check_pre_trust_gate 的 workspace_trusted=None 读全局会话信任状态（测试显式传参已修复）。

## 7. Exit Gate 状态

```
R7:   6/7  verified（R7-07 缺口）      ✗ 未达 7/7
R5:   5/5  落点齐全，未 complete        ✗ 未达 5/5 complete
CCR: 14/14 落点齐全，未 complete        ✗ 未达 14/14 complete
Lifecycle: 14/14 落点，resume 真重入缺口  ✗
critical UNKNOWN = 大量（未冒充 complete）  ✗
```

**最终结论：按规则圣经 §18，Exit Gate 未通过，唯一正确行为是继续完成 7×5×14（Wave 4 Isolation/Backend 为下一优先级）。**
