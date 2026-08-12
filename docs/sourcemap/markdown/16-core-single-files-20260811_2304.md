# core-single-files 源码盘点
> 编号: 16
> 时间戳: 20260811_2304
> 基线: def709361a86
> Reference: Claude Code 2.1.88 @ a8a678cb6244
> 类型: group（core 单文件组）
> 盘点状态: INVENTORY_COMPLETE
> 映射状态: UNVERIFIED（启发式初版，待逐项核实）

## 1. 模块概况

1. 模块名: core-single-files
2. 类型: group（core 单文件组）
3. Python 文件数: 13
4. 总行数: 3343
5. 依赖的 src 内部模块: cost_tracker, tasks_core
6. 一句话职责: UNKNOWN（待人工核实）

## 2. 文件清单

1. `cli.py` — 1014 行（类 0，函数 15）
1. `config.py` — 550 行（类 1，函数 28）
1. `costHook.py` — 8 行（类 0，函数 1）
1. `cost_tracker.py` — 126 行（类 1，函数 1）
1. `deferred_init.py` — 133 行（类 1，函数 3）
1. `history.py` — 22 行（类 2，函数 0）
1. `init.py` — 217 行（类 0，函数 7）
1. `prefetch.py` — 244 行（类 1，函数 8）
1. `projectOnboardingState.py` — 10 行（类 1，函数 0）
1. `secret_store.py` — 142 行（类 0，函数 6）
1. `task_registry.py` — 225 行（类 2，函数 3）
1. `tasks_core.py` — 168 行（类 1，函数 3）
1. `token_estimation.py` — 484 行（类 1，函数 28）

## 3. 关键符号

