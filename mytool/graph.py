from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Set

from mytool.console import info_print


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


def print_graph_summary(graph: Graph) -> None:
    """输出图摘要。"""

    info_print(f"节点数量: {len(graph.nodes)}")
    edge_count = sum(len(edges) for edges in graph.directed_edges)
    info_print(f"有向连接数量: {edge_count}")
    node_ids = " ".join(node.node_id for node in graph.nodes)
    info_print(f"节点列表: {node_ids}")
