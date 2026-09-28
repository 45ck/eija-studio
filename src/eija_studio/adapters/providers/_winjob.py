"""Windows Job Object: every process started under the job dies with it (``KILL_ON_JOB_CLOSE``).

Why: on Windows a child that is reparented when its parent exits cannot be found by walking the process tree,
and a parent that exits within milliseconds can leave a grandchild no periodic scan has seen yet. A job
follows descendants by membership, not by parentage, so nothing that started after the job was attached can
escape it. Off Windows ``attach`` returns None and the caller relies on the POSIX process group instead.

Not established: a process that spawned a child in the few microseconds between ``Popen`` returning and
``attach`` running is not in the job. The descendant scan in process.py covers that gap.
"""
from __future__ import annotations

import contextlib
import ctypes
import sys
from ctypes import wintypes
from typing import Any

_KILL_ON_JOB_CLOSE = 0x2000
_EXTENDED_LIMIT_INFORMATION = 9
_PROCESS_SET_QUOTA = 0x0100
_PROCESS_TERMINATE = 0x0001


class _BasicLimits(ctypes.Structure):
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


class _IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimits),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class JobObject:
    """Owns one job handle. ``terminate`` kills every member now; ``close`` does so too (kill-on-close)."""

    def __init__(self, kernel32: Any, handle: Any) -> None:
        self._kernel32, self._handle = kernel32, handle

    def terminate(self) -> None:
        if self._handle:
            self._kernel32.TerminateJobObject(self._handle, 1)

    def close(self) -> None:
        if self._handle:
            self._kernel32.CloseHandle(self._handle)
            self._handle = None


if sys.platform == "win32":

    def _kernel32() -> Any:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
        kernel.SetInformationJobObject.restype = wintypes.BOOL
        kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel.TerminateJobObject.restype = wintypes.BOOL
        kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        kernel.CloseHandle.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        return kernel

    def _arm_kill_on_close(kernel: Any, job: Any) -> bool:
        limits = _ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = _KILL_ON_JOB_CLOSE
        return bool(kernel.SetInformationJobObject(job, _EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits)))

    def _assign(kernel: Any, job: Any, pid: int) -> bool:
        process = kernel.OpenProcess(_PROCESS_SET_QUOTA | _PROCESS_TERMINATE, False, pid)
        if not process:
            return False
        try:
            return bool(kernel.AssignProcessToJobObject(job, process))
        finally:
            kernel.CloseHandle(process)

    def attach(pid: int) -> JobObject | None:
        """Put ``pid`` in a new kill-on-close job. None when Windows refuses (best effort, never raises)."""
        with contextlib.suppress(OSError, AttributeError):
            kernel = _kernel32()
            job = kernel.CreateJobObjectW(None, None)
            if job:
                if _arm_kill_on_close(kernel, job) and _assign(kernel, job, pid):
                    return JobObject(kernel, job)
                kernel.CloseHandle(job)
        return None

else:

    def attach(pid: int) -> JobObject | None:
        return None