1. 文件 `cli.py`
1. 函数 main — L28
1. 函数 _maybe_create_worktree — L254
1. 函数 _gate_folder_trust — L283
1. 函数 _run_tui_subcommand — L307
1. 函数 _prompt_folder_trust — L352
1. 函数 _build_parser — L393
1. 函数 _resolve_permission_state — L584
1. 函数 _run_print_mode — L653
1. 函数 _split_csv — L718
1. 函数 _show_provider_defaults_table — L724
1. 函数 handle_login — L748
1. 函数 _handle_anthropic_subscription_login — L819
1. 函数 _handle_openai_subscription_login — L856
1. 函数 handle_logout — L930
1. 函数 show_config — L952
1. 文件 `config.py`
1. 类 ConfigManager — L209
1. 函数 _find_git_root — L38
1. 函数 get_global_config_path — L55
1. 函数 get_project_config_path — L59
1. 函数 get_local_config_path — L66
1. 函数 _deep_merge — L77
1. 函数 _read_json — L92
1. 函数 _atomic_write_json — L111
1. 函数 get_default_config — L134
1. 函数 _session_trusted — L166
1. 函数 _strip_untrusted_keys — L196
1. 函数 _global_config_file — L316
1. 函数 normalize_path_for_config_key — L322
1. 函数 get_project_path_for_config — L328
1. 函数 get_project_entry — L338
1. 函数 update_project_entry — L349
1. 函数 append_history_entry — L387
1. 函数 read_history_entries — L395
1. 函数 _get_default_manager — L421
1. 函数 get_config_path — L428
1. 函数 load_config — L433
1. 函数 save_config — L438
1. 函数 get_provider_config — L443
1. 函数 set_api_key — L467
1. 函数 set_default_provider — L488
1. 函数 get_default_provider — L496
1. 函数 set_theme — L501
1. 函数 set_logo_color — L513
1. 函数 set_effort — L525
1. 文件 `costHook.py`
1. 函数 apply_cost_hook — L6
1. 文件 `cost_tracker.py`
1. 类 CostTracker — L87
1. 函数 record_api_usage — L32
1. 文件 `deferred_init.py`
1. 类 DeferredPrefetchHandle — L44
1. 函数 _system_context_allowed — L57
1. 函数 _warm — L72
1. 函数 start_deferred_prefetches — L93
1. 文件 `history.py`
1. 类 HistoryEvent — L7
1. 类 HistoryLog — L13
1. 文件 `init.py`
1. 函数 init — L63
1. 函数 _placeholder_initialize_remote_managed_settings — L115
1. 函数 _placeholder_initialize_policy_limits — L119
1. 函数 run_pre_action — L123
1. 函数 _determine_is_interactive — L176
1. 函数 _determine_client_type — L198
1. 函数 reset_init_for_test_only — L206
1. 文件 `prefetch.py`
1. 类 PrefetchHandle — L40
1. 函数 _register_atexit_drain — L87
1. 函数 start_keychain_prefetch — L112
1. 函数 get_or_start_keychain_prefetch — L145
1. 函数 wait_and_read_keychain — L164
1. 函数 start_mdm_raw_read — L186
1. 函数 get_or_start_mdm_raw_read — L212
1. 函数 wait_and_read_mdm — L223
1. 函数 start_project_scan — L238
1. 文件 `projectOnboardingState.py`
1. 类 ProjectOnboardingState — L7
1. 文件 `secret_store.py`
1. 函数 _coerce_env_map — L46
1. 函数 _config_env — L66
1. 函数 get_secret — L83
1. 函数 list_secret_names — L98
1. 函数 set_secret — L103
1. 函数 delete_secret — L125
1. 文件 `task_registry.py`
1. 类 Task — L45
1. 类 RuntimeTaskRegistry — L72
1. 函数 register_task — L190
1. 函数 get_all_tasks — L202
1. 函数 get_task_by_type — L211
1. 文件 `tasks_core.py`
1. 类 TaskStateBase — L105
1. 函数 is_terminal_task_status — L52
1. 函数 generate_task_id — L85
1. 函数 create_task_state_base — L140
1. 文件 `token_estimation.py`
1. 类 _TokenCountCache — L56
1. 函数 _load_tiktoken — L32
1. 函数 _get_encoder — L40
1. 函数 get_token_cache_stats — L128
1. 函数 reset_token_cache — L144
1. 函数 count_tokens — L150
1. 函数 rough_token_count_estimation — L169
1. 函数 bytes_per_token_for_file_type — L173
1. 函数 rough_token_count_estimation_for_file_type — L179
1. 函数 rough_token_count_estimation_for_messages — L187
1. 函数 rough_token_count_estimation_for_message — L196
1. 函数 rough_token_count_estimation_for_content — L216
1. 函数 _block_cache_key — L229
1. 函数 _rough_token_count_estimation_for_block_impl — L258
1. 函数 rough_token_count_estimation_for_block — L291
1. 函数 count_messages_tokens — L303
1. 函数 count_tokens_with_api — L335
1. 函数 count_messages_tokens_with_api — L343
1. 函数 _get_type — L370
1. 函数 _get_content — L376
1. 函数 _get_block_type — L388
1. 函数 _json_stringify — L394
1. 函数 _estimate_attachment_tokens — L401
1. 函数 estimate_tool_schema_tokens — L418
1. 函数 estimate_system_prompt_tokens — L428
1. 函数 estimate_system_prompt_sections_tokens — L433
1. 函数 estimate_image_tokens — L438
1. 函数 estimate_cache_aware_tokens — L451
1. 函数 rough_token_count_estimation_per_block_type — L475

## 4. 依赖与调用边（import 级）

