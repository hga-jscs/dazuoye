from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from mytool.config import debug_dump_config, load_plus_config, resolve_config_path, validate_bounds
from mytool.console import debug_print, error_print, info_print
from mytool.graph import build_graph, print_graph_summary
from mytool.io import collect_json_files, load_json_file, write_modules
from mytool.subgraphs import enumerate_subgraphs


def print_usage() -> None:
    """打印用法。"""

    print("用法: python3 -m mytool <目标文件/目录> <下界> <上界> [忽略标签1 忽略标签2 ...]")
    print("示例: python3 -m mytool ./json 5 6 z")
    print("兼容旧入口: python3 script/mytool.py <目标文件/目录> <下界> <上界> [忽略标签1 ...]")


def main(argv: Sequence[str]) -> int:
    if len(argv) < 4:
        print_usage()
        return 1

    input_path = Path(argv[1])
    try:
        lower = int(argv[2])
        upper = int(argv[3])
    except ValueError:
        error_print("下界和上界必须是非负整数。")
        return 1

    if not validate_bounds(lower, upper):
        return 1

    if not input_path.exists():
        error_print(f"目标路径不存在: {input_path}")
        return 1

    ignored_labels = list(argv[4:])
    config_path = resolve_config_path(input_path)
    config = load_plus_config(config_path)

    files = collect_json_files(input_path)
    if not files:
        error_print("未找到可处理的 JSON 文件。")
        return 1

    debug_dump_config(config, input_path, lower, upper, ignored_labels)
    debug_print(f"待处理文件数量: {len(files)}", enabled=config.verbose_debug)

    ignored_map = set(ignored_labels)

    for file_path in files:
        data = load_json_file(file_path)
        if data is None:
            continue
        print(f"\n[FILE] {file_path}")
        graph = build_graph(data, ignored_map, config.use_all_wires)
        if config.verbose_debug:
            print_graph_summary(graph)
        subgraphs = enumerate_subgraphs(graph, lower, upper, config.allow_disconnected)
        info_print(f"满足条件的子图数量: {len(subgraphs)}")
        write_modules(file_path, graph, subgraphs, ignored_labels, config.verbose_debug)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
