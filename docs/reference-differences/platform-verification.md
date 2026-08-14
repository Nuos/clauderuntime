# 平台真机验证追踪（B6 — Platform Verification Ledger）

> 文档编号：`CR-B6-PLATFORM-VERIFICATION-LEDGER`
> 创建日期：`2026-08-14`
> 关联台账：`docs/reference-differences/registry.yaml`（DIFF-SANDBOX-001）
> 状态词：`PENDING_REAL_DEVICE`（待真机验证）/ `VERIFIED`（已真机验证）/ `BLOCKED`（环境无法验证）

## 目的

B6 验收清单 D 节要求“macOS execution boundary smoke / Linux capability / Windows
capability 说明真实”。本机为 macOS 开发环境，且该环境的受管终端阻止
`sandbox-exec` 应用沙箱规则。因此以下平台隔离路径**只有代码路径 + 单元测试 +
能力披露**，真实进程级隔离必须在对应平台真机/容器上验证。本账本逐项登记，
禁止把“代码已写”写成“平台已验证”，禁止谎报 `provides_isolation`。

---

## 1. Windows Job Object 进程树包含（`src/execution/win_job_launcher.py`）

| 字段 | 内容 |
|---|---|
| 代码路径 | `src/execution/win_job_launcher.py::run_argv_in_job`；`WindowsSandboxBackend.run`；`sandbox_command_argv` 的 `windows-job-object` 分支 |
| 实现依据 | MSDN `CreateJobObjectW` / `SetInformationJobObject(JobObjectExtendedLimitInformation, JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)` / `AssignProcessToJobObject` / `CreateToolhelp32Snapshot` + `ResumeThread` |
| 已验证（macOS 上） | capability 上报（非 win32 → available=False）、`prepare` 在 `require_isolation` 下 fail-closed、argv 包装形状、非 win32 调用 `run_argv_in_job` 返回 126 —— `tests/test_b6_linux_windows_sandbox.py` |
| **待真机验证** | ① ctypes 结构体布局与 64 位对齐是否符合 MSDN 实际布局；② `CreateProcessW(CREATE_SUSPENDED)` 后 `_resume_first_thread` 是否能恢复主线程；③ `KILL_ON_JOB_CLOSE` 在父进程退出/超时时是否真正结束整棵进程树（含孙进程） |
| 验证方法 | 在 Windows 主机/CI runner 执行：`.venv/Scripts/python.exe -m src.execution.win_job_launcher -- cmd /c "echo ok & start /b timeout 5"`，确认返回、超时后 `tasklist` 无残留；再跑 `pytest tests/test_b6_linux_windows_sandbox.py` |
| 状态 | `PENDING_REAL_DEVICE` |
| 风险 | ctypes 布局/句柄权限若与实际不符，Job Object 挂接会静默失败 → 必须真机验证后才能真正声明 Windows 隔离可用；在验证通过前 Windows 一律按 fail-closed 处理 |

## 2. Linux bubblewrap 容器执行（`LinuxSandboxBackend`）

| 字段 | 内容 |
|---|---|
| 代码路径 | `src/execution/sandbox.py::LinuxSandboxBackend`（`_probe` / `_wrap_argv` / `prepare` / `run`）；`sandbox_command_argv` 的 `linux-bubblewrap` 分支 |
| 实现依据 | bubblewrap 参数：`--die-with-parent --ro-bind / / --dev /dev --proc /proc --tmpfs /tmp --bind <cwd> <cwd> [--unshare-net]` |
| 已验证（macOS 上） | 平台守卫（非 linux → unavailable）、`prepare` fail-closed / isolated 分支、`_wrap_argv` 参数结构（只读根/可写 cwd/默认断网/允许网络时去 `--unshare-net`）—— `tests/test_b6_linux_windows_sandbox.py` |
| **待真机验证** | ① 目标 Linux 主机是否具备 `bwrap` 与用户命名空间（`--ro-bind / /` 需要）；② 容器内解释器/动态库/目标程序能否启动；③ 写入是否被限制在工作目录；④ 断网是否生效 |
| 验证方法 | 在 Linux 主机执行：`bwrap --version`；再跑 `pytest tests/test_b6_linux_windows_sandbox.py -k linux` 与一个真实 sandboxed Bash smoke（`echo hi` 经 `_bash_call` 沙箱路径） |
| 状态 | `PENDING_REAL_DEVICE` |
| 风险 | 探测会如实返回不可用并 fail-closed；不存在“谎报已沙箱”风险 |

## 3. macOS Seatbelt 在本环境的限制

| 字段 | 内容 |
|---|---|
| 代码路径 | `MacOSSandboxBackend`（已有，本轮未改其逻辑，仅加进程内探测缓存） |
| 本环境实测 | `_probe` 返回 `sandbox-exec: sandbox_apply: Operation not permitted` —— 受管终端禁止应用沙箱规则，因此本机 `provides_isolation=False`，相关测试按 fail-closed 行为断言 |
| 真机/普通终端验证 | 在普通 macOS 终端执行 `sandbox-exec -p '(version 1) (allow default)' /usr/bin/true`，成功即 Seatbelt 可用；随后 `tests/test_phase_c_exit_gate.py` 等真实沙箱用例应通过 |
| 状态 | 代码路径 `VERIFIED`（结构）；本环境能力探测 `BLOCKED`（环境限制，非代码缺陷） |

## 4. 其余平台的 Surface smoke

| 面 | 验证方式 | 状态 |
|---|---|---|
| Server（WebSocket 真实链路） | `tests/test_b6_surface_smoke.py`（启动/回答/Read/权限/中断/续谈） | `VERIFIED`（本机全绿） |
| CLI（headless 核心） | `tests/test_b6_surface_smoke.py` CLI 两项 | `VERIFIED`（本机全绿） |
| TUI | `ui-tui` 自有套件（文档基线 1692 passed） | 由 ui-tui 套件覆盖 |
| Desktop | server 端 gateway（`tests/server` 系列） | 由 server 套件覆盖 |

---

## 关闭条件（何时可把 `PENDING_REAL_DEVICE` 改为 `VERIFIED`）

1. 在对应平台真机/容器/CI runner 上执行“验证方法”列的步骤并记录输出；
2. 更新本账本状态并附上执行日期与运行环境；
3. 更新 `docs/reference-differences/registry.yaml` 中 DIFF-SANDBOX-001 的 notes；
4. 在 progress 文档“剩余功能缺口”中移除对应条目。

## 红线

- `PENDING_REAL_DEVICE` 期间不得在文档中写“Windows/Linux 隔离已验证”；
- Windows `provides_isolation` 在真机验证前保持 fail-closed 语义；
- GitHub CI 结果必须与 local 分开记录，不得写 `current-head GitHub CI green`。