1. cli.py → import __future__（外部）
1. cli.py → import argparse（外部）
1. cli.py → import os（外部）
1. cli.py → import sys（外部）
1. cli.py → import pathlib（外部）
1. cli.py → import src（外部）
1. config.py → import __future__（外部）
1. config.py → import json（外部）
1. config.py → import logging（外部）
1. config.py → import os（外部）
1. config.py → import subprocess（外部）
1. config.py → import tempfile（外部）
1. config.py → import time（外部）
1. config.py → import dataclasses（外部）
1. config.py → import pathlib（外部）
1. config.py → import typing（外部）
1. costHook.py → import __future__（外部）
1. costHook.py → import cost_tracker（内部）
1. cost_tracker.py → import __future__（外部）
1. cost_tracker.py → import dataclasses（外部）
1. cost_tracker.py → import typing（外部）
1. cost_tracker.py → import src（外部）
1. deferred_init.py → import __future__（外部）
1. deferred_init.py → import asyncio（外部）
1. deferred_init.py → import logging（外部）
1. deferred_init.py → import threading（外部）
1. deferred_init.py → import dataclasses（外部）
1. history.py → import __future__（外部）
1. history.py → import dataclasses（外部）
1. init.py → import __future__（外部）
1. init.py → import logging（外部）
1. init.py → import os（外部）
1. init.py → import sys（外部）
1. init.py → import functools（外部）
1. init.py → import src（外部）
1. prefetch.py → import __future__（外部）
1. prefetch.py → import atexit（外部）
1. prefetch.py → import subprocess（外部）
1. prefetch.py → import sys（外部）
1. prefetch.py → import threading（外部）
1. prefetch.py → import dataclasses（外部）
1. prefetch.py → import pathlib（外部）
1. projectOnboardingState.py → import __future__（外部）
1. projectOnboardingState.py → import dataclasses（外部）
1. secret_store.py → import __future__（外部）
1. secret_store.py → import logging（外部）
1. secret_store.py → import os（外部）
1. secret_store.py → import typing（外部）
1. task_registry.py → import __future__（外部）
1. task_registry.py → import inspect（外部）
1. task_registry.py → import threading（外部）
1. task_registry.py → import typing（外部）
1. task_registry.py → import tasks_core（内部）
1. tasks_core.py → import __future__（外部）
1. tasks_core.py → import secrets（外部）
1. tasks_core.py → import time（外部）
1. tasks_core.py → import dataclasses（外部）
1. tasks_core.py → import typing（外部）
1. token_estimation.py → import __future__（外部）
1. token_estimation.py → import json（外部）
1. token_estimation.py → import logging（外部）
1. token_estimation.py → import collections（外部）
1. token_estimation.py → import typing（外部）

## 5. R7/R5/CCR-14 映射（启发式初版）

1. R7-02 Interfaces — 候选（启发式），状态 UNVERIFIED
1. R5-01 Surface Layer — 候选（启发式），状态 UNVERIFIED
1. CCR-14 Runtime Config / Feature Gate Control Plane — 候选（启发式），状态 UNVERIFIED

## 6. 文件级映射细分

1. `cli.py` → R7-02, R5-01（UNVERIFIED）
1. `config.py` → CCR-14（UNVERIFIED）
1. `costHook.py` → CCR-01（UNVERIFIED）
1. `cost_tracker.py` → CCR-09（UNVERIFIED）
1. `deferred_init.py` → CCR-14（UNVERIFIED）
1. `history.py` → CCR-10（UNVERIFIED）
1. `init.py` → R7-03, R5-02（UNVERIFIED）
1. `prefetch.py` → CCR-07（UNVERIFIED）
1. `projectOnboardingState.py` → CCR-14（UNVERIFIED）
1. `secret_store.py` → CCR-13（UNVERIFIED）
1. `task_registry.py` → CCR-06（UNVERIFIED）
1. `tasks_core.py` → CCR-06（UNVERIFIED）
1. `token_estimation.py` → CCR-03（UNVERIFIED）

## 7. 未确认项与待核实项

1. ☐ 模块一句话职责待人工核实
1. ☐ reference 侧对应文件/symbol 映射待核实
1. ☐ 关键 call-edge/state-edge 待逐条对照 reference source
1. ☐ 本模块 R7/R5/CCR 归属的 UNVERIFIED 状态待升级或降级
