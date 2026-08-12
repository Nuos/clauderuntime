# ClaudeRuntime B3 — 文件级同名匹配报告（Reference ↔ Python）

> 文档编号：`CR-B3-FILE-LEVEL-MATCH`
> 依据：Wave 0 收尾（w0g）第一步——reference 与 python 文件名精确对照
> 基线：`def709361a86900920bf1d6b75134fdc9bc59def` / Reference `2.1.88` @ `a8a678cb`
> 快照：20260811_2345
> 机器可读完整数据：`docs/sourcemap/file-level-match.json`

## 1. 结论摘要

1. 总同名匹配: 803 条（reference 规范名 1575 / python 规范名 524 求交）
2. 1:1 唯一匹配: 211 条 —— 一个 reference 文件精确对应一个 python 文件，**最高置信度结构证据（STRUCTURAL_VERIFIED 候选）**
3. 多候选匹配: 136 条 —— 一个 reference 文件对应多个 python 候选（python 侧目录重组所致，保持 UNVERIFIED，需逐条核实）
4. 无匹配: reference 文件无同名 python 对应（UNKNOWN，等待 symbol 级核实或登记为缺口的候补证据）
5. 状态规则: 1:1 可升级为 STRUCTURAL_VERIFIED；多候选与无匹配维持 UNVERIFIED/UNKNOWN，禁止冒充完成

## 2. 1:1 唯一匹配清单（按 reference 模块分组）

