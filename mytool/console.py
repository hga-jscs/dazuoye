from __future__ import annotations

import sys


def debug_print(message: str, *, enabled: bool) -> None:
    """统一调试输出格式，便于可视化排查。"""

    if enabled:
        print(f"[DEBUG] {message}")


def info_print(message: str) -> None:
    """普通信息输出。"""

    print(f"[INFO] {message}")


def warn_print(message: str) -> None:
    """警告输出。"""

    print(f"[WARN] {message}", file=sys.stderr)


def error_print(message: str) -> None:
    """错误输出。"""

    print(f"[ERROR] {message}", file=sys.stderr)
