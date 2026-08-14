"""Windows Job Object 进程树包含 launcher（B6 Wave F5 — Windows 最低隔离）。

Reference Mapping
-----------------
REF Source:
    utils/sandbox/sandbox-adapter.ts（外部 sandbox runtime）
REF Behavior:
    命令在真实 OS 沙箱内执行；隔离范围与 capability 必须真实。
PY Owner:
    src/execution/win_job_launcher.py::run_argv_in_job
PY Behavior:
    用 Job Object（``KILL_ON_JOB_CLOSE``）提供 Windows 进程树包含；父进程退出
    即结束整棵进程树；非 win32 平台 fail-closed。
Known Differences:
    Windows 无文件系统/网络沙箱，仅进程树包含；工作区边界与 secret scrub 由
    执行层策略保证。
Reason:
    OS_PLATFORM_ADAPTATION + PRODUCT_SCOPE_SIMPLIFICATION
Functional Status:
    LIMITED（win32 上可用；其他平台 fail-closed，见 DIFF-SANDBOX-001）

Windows 上通过 Job Object 实现进程树包含：子进程在挂接 ``KILL_ON_JOB_CLOSE``
的作业对象内启动，父进程（本 launcher）退出时整棵进程树被系统强制结束，避免
超时/中断后后台孙进程脱离监管继续执行。这是 Windows 的最低隔离能力 —— 它提供
进程树包含，不提供文件系统/网络沙箱；工作区路径边界与 secret scrub 由执行层
策略保证（见 ``SandboxPolicy`` / ``bash_env``）。

本模块只在 ``sys.platform == "win32"`` 时真正运行；在其他平台被调用时返回明确
错误（fail-closed），不得悄悄退回普通进程执行。

ctypes 布局遵循 MSDN 文档：
- ``JOBOBJECT_EXTENDED_LIMIT_INFORMATION``（Job 级别 9）
- ``THREADENTRY32``（CreateToolhelp32Snapshot 的线程枚举，用于恢复被挂起的
  主线程，因为 ``subprocess`` 不暴露线程句柄）

用法（由 ``sandbox_command_argv`` 生成）::

    python -m src.execution.win_job_launcher -- <command> [args...]
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass

#: JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE — 作业句柄关闭时结束作业内所有进程。
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
#: JobObjectExtendedLimitInformation
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
#: TH32CS_SNAPTHREAD
TH32CS_SNAPTHREAD = 0x00000004
#: 进程/线程访问权限
PROCESS_SET_QUOTA = 0x0100
PROCESS_TERMINATE = 0x0001
THREAD_SUSPEND_RESUME = 0x0002
#: CREATE_SUSPENDED | CREATE_NEW_PROCESS_GROUP | CREATE_UNICODE_ENVIRONMENT
CREATE_SUSPENDED = 0x00000004
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_UNICODE_ENVIRONMENT = 0x00000400


@dataclass(frozen=True)
class JobRunResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    termination_reason: str = ""


def _win32() -> bool:
    return sys.platform == "win32"


def _job_object_argv(argv: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """构造经 ``-m`` launcher 包装的 argv（在非 Windows 上仅用于结构验证）。"""
    return (
        sys.executable,
        "-m",
        "src.execution.win_job_launcher",
        "--",
        *argv,
    )


def _create_job(ctypes, wintypes) -> object:
    """创建挂接 ``KILL_ON_JOB_CLOSE`` 的作业对象，返回其 HANDLE。"""
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateJobObjectW(None, None)
    if not handle:
        raise OSError("CreateJobObjectW failed")

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
            ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", wintypes.ULONGLONG),
            ("WriteOperationCount", wintypes.ULONGLONG),
            ("OtherOperationCount", wintypes.ULONGLONG),
            ("ReadTransferCount", wintypes.ULONGLONG),
            ("WriteTransferCount", wintypes.ULONGLONG),
            ("OtherTransferCount", wintypes.ULONGLONG),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    ok = kernel32.SetInformationJobObject(
        handle,
        JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(info),
        ctypes.sizeof(info),
    )
    if not ok:
        kernel32.CloseHandle(handle)
        raise OSError("SetInformationJobObject failed")
    return handle


def _assign_process_to_job(ctypes, wintypes, job_handle: int, pid: int) -> None:
    kernel32 = ctypes.windll.kernel32
    process_handle = kernel32.OpenProcess(
        PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, pid
    )
    if not process_handle:
        raise OSError("OpenProcess failed")
    try:
        if not kernel32.AssignProcessToJobObject(job_handle, process_handle):
            raise OSError("AssignProcessToJobObject failed")
    finally:
        kernel32.CloseHandle(process_handle)


def _resume_first_thread(ctypes, wintypes, pid: int) -> None:
    """恢复目标进程的第一个线程（CREATE_SUSPENDED 后线程处于挂起状态）。"""
    kernel32 = ctypes.windll.kernel32
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snapshot == -1:  # INVALID_HANDLE_VALUE
        raise OSError("CreateToolhelp32Snapshot failed")

    class THREADENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD),
            ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", wintypes.LONG),
            ("tpDeltaPri", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
        ]

    try:
        entry = THREADENTRY32()
        entry.dwSize = ctypes.sizeof(THREADENTRY32)
        if not kernel32.Thread32First(snapshot, ctypes.byref(entry)):
            raise OSError("Thread32First failed")
        while True:
            if entry.th32OwnerProcessID == pid:
                thread_handle = kernel32.OpenThread(
                    THREAD_SUSPEND_RESUME, False, entry.th32ThreadID
                )
                if thread_handle:
                    try:
                        kernel32.ResumeThread(thread_handle)
                    finally:
                        kernel32.CloseHandle(thread_handle)
                return
            if not kernel32.Thread32Next(snapshot, ctypes.byref(entry)):
                raise OSError("target process thread not found")
    finally:
        kernel32.CloseHandle(snapshot)


def run_argv_in_job(
    argv: tuple[str, ...] | list[str],
    *,
    cwd: str,
    env: dict[str, str] | None = None,
    timeout_s: int | float | None = None,
) -> JobRunResult:
    """在 ``KILL_ON_JOB_CLOSE`` Job Object 内运行 ``argv`` 并等待结束。

    非 Windows 平台直接返回 fail-closed 错误 —— 绝不静默退化成无作业执行。
    """
    if not _win32():
        return JobRunResult(
            exit_code=126,
            stderr="windows-job-object launcher requires win32",
            termination_reason="refused on non-Windows platform",
        )

    import ctypes
    from ctypes import wintypes

    job_handle = _create_job(ctypes, wintypes)
    process = None
    try:
        process = subprocess.Popen(
            list(argv),
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=(
                CREATE_SUSPENDED | CREATE_NEW_PROCESS_GROUP | CREATE_UNICODE_ENVIRONMENT
            ),
        )
        _assign_process_to_job(ctypes, wintypes, job_handle, process.pid)
        _resume_first_thread(ctypes, wintypes, process.pid)

        try:
            stdout, stderr = process.communicate(timeout=timeout_s)
            return JobRunResult(
                exit_code=process.returncode or 0,
                stdout=stdout or "",
                stderr=stderr or "",
            )
        except subprocess.TimeoutExpired:
            # 关闭作业句柄 → KILL_ON_JOB_CLOSE 结束整棵进程树（含孙进程）。
            ctypes.windll.kernel32.TerminateJobObject(job_handle, 124)
            try:
                stdout, stderr = process.communicate(timeout=0.5)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            return JobRunResult(
                exit_code=124,
                stdout=stdout or "",
                stderr=stderr or "command timed out",
                timed_out=True,
                termination_reason="timeout: job object terminated process tree",
            )
    finally:
        if process is not None and process.poll() is None:
            try:
                process.kill()
            except Exception:  # noqa: BLE001
                pass
        if _win32():
            import ctypes

            if job_handle:
                ctypes.windll.kernel32.CloseHandle(job_handle)


if __name__ == "__main__":  # pragma: no cover - exercised only on win32
    if "--" not in sys.argv:
        print("usage: python -m src.execution.win_job_launcher -- <command> ...", file=sys.stderr)
        sys.exit(2)
    index = sys.argv.index("--")
    command = tuple(sys.argv[index + 1 :])
    if not command:
        sys.exit(2)
    result = run_argv_in_job(command, cwd=os.getcwd())
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    sys.exit(result.exit_code)