| Reference 文件 | Python 文件 |
|---|---|
| **assistant**（1） | |
| `assistant/sessionHistory.ts` | `assistant/session_history.py` |
| **bridge**（26） | |
| `bridge/bridgeApi.ts` | `bridge/bridge_api.py` |
| `bridge/bridgeConfig.ts` | `bridge/bridge_config.py` |
| `bridge/bridgeEnabled.ts` | `bridge/bridge_enabled.py` |
| `bridge/bridgeMain.ts` | `bridge/bridge_main.py` |
| `bridge/bridgePermissionCallbacks.ts` | `bridge/bridge_permission_callbacks.py` |
| `bridge/bridgePointer.ts` | `bridge/bridge_pointer.py` |
| `bridge/bridgeStatusUtil.ts` | `bridge/bridge_status_util.py` |
| `bridge/capacityWake.ts` | `bridge/capacity_wake.py` |
| `bridge/codeSessionApi.ts` | `bridge/code_session_api.py` |
| `bridge/debugUtils.ts` | `bridge/debug_utils.py` |
| `bridge/envLessBridgeConfig.ts` | `bridge/env_less_bridge_config.py` |
| `bridge/flushGate.ts` | `bridge/flush_gate.py` |
| `bridge/inboundAttachments.ts` | `bridge/inbound_attachments.py` |
| `bridge/inboundMessages.ts` | `bridge/inbound_messages.py` |
| `bridge/initReplBridge.ts` | `bridge/init_repl_bridge.py` |
| `bridge/jwtUtils.ts` | `bridge/jwt_utils.py` |
| `bridge/pollConfig.ts` | `bridge/poll_config.py` |
| `bridge/pollConfigDefaults.ts` | `bridge/poll_config_defaults.py` |
| `bridge/remoteBridgeCore.ts` | `bridge/remote_bridge_core.py` |
| `bridge/replBridge.ts` | `bridge/repl_bridge.py` |
| `bridge/replBridgeHandle.ts` | `bridge/repl_bridge_handle.py` |
| `bridge/replBridgeTransport.ts` | `bridge/repl_bridge_transport.py` |
| `bridge/sessionIdCompat.ts` | `bridge/session_id_compat.py` |
| `bridge/sessionRunner.ts` | `bridge/session_runner.py` |
| `bridge/trustedDevice.ts` | `bridge/trusted_device.py` |
| `bridge/workSecret.ts` | `bridge/work_secret.py` |
| **buddy**（2） | |
| `buddy/companion.ts` | `buddy/companion.py` |
| `buddy/sprites.ts` | `buddy/sprites.py` |
| **cli**（8） | |
| `cli/exit.ts` | `cli_core/exit.py` |
| `cli/remoteIO.ts` | `transports/remote_io.py` |
| `cli/structuredIO.ts` | `cli_core/structured_io.py` |
| `cli/transports/HybridTransport.ts` | `transports/hybrid_transport.py` |
| `cli/transports/SerialBatchEventUploader.ts` | `transports/serial_batch_event_uploader.py` |
| `cli/transports/WorkerStateUploader.ts` | `transports/worker_state_uploader.py` |
| `cli/transports/ccrClient.ts` | `transports/ccr_client.py` |
| `cli/transports/transportUtils.ts` | `transports/transport_utils.py` |
| **commands**（17） | |
| `commands/brief.ts` | `tool_system/tools/brief.py` |
| `commands/clear/conversation.ts` | `agent/conversation.py` |
| `commands/compact/compact.ts` | `services/compact/compact.py` |
| `commands/effort/effort.tsx` | `utils/effort.py` |
| `commands/exit/exit.tsx` | `cli_core/exit.py` |
| `commands/init.ts` | `init.py` |
| `commands/memory/memory.tsx` | `tool_system/tools/memory.py` |
| `commands/permissions/permissions.tsx` | `services/swarm/permissions.py` |
| `commands/plan/plan.tsx` | `plan/plan.py` |
| `commands/release-notes/release-notes.ts` | `utils/release_notes.py` |
| `commands/remote-setup/api.ts` | `utils/teleport/api.py` |
| `commands/review.ts` | `memory/review.py` |
| `commands/security-review.ts` | `command_system/security_review.py` |
| `commands/session/session.tsx` | `agent/session.py` |
| `commands/statusline.tsx` | `command_system/statusline.py` |
| `commands/tasks/tasks.tsx` | `background/tasks.py` |
| `commands/theme/theme.tsx` | `utils/theme.py` |
| **commands.ts**（1） | |
| `commands.ts` | `permissions/bash_parser/commands.py` |
| **components**（3） | |
| `components/HelpV2/Commands.tsx` | `permissions/bash_parser/commands.py` |
| `components/Settings/Settings.tsx` | `settings/settings.py` |
| `components/TokenWarning.tsx` | `services/token_warning.py` |
| **constants**（3） | |
| `constants/oauth.ts` | `auth/oauth.py` |
| `constants/spinnerVerbs.ts` | `constants/spinner_verbs.py` |
| `constants/xml.ts` | `constants/xml.py` |
| **context**（1） | |
| `context/mailbox.tsx` | `services/swarm/mailbox.py` |
| **entrypoints**（2） | |
| `entrypoints/cli.tsx` | `cli.py` |
| `entrypoints/init.ts` | `init.py` |
| **history.ts**（1） | |
| `history.ts` | `history.py` |
| **ink**（4） | |
| `ink/selection.ts` | `services/ide/selection.py` |
| `ink/styles.ts` | `outputStyles/styles.py` |
| `ink/terminal.ts` | `query/terminal.py` |
| `ink/termio/parser.ts` | `permissions/bash_parser/parser.py` |
| **keybindings**（1） | |
| `keybindings/parser.ts` | `permissions/bash_parser/parser.py` |
| **memdir**（8） | |
| `memdir/findRelevantMemories.ts` | `memdir/find_relevant_memories.py` |
| `memdir/memdir.ts` | `memdir/memdir.py` |
| `memdir/memoryAge.ts` | `memdir/memory_age.py` |
| `memdir/memoryScan.ts` | `memdir/memory_scan.py` |
| `memdir/memoryTypes.ts` | `memdir/memory_types.py` |
| `memdir/paths.ts` | `memdir/paths.py` |
| `memdir/teamMemPaths.ts` | `memdir/team_mem_paths.py` |
| `memdir/teamMemPrompts.ts` | `memdir/team_mem_prompts.py` |
| **plugins**（1） | |
| `plugins/builtinPlugins.ts` | `plugins/builtin_plugins.py` |
| **query**（3） | |
| `query/deps.ts` | `query/deps.py` |
| `query/stopHooks.ts` | `query/stop_hooks.py` |
| `query/tokenBudget.ts` | `query/token_budget.py` |
| **query.ts**（1） | |
| `query.ts` | `query/query.py` |
| **remote**（2） | |
| `remote/RemoteSessionManager.ts` | `remote/remote_session_manager.py` |
| `remote/sdkMessageAdapter.ts` | `remote/sdk_message_adapter.py` |
| **server**（1） | |
| `server/directConnectManager.ts` | `server/direct_connect_manager.py` |
| **services**（22） | |
| `services/analytics/metadata.ts` | `services/analytics/metadata.py` |
| `services/analytics/sink.ts` | `services/analytics/sink.py` |
| `services/api/claude.ts` | `services/api/claude.py` |
| `services/api/logging.ts` | `services/api/logging.py` |
| `services/compact/compact.ts` | `services/compact/compact.py` |
| `services/compact/grouping.ts` | `services/compact/grouping.py` |
| `services/compact/postCompactCleanup.ts` | `services/compact/post_compact_cleanup.py` |
| `services/compact/sessionMemoryCompact.ts` | `services/compact/session_memory_compact.py` |
| `services/lsp/manager.ts` | `services/mcp/manager.py` |
| `services/mcp/InProcessTransport.ts` | `services/mcp/in_process_transport.py` |
| `services/mcp/channelPermissions.ts` | `services/mcp/channel_permissions.py` |
| `services/mcp/claudeai.ts` | `services/mcp/claudeai.py` |
| `services/mcp/envExpansion.ts` | `services/mcp/env_expansion.py` |
| `services/mcp/mcpStringUtils.ts` | `services/mcp/mcp_string_utils.py` |
| `services/mcp/normalization.ts` | `services/mcp/normalization.py` |
| `services/mcp/oauthPort.ts` | `services/mcp/oauth_port.py` |
| `services/mcp/officialRegistry.ts` | `services/mcp/official_registry.py` |
| `services/mcp/xaa.ts` | `services/mcp/xaa.py` |
| `services/mcp/xaaIdpLogin.ts` | `services/mcp/xaa_idp_login.py` |
| `services/tokenEstimation.ts` | `token_estimation.py` |
| `services/tools/toolExecution.ts` | `services/tool_execution/tool_execution.py` |
| `services/tools/toolHooks.ts` | `services/tool_execution/tool_hooks.py` |
| **setup.ts**（1） | |
| `setup.ts` | `permissions/setup.py` |
| **skills**（9） | |
| `skills/bundled/batch.ts` | `skills/bundled/batch.py` |
| `skills/bundled/debug.ts` | `skills/bundled/debug.py` |
| `skills/bundled/loop.ts` | `skills/bundled/loop.py` |
| `skills/bundled/simplify.ts` | `skills/bundled/simplify.py` |
| `skills/bundled/stuck.ts` | `skills/bundled/stuck.py` |
| `skills/bundled/updateConfig.ts` | `skills/bundled/update_config.py` |
| `skills/bundled/verifyContent.ts` | `skills/bundled/verify_content.py` |
| `skills/bundledSkills.ts` | `skills/bundled_skills.py` |
| `skills/mcpSkillBuilders.ts` | `skills/mcp_skill_builders.py` |
| **state**（1） | |
| `state/AppState.tsx` | `state/app_state.py` |
| **tasks**（2） | |
| `tasks/pillLabel.ts` | `tasks/pill_label.py` |
| `tasks/stopTask.ts` | `tasks/stop_task.py` |
| **tasks.ts**（1） | |
| `tasks.ts` | `background/tasks.py` |
| **tools**（12） | |
| `tools/AgentTool/agentToolUtils.ts` | `agent/agent_tool_utils.py` |
| `tools/AgentTool/forkSubagent.ts` | `agent/fork_subagent.py` |
| `tools/AgentTool/loadAgentsDir.ts` | `agent/load_agents_dir.py` |
| `tools/AgentTool/resumeAgent.ts` | `agent/resume_agent.py` |
| `tools/AgentTool/runAgent.ts` | `agent/run_agent.py` |
| `tools/BashTool/BashTool.tsx` | `tool_system/tools/bash/bash_tool.py` |
| `tools/BashTool/bashSecurity.ts` | `permissions/bash_security.py` |
| `tools/BashTool/commandSemantics.ts` | `tool_system/tools/bash/command_semantics.py` |
| `tools/BashTool/readOnlyValidation.ts` | `tool_system/tools/bash/read_only_validation.py` |
| `tools/FileReadTool/imageProcessor.ts` | `utils/image_processor.py` |
| `tools/PowerShellTool/commandSemantics.ts` | `tool_system/tools/bash/command_semantics.py` |
| `tools/PowerShellTool/readOnlyValidation.ts` | `tool_system/tools/bash/read_only_validation.py` |
| **types**（2） | |
| `types/command.ts` | `goals/command.py` |
| `types/permissions.ts` | `services/swarm/permissions.py` |
| **upstreamproxy**（1） | |
| `upstreamproxy/relay.ts` | `upstreamproxy/relay.py` |
| **utils**（73） | |
| `utils/abortController.ts` | `utils/abort_controller.py` |
| `utils/api.ts` | `utils/teleport/api.py` |
| `utils/apiPreconnect.ts` | `utils/api_preconnect.py` |
| `utils/aws.ts` | `auth/aws.py` |
| `utils/bash/commands.ts` | `permissions/bash_parser/commands.py` |
| `utils/bash/parser.ts` | `permissions/bash_parser/parser.py` |
| `utils/bash/shellQuote.ts` | `permissions/bash_parser/shell_quote.py` |
| `utils/bash/specs/sleep.ts` | `tool_system/tools/sleep.py` |
| `utils/claudeInChrome/setup.ts` | `permissions/setup.py` |
| `utils/combinedAbortSignal.ts` | `utils/combined_abort_signal.py` |
| `utils/computerUse/setup.ts` | `permissions/setup.py` |
| `utils/cron.ts` | `tool_system/tools/cron.py` |
| `utils/debug.ts` | `skills/bundled/debug.py` |
| `utils/dxt/helpers.ts` | `services/swarm/helpers.py` |
| `utils/effort.ts` | `utils/effort.py` |
| `utils/env.ts` | `utils/env.py` |
| `utils/exportRenderer.tsx` | `utils/export_renderer.py` |
| `utils/fastMode.ts` | `utils/fast_mode.py` |
| `utils/fileHistory.ts` | `utils/file_history.py` |
| `utils/fileStateCache.ts` | `utils/file_state_cache.py` |
| `utils/format.ts` | `utils/format.py` |
| `utils/git.ts` | `utils/git.py` |
| `utils/glob.ts` | `tool_system/tools/glob.py` |
| `utils/gracefulShutdown.ts` | `utils/graceful_shutdown.py` |
| `utils/hooks/execAgentHook.ts` | `hooks/exec_agent_hook.py` |
| `utils/hooks/execHttpHook.ts` | `hooks/exec_http_hook.py` |
| `utils/hooks/execPromptHook.ts` | `hooks/exec_prompt_hook.py` |
| `utils/hooks/postSamplingHooks.ts` | `hooks/post_sampling_hooks.py` |
| `utils/hooks/sessionHooks.ts` | `hooks/session_hooks.py` |
| `utils/hooks/ssrfGuard.ts` | `hooks/ssrf_guard.py` |
| `utils/imagePaste.ts` | `utils/image_paste.py` |
| `utils/imageValidation.ts` | `utils/image_validation.py` |
| `utils/lockfile.ts` | `server/lockfile.py` |
| `utils/mailbox.ts` | `services/swarm/mailbox.py` |
| `utils/markdownConfigLoader.ts` | `utils/markdown_config_loader.py` |
| `utils/messageQueueManager.ts` | `utils/message_queue_manager.py` |
| `utils/model/agent.ts` | `tool_system/tools/agent.py` |
| `utils/model/aliases.ts` | `models/aliases.py` |
| `utils/model/bedrock.ts` | `models/bedrock.py` |
| `utils/model/configs.ts` | `models/configs.py` |
| `utils/peerAddress.ts` | `utils/peer_address.py` |
| `utils/permissions/filesystem.ts` | `permissions/filesystem.py` |
| `utils/permissions/permissions.ts` | `services/swarm/permissions.py` |
| `utils/permissions/yoloClassifier.ts` | `permissions/yolo_classifier.py` |
| `utils/plans.ts` | `utils/plans.py` |
| `utils/plugins/loadPluginAgents.ts` | `agent/load_plugin_agents.py` |
| `utils/powershell/parser.ts` | `permissions/bash_parser/parser.py` |
| `utils/releaseNotes.ts` | `utils/release_notes.py` |
| `utils/ripgrep.ts` | `tool_system/utils/ripgrep.py` |
| `utils/sessionIngressAuth.ts` | `utils/session_ingress_auth.py` |
| `utils/sessionStart.ts` | `state/session_start.py` |
| `utils/sessionStorage.ts` | `services/session_storage.py` |
| `utils/sessionTitle.ts` | `services/session_title.py` |
| `utils/settings/changeDetector.ts` | `settings/change_detector.py` |
| `utils/settings/managedPath.ts` | `settings/managed_path.py` |
| `utils/settings/mdm/settings.ts` | `settings/settings.py` |
| `utils/settings/permissionValidation.ts` | `settings/permission_validation.py` |
| `utils/settings/settings.ts` | `settings/settings.py` |
| `utils/signal.ts` | `utils/signal.py` |
| `utils/sleep.ts` | `tool_system/tools/sleep.py` |
| `utils/startupProfiler.ts` | `utils/startup_profiler.py` |
| `utils/subprocessEnv.ts` | `utils/subprocess_env.py` |
| `utils/swarm/backends/detection.ts` | `services/voice/detection.py` |
| `utils/swarm/leaderPermissionBridge.ts` | `services/swarm/leader_permission_bridge.py` |
| `utils/tasks.ts` | `background/tasks.py` |
| `utils/teammate.ts` | `services/swarm/teammate.py` |
| `utils/telemetry/events.ts` | `services/analytics/events.py` |
| `utils/teleport/api.ts` | `utils/teleport/api.py` |
| `utils/terminal.ts` | `query/terminal.py` |
| `utils/theme.ts` | `utils/theme.py` |
| `utils/tokenBudget.ts` | `query/token_budget.py` |
| `utils/words.ts` | `utils/words.py` |
| `utils/xml.ts` | `constants/xml.py` |
| **vim**（1） | |
| `vim/transitions.ts` | `query/transitions.py` |

