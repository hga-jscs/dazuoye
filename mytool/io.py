from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

from mytool.console import error_print, warn_print
from mytool.graph import Graph


def collect_json_files(input_path: Path) -> List[Path]:
    """收集待处理 JSON 文件列表。"""

    if input_path.is_file():
        return [input_path] if input_path.suffix == ".json" else []

    if not input_path.is_dir():
        return []

    files: List[Path] = []
    for entry in sorted(input_path.iterdir()):
        if not entry.is_file() or entry.suffix != ".json":
            continue
        if entry.name.startswith("module_"):
            # 避免重复处理输出文件
            continue
        files.append(entry)
    return files


def load_json_file(path: Path) -> Any:
    """读取 JSON 文件，失败返回 None。"""

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - 输出需友好
        error_print(f"JSON 解析失败: {path} ({exc})")
        return None


def join_labels(labels: Sequence[str]) -> str:
    """将忽略标签拼接为文件名片段。"""

    return "_".join(labels)


def write_modules(
    input_path: Path,
    graph: Graph,
    subgraphs: List[List[int]],
    ignored_labels: Sequence[str],
    verbose_debug: bool,
) -> None:
    """输出 module_*.json 文件。"""

    counter_by_size: Dict[int, int] = {}
    base = input_path.stem
    label_part = join_labels(ignored_labels)

    for nodes in subgraphs:
        size = len(nodes)
        counter_by_size[size] = counter_by_size.get(size, 0) + 1
        index = counter_by_size[size]

        filename = f"module_{base}_"
        if label_part:
            filename += f"{label_part}_"
        filename += f"{size}_{index}.json"

        out_path = input_path.parent / filename
        payload = [graph.nodes[idx].data for idx in nodes]
        try:
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=4), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001 - 输出需友好
            warn_print(f"无法写入文件: {out_path} ({exc})")
            continue

        if verbose_debug:
            print("[MODULE]")
            print(f"  文件: {out_path.name}")
            print(f"  节点数量: {size}")
            print("  节点列表: " + ", ".join(graph.nodes[idx].node_id for idx in nodes))
