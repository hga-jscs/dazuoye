#!/usr/bin/env python3
"""
mytool.py

从 Node-RED 风格的 JSON 中枚举满足约束的子图，并输出为 module_*.json 文件。

使用方式请见 script/使用说明.md。
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Set


@dataclass
class Node:
    """图节点，保留原始 JSON 数据以便输出。"""

    node_id: str
    data: Dict[str, Any]


@dataclass
class Graph:
    """图结构（邻接表表示）。"""

    nodes: List[Node]
    id_to_index: Dict[str, int]
    directed_edges: List[List[int]]
    undirected_edges: List[List[int]]


@dataclass
class PlusConfig:
    """可选配置（来自 plusconfig.json）。"""

    use_all_wires: bool = False
    allow_disconnected: bool = False
    verbose_debug: bool = True


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


def add_edge(
    directed: List[List[int]],
    undirected: List[List[int]],
    from_index: int,
    to_index: int,
) -> None:
    """添加边（有向 + 无向）。"""

    directed[from_index].append(to_index)
    undirected[from_index].append(to_index)
    undirected[to_index].append(from_index)


def scan_json_for_ids(
    value: Any,
    key: str,
    from_index: int,
    id_to_index: Dict[str, int],
    ignored_labels: Set[str],
    seen: Set[int],
    directed: List[List[int]],
    undirected: List[List[int]],
) -> None:
    """深度扫描 JSON 内容，寻找字符串形式的节点引用。"""

    if key and key in ignored_labels:
        return

    if isinstance(value, dict):
        for child_key, child_value in value.items():
            # wires/id 单独处理，避免重复建边
            if child_key in {"wires", "id"}:
                continue
            scan_json_for_ids(
                child_value,
                child_key,
                from_index,
                id_to_index,
                ignored_labels,
                seen,
                directed,
                undirected,
            )
        return

    if isinstance(value, list):
        for child in value:
            scan_json_for_ids(
                child,
                key,
                from_index,
                id_to_index,
                ignored_labels,
                seen,
                directed,
                undirected,
            )
        return

    if isinstance(value, str):
        target_index = id_to_index.get(value)
        if target_index is None or target_index in seen:
            return
        seen.add(target_index)
        add_edge(directed, undirected, from_index, target_index)


def build_graph(
    array: Any,
    ignored_labels: Set[str],
    use_all_wires: bool,
) -> Graph:
    """根据输入 JSON 构建图。"""

    nodes: List[Node] = []
    id_to_index: Dict[str, int] = {}

    if not isinstance(array, list):
        return Graph(nodes=nodes, id_to_index=id_to_index, directed_edges=[], undirected_edges=[])

    for node_json in array:
        if not isinstance(node_json, dict):
            continue
        node_id = node_json.get("id")
        if not isinstance(node_id, str):
            continue
        id_to_index[node_id] = len(nodes)
        nodes.append(Node(node_id=node_id, data=node_json))

    directed = [[] for _ in nodes]
    undirected = [[] for _ in nodes]

    for idx, node in enumerate(nodes):
        node_json = node.data
        seen: Set[int] = set()

        # 1) wires 结构直接建立连接
        wires = node_json.get("wires")
        if isinstance(wires, list):
            groups = wires if use_all_wires else wires[:1]
            for group in groups:
                if not isinstance(group, list):
                    continue
                for target in group:
                    if not isinstance(target, str):
                        continue
                    target_index = id_to_index.get(target)
                    if target_index is None or target_index in seen:
                        continue
                    seen.add(target_index)
                    add_edge(directed, undirected, idx, target_index)

        # 2) 其他字段深度扫描，补充隐藏引用
        for key, value in node_json.items():
            if key in {"wires", "id"}:
                continue
            scan_json_for_ids(
                value,
                key,
                idx,
                id_to_index,
                ignored_labels,
                seen,
                directed,
                undirected,
            )

    return Graph(nodes=nodes, id_to_index=id_to_index, directed_edges=directed, undirected_edges=undirected)


def is_closed(graph: Graph, in_set: List[bool]) -> bool:
    """检查子图是否闭包（有向边不指向外部）。"""

    for idx, included in enumerate(in_set):
        if not included:
            continue
        for target in graph.directed_edges[idx]:
            if not in_set[target]:
                return False
    return True


def add_if_valid(
    output: List[List[int]],
    graph: Graph,
    nodes: List[int],
    lower: int,
    upper: int,
) -> None:
    """满足约束时写入结果集。"""

    if len(nodes) < lower or len(nodes) > upper:
        return
    in_set = [False] * len(graph.nodes)
    for node in nodes:
        in_set[node] = True
    if not is_closed(graph, in_set):
        return
    output.append(nodes.copy())


def enumerate_disconnected_rec(
    output: List[List[int]],
    graph: Graph,
    current: List[int],
    index: int,
    lower: int,
    upper: int,
) -> None:
    """允许非连通子图时的枚举。"""

    if len(current) > upper:
        return
    if index == len(graph.nodes):
        add_if_valid(output, graph, current, lower, upper)
        return
    current.append(index)
    enumerate_disconnected_rec(output, graph, current, index + 1, lower, upper)
    current.pop()
    enumerate_disconnected_rec(output, graph, current, index + 1, lower, upper)


def enumerate_connected_rec(
    output: List[List[int]],
    graph: Graph,
    current: List[int],
    candidates: List[int],
    in_set: List[bool],
    start: int,
    lower: int,
    upper: int,
) -> None:
    """仅连通子图时的 DFS 枚举。"""

    add_if_valid(output, graph, current, lower, upper)
    if len(current) >= upper:
        return

    candidates_snapshot = candidates.copy()
    for candidate in candidates_snapshot:
        if in_set[candidate]:
            continue
        current.append(candidate)
        in_set[candidate] = True

        new_candidates = [c for c in candidates if c != candidate]
        for neighbor in graph.undirected_edges[candidate]:
            if neighbor > start and not in_set[neighbor] and neighbor not in new_candidates:
                new_candidates.append(neighbor)

        enumerate_connected_rec(
            output,
            graph,
            current,
            new_candidates,
            in_set,
            start,
            lower,
            upper,
        )

        in_set[candidate] = False
        current.pop()


def enumerate_subgraphs(
    graph: Graph,
    lower: int,
    upper: int,
    allow_disconnected: bool,
) -> List[List[int]]:
    """根据配置枚举子图。"""

    if not graph.nodes or lower > upper or upper <= 0:
        return []

    output: List[List[int]] = []
    if allow_disconnected:
        enumerate_disconnected_rec(output, graph, [], 0, lower, upper)
        return output

    for start in range(len(graph.nodes)):
        current = [start]
        in_set = [False] * len(graph.nodes)
        in_set[start] = True
        candidates = [n for n in graph.undirected_edges[start] if n > start]
        enumerate_connected_rec(output, graph, current, candidates, in_set, start, lower, upper)
    return output


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


def print_graph_summary(graph: Graph) -> None:
    """输出图摘要。"""

    info_print(f"节点数量: {len(graph.nodes)}")
    edge_count = sum(len(edges) for edges in graph.directed_edges)
    info_print(f"有向连接数量: {edge_count}")
    node_ids = " ".join(node.node_id for node in graph.nodes)
    info_print(f"节点列表: {node_ids}")


def load_json_file(path: Path) -> Any:
    """读取 JSON 文件，失败返回 None。"""

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - 输出需友好
        error_print(f"JSON 解析失败: {path} ({exc})")
        return None


def print_usage() -> None:
    """打印用法。"""

    print("用法: python3 script/mytool.py <目标文件/目录> <下界> <上界> [忽略标签1 忽略标签2 ...]")
    print("示例: python3 script/mytool.py ./json 5 6 z")


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


def debug_dump_config(config: PlusConfig, input_path: Path, lower: int, upper: int, ignored_labels: Iterable[str]) -> None:
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
