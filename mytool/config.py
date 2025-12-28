from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from mytool.console import debug_print, error_print, warn_print


@dataclass
class PlusConfig:
    """可选配置（来自 plusconfig.json）。"""

    use_all_wires: bool = False
    allow_disconnected: bool = False
    verbose_debug: bool = True


def load_plus_config(path: Path) -> PlusConfig:
    """读取 plusconfig.json，文件不存在则使用默认配置。"""

    config = PlusConfig()
    if not path.exists():
        return config

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - 输出需友好
        warn_print(f"解析 plusconfig 失败: {exc}，使用默认配置。")
        return config

    if not isinstance(data, dict):
        warn_print("plusconfig.json 内容不是对象，使用默认配置。")
        return config

    config.use_all_wires = bool(data.get("use_all_wires", config.use_all_wires))
    config.allow_disconnected = bool(data.get("allow_disconnected", config.allow_disconnected))
    config.verbose_debug = bool(data.get("verbose_debug", config.verbose_debug))
    return config


def resolve_config_path(input_path: Path) -> Path:
    """查找 plusconfig.json 配置文件路径。"""

    if input_path.is_dir():
        config_path = input_path / "plusconfig.json"
    else:
        config_path = input_path.parent / "plusconfig.json"

    if not config_path.exists():
        config_path = Path.cwd() / "plusconfig.json"
    return config_path


def validate_bounds(lower: int, upper: int) -> bool:
    """检查规模上下界是否合法。"""

    if lower <= 0 or upper <= 0:
        error_print("下界和上界必须是正整数。")
        return False
    if lower > upper:
        error_print("下界不能大于上界。")
        return False
    return True


def debug_dump_config(
    config: PlusConfig,
    input_path: Path,
    lower: int,
    upper: int,
    ignored_labels: Iterable[str],
) -> None:
    """输出配置与输入信息。"""

    debug_print(f"使用配置文件: {resolve_config_path(input_path)}", enabled=config.verbose_debug)
    debug_print(
        "use_all_wires="
        f"{str(config.use_all_wires).lower()}, "
        "allow_disconnected="
        f"{str(config.allow_disconnected).lower()}, "
        "verbose_debug="
        f"{str(config.verbose_debug).lower()}",
        enabled=config.verbose_debug,
    )
    debug_print(f"输入路径: {input_path}", enabled=config.verbose_debug)
    debug_print(f"子图规模范围: [{lower}, {upper}]", enabled=config.verbose_debug)
    if ignored_labels:
        debug_print(f"忽略标签: {' '.join(ignored_labels)}", enabled=config.verbose_debug)
    else:
        debug_print("忽略标签: (无)", enabled=config.verbose_debug)