## 3. 多候选匹配摘要（UNVERIFIED，需逐条核实）

1. `bootstrap/state.ts` → `bootstrap/state.py`、`eco/state.py`
1. `bridge/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `buddy/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `buddy/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `cli/handlers/auth.ts` → `auth/auth.py`、`services/mcp/auth.py`
1. `cli/handlers/mcp.tsx` → `entrypoints/mcp.py`、`tool_system/tools/mcp.py`
1. `commands/add-dir/validation.ts` → `models/validation.py`、`settings/validation.py`
1. `commands/advisor.ts` → `tool_system/tools/advisor.py`、`utils/advisor.py`
1. `commands/config/config.tsx` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `commands/context/context.tsx` → `models/context.py`、`tool_system/context.py`
1. `commands/doctor/doctor.tsx` → `entrypoints/doctor.py`、`services/mcp/doctor.py`
1. `commands/mcp/mcp.tsx` → `entrypoints/mcp.py`、`tool_system/tools/mcp.py`
1. `commands/model/model.tsx` → `models/model.py`、`skills/model.py`
1. `components/ManagedSettingsSecurityDialog/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `components/Messages.tsx` → `compact_service/messages.py`、`types/messages.py`、`utils/messages.py`
1. `components/PromptInput/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `components/Settings/Config.tsx` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `components/Spinner/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `components/TrustDialog/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `components/agents/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `components/agents/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `components/messages/UserToolResultMessage/utils.tsx` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `components/permissions/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `constants/messages.ts` → `compact_service/messages.py`、`types/messages.py`、`utils/messages.py`
1. `context.ts` → `models/context.py`、`tool_system/context.py`
1. `cost-tracker.ts` → `cost_tracker.py`、`services/cost_tracker.py`
1. `entrypoints/mcp.ts` → `entrypoints/mcp.py`、`tool_system/tools/mcp.py`
1. `ink/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `ink/layout/engine.ts` → `command_system/engine.py`、`eco/engine.py`、`query/engine.py`
1. `ink/termio/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `query/config.ts` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `screens/Doctor.tsx` → `entrypoints/doctor.py`、`services/mcp/doctor.py`
1. `server/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `services/analytics/config.ts` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `services/api/client.ts` → `services/mcp/client.py`、`services/oauth/client.py`
1. `services/api/errors.ts` → `services/api/errors.py`、`services/mcp/errors.py`、`tool_system/errors.py`、`workflow/errors.py`
1. `services/autoDream/config.ts` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `services/compact/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `services/lsp/config.ts` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `services/mcp/auth.ts` → `auth/auth.py`、`services/mcp/auth.py`
1. `services/mcp/client.ts` → `services/mcp/client.py`、`services/oauth/client.py`
1. `services/mcp/config.ts` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `services/mcp/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `services/mcp/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `services/oauth/client.ts` → `services/mcp/client.py`、`services/oauth/client.py`
1. `services/policyLimits/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `services/remoteManagedSettings/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `services/settingsSync/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `services/teamMemorySync/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `state/store.ts` → `memory/store.py`、`utils/store.py`
1. `tasks/InProcessTeammateTask/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `tasks/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `tools/AgentTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/AgentTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/AskUserQuestionTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/BashTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/BashTool/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `tools/BriefTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/ConfigTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/ConfigTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/EnterPlanModeTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/EnterPlanModeTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/EnterWorktreeTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/EnterWorktreeTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/ExitPlanModeTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/ExitPlanModeTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/ExitWorktreeTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/ExitWorktreeTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/FileEditTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/FileEditTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/FileEditTool/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `tools/FileEditTool/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `tools/FileReadTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/FileWriteTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/GlobTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/GrepTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/LSPTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/ListMcpResourcesTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/MCPTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/NotebookEditTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/NotebookEditTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/PowerShellTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/REPLTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/ReadMcpResourceTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/RemoteTriggerTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/ScheduleCronTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/SendMessageTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/SendMessageTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/SkillTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/SkillTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/SleepTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TaskCreateTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TaskCreateTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TaskGetTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TaskGetTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TaskListTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TaskListTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TaskOutputTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TaskStopTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TaskUpdateTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TaskUpdateTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TeamCreateTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TeamCreateTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TeamDeleteTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TeamDeleteTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/TodoWriteTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/TodoWriteTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/ToolSearchTool/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `tools/ToolSearchTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/WebFetchTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/WebFetchTool/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `tools/WebSearchTool/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `tools/utils.ts` → `tool_system/tools/bash/utils.py`、`wiki/utils.py`
1. `types/generated/events_mono/common/v1/auth.ts` → `auth/auth.py`、`services/mcp/auth.py`
1. `utils/advisor.ts` → `tool_system/tools/advisor.py`、`utils/advisor.py`
1. `utils/argumentSubstitution.ts` → `command_system/argument_substitution.py`、`skills/argument_substitution.py`
1. `utils/auth.ts` → `auth/auth.py`、`services/mcp/auth.py`
1. `utils/bash/registry.ts` → `command_system/registry.py`、`hooks/registry.py`、`tool_system/registry.py`
1. `utils/claudeInChrome/prompt.ts` → `agent/prompt.py`、`buddy/prompt.py`、`coordinator/prompt.py`、`services/compact/prompt.py`、`tool_system/tools/bash/prompt.py`
1. `utils/config.ts` → `config.py`、`query/config.py`、`services/autofix/config.py`、`services/mcp/config.py`、`tool_system/tools/config.py`
1. `utils/context.ts` → `models/context.py`、`tool_system/context.py`
1. `utils/errors.ts` → `services/api/errors.py`、`services/mcp/errors.py`、`tool_system/errors.py`、`workflow/errors.py`
1. `utils/memory/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `utils/messages.ts` → `compact_service/messages.py`、`types/messages.py`、`utils/messages.py`
1. `utils/model/model.ts` → `models/model.py`、`skills/model.py`
1. `utils/settings/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `utils/settings/mdm/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `utils/settings/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `utils/settings/validation.ts` → `models/validation.py`、`settings/validation.py`
1. `utils/swarm/backends/registry.ts` → `command_system/registry.py`、`hooks/registry.py`、`tool_system/registry.py`
1. `utils/swarm/backends/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `utils/swarm/constants.ts` → `agent/constants.py`、`settings/constants.py`、`workflow/constants.py`
1. `utils/todo/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`
1. `utils/toolSearch.ts` → `tool_system/tool_search.py`、`tool_system/tools/tool_search.py`
1. `utils/worktree.ts` → `bridge/worktree.py`、`tool_system/tools/worktree.py`、`workflow/worktree.py`
1. `vim/types.ts` → `bridge/types.py`、`buddy/types.py`、`command_system/types.py`、`permissions/types.py`、`plugins/types.py`、`server/types.py`、`services/ide/types.py`、`services/mcp/types.py`、`settings/types.py`、`workflow/types.py`

## 4. 未确认项

1. ☐ 1:1 匹配的 symbol 级语义（类/函数/行为）尚未逐条对照，STRUCTURAL_VERIFIED 仅证明文件级存在对应
2. ☐ 多候选匹配需人工判断正确落点（如 prompt.ts → 5 个候选）
3. ☐ 无匹配文件的 reference 侧语义归属（可能落在 python 合并文件内）待 symbol 级定位
4. ☐ 本表与 10 文档模块总表的映射状态联动更新
