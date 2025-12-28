from __future__ import annotations

from typing import List

from mytool.graph import Graph, is_closed


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
