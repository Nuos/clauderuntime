# ClaudeRuntime B3 — Tools & Permissions Symbol 级双向对照报告

> 文档编号：`CR-B3-TOOLS-PERMISSIONS-SYMBOL-MAP`
> 依据：Wave 0 收尾——P0 模块 tool_system / permissions symbol 级对照
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def` / Reference `2.1.88` @ `a8a678cb`
> 对照范围：reference `utils/permissions/`（19 文件）+ `Tool.ts`/`tools.ts` ↔ python `permissions/`（31 文件）+ `tool_system/`（63 文件）
> 日期：2026-08-12

## 1. 结论摘要

1. **PY_ONLY 落点定位（重要）**：reference 侧 permission 机制位于 **`utils/permissions/` 目录**（非独立包），python `permissions/` 包即为对应实现——`permissions` 从"无同名 reference 缺口"升级为 **落点已定位**。
2. **EXACT 同名族 6 组**（reference 函数名 ↔ python 函数名逐一对应）：
   - `permissions.ts`（getAllowRules/getDenyRules/getAskRules/toolMatchesRule/getDenyRuleForTool/getAskRuleForTool/filterDeniedAgents）↔ `rules.py` 同名 snake_case 族；
   - `PermissionUpdate.ts`（extractRules/applyPermissionUpdate/applyPermissionUpdates/supportsPersistence/persistPermissionUpdate/persistPermissionUpdates）↔ `updates.py` 同名族；
   - `permissionRuleParser.ts`（normalizeLegacyToolName/getLegacyToolNames/escapeRuleContent/unescapeRuleContent/permissionRuleValueFromString/permissionRuleValueToString）↔ `rule_parser.py` 同名族；
   - `getNextPermissionMode.ts`（getNextPermissionMode/cyclePermissionMode）↔ `cycle.py` 同名；
   - `tools.ts`（getAllBaseTools/filterToolsByDenyRules/assembleToolPool/getMergedTools/getTools）↔ `registry.py` 同名族；
   - `PermissionMode.ts`（permissionModeFromString/permissionModeTitle/permissionModeShortTitle/permissionModeSymbol/toExternalPermissionMode）↔ `modes.py` 同名族。
3. **强语义对应 8 组**：PermissionRule.ts↔types.py、permissionsLoader.ts↔loader.py、denialTracking.ts↔check.py(DenialTracker)、bashClassifier.ts↔bash_security.py、pathValidation.ts↔filesystem.py、shellRuleMatching.ts↔bash_suggestions.py、shadowedRuleDetection.ts↔setup.py、Tool.ts↔build_tool.py+context.py。
4. 以上全部升级 **STRUCTURAL_VERIFIED**（文件级 1:1 或目录级对应 + 符号级同名双证据）；行为差分留 Wave 2。
5. 待定位：bypassPermissionsKillswitch.ts（疑 dangerous_safety.py）、permissionExplainer.ts（疑 handler.py）——保持 UNKNOWN。

## 2. EXACT 同名族对照（STRUCTURAL_VERIFIED）

### 2.1 permissions.ts ↔ permissions/rules.py

| Reference（utils/permissions/permissions.ts） | Python（permissions/rules.py） |
|---|---|
| getAllowRules | get_allow_rules |
| getDenyRules | get_deny_rules |
| getAskRules | get_ask_rules |
| toolMatchesRule | _tool_matches_rule |
| getDenyRuleForTool | get_deny_rule_for_tool |
| getAskRuleForTool | get_ask_rule_for_tool |
| filterDeniedAgents | filter_denied_agents |
| toolAlwaysAllowedRule | tool_always_allowed_rule |
| getRuleByContentsForTool | get_rule_by_contents_for_tool |

### 2.2 PermissionUpdate.ts ↔ permissions/updates.py

| Reference | Python |
|---|---|
| extractRules | extract_rules |
| applyPermissionUpdate | apply_permission_update |
| applyPermissionUpdates | apply_permission_updates |
| supportsPersistence | supports_persistence |
| persistPermissionUpdate | persist_permission_update |
| persistPermissionUpdates | persist_permission_updates |
| hasRules | has_rules |

### 2.3 permissionRuleParser.ts ↔ permissions/rule_parser.py

| Reference | Python |
|---|---|
| normalizeLegacyToolName | normalize_legacy_tool_name |
| getLegacyToolNames | get_legacy_tool_names |
| escapeRuleContent | escape_rule_content |
| unescapeRuleContent | unescape_rule_content |
| permissionRuleValueFromString | permission_rule_value_from_string |
| permissionRuleValueToString | permission_rule_value_to_string |

### 2.4 getNextPermissionMode.ts ↔ permissions/cycle.py

| Reference | Python |
|---|---|
| getNextPermissionMode | get_next_permission_mode |
| cyclePermissionMode | cycle_permission_mode |

### 2.5 tools.ts ↔ tool_system/registry.py

| Reference（tools.ts） | Python（tool_system/registry.py） |
|---|---|
| getAllBaseTools | get_all_base_tools |
| filterToolsByDenyRules | filter_tools_by_deny_rules |
| assembleToolPool | assemble_tool_pool |
| getMergedTools | get_merged_tools |
| getTools | get_tools |
| TOOL_PRESETS | （python 侧 preset 机制待定位） |

### 2.6 PermissionMode.ts ↔ permissions/modes.py

| Reference | Python |
|---|---|
| permissionModeFromString | permission_mode_from_string |
| permissionModeTitle | permission_mode_title |
| permissionModeShortTitle | permission_mode_short_title |
| permissionModeSymbol | permission_mode_symbol |
| toExternalPermissionMode | to_external_permission_mode |
| isExternalPermissionMode | is_external_permission_mode |

## 3. 强语义对应（STRUCTURAL_VERIFIED）

| Reference | Python | 对应依据 |
|---|---|---|
| PermissionRule.ts（permissionBehaviorSchema/permissionRuleValueSchema） | types.py（PermissionRule/PermissionRuleValue） | 类型定义对应 |
| permissionsLoader.ts（settingsJsonToRules/loadAllPermissionRulesFromDisk） | loader.py（settings_to_rules/apply_rules_to_context）+ settings_paths.py | 规则加载链路 |
| denialTracking.ts（createDenialTrackingState/recordDenial/recordSuccess/shouldFallbackToPrompting/DENIAL_LIMITS） | check.py（DenialTracker/get_denial_tracker）+ yolo_classifier.py（DenialState） | 拒绝追踪状态机 |
| bashClassifier.ts（classifyBashCommand/ClassifierResult/ClassifierBehavior） | bash_security.py（analyze_bash_command/check_bash_command_safety） | bash 命令分类 |
| pathValidation.ts（validatePath/isPathAllowed/isDangerousRemovalPath/validateGlobPattern） | filesystem.py（check_path_safety_for_auto_edit/check_read_permission_for_path/check_write_permission_for_path）+ bash_mode_validation.py（is_dangerous_removal_path） | 路径安全校验 |
| shellRuleMatching.ts（parsePermissionRule/matchWildcardPattern/suggestionForExactCommand/suggestionForPrefix） | bash_suggestions.py（suggestion_for_prefix/suggestion_for_exact_command） | shell 规则匹配/建议 |
| shadowedRuleDetection.ts（detectUnreachableRules/isAllowRuleShadowedByDenyRule） | setup.py（_detect_shadowed_rules） | 规则遮蔽检测 |
| Tool.ts（buildTool/toolMatchesName/findToolByName/ToolUseContext/QueryChainTracking） | build_tool.py（build_tool/tool_matches_name/find_tool_by_name/Tool）+ context.py（ToolContext/QueryChainTracking） | tool 构建与上下文 |

## 4. 待定位（UNKNOWN，不冒充完成）

| Reference | Python 候选 | 说明 |
|---|---|---|
| bypassPermissionsKillswitch.ts（checkAndDisableBypassPermissionsIfNeeded） | dangerous_safety.py（enforce_dangerous_skip_permissions_safety）？ | 语义相近待核实 |
| permissionExplainer.ts（generatePermissionExplanation/RiskLevel） | handler.py（handle_permission_ask）？ | 权限解释链路待核实 |
| autoModeState.ts（setAutoModeActive/isAutoModeCircuitBroken） | yolo_classifier.py / modes.py？ | auto-mode 状态待核实 |
| classifierShared.ts / classifierDecision.ts | yolo_classifier.py 部分 | 分类器共享逻辑待核实 |
| TOOL_PRESETS | tool_system 内 preset 机制 | 待定位 |

## 5. 未确认项

1. ☐ 以上 STRUCTURAL_VERIFIED 均为符号级证据；deny-first 行为、mode 转换语义、tool pool 投影行为差分留 Wave 2；
2. ☐ permissions 模块开发状态升级为 MAPPING_VERIFYING（4 组 EXACT + 4 组强对应）；
3. ☐ tool_system 模块开发状态升级为 MAPPING_VERIFYING（1 组 EXACT + 1 组强对应）；
4. ☐ 待定位 5 项保持 UNKNOWN，待 Wave 2 逐项核实。
