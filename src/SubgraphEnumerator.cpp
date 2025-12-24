#include "SubgraphEnumerator.hpp"

#include <algorithm>
#include <unordered_set>

namespace {

bool IsClosed(const Graph& graph, const std::vector<bool>& in_set) {
    // 闭包检查：子图内的节点不能指向子图外的节点。
    for (std::size_t i = 0; i < graph.nodes.size(); ++i) {
        if (!in_set[i]) {
            continue;
        }
        for (std::size_t target : graph.directed_edges[i]) {
            if (!in_set[target]) {
                return false;
            }
        }
    }
    return true;
}

void AddIfValid(std::vector<Subgraph>& output,
                const Graph& graph,
                const std::vector<std::size_t>& nodes,
                std::size_t lower,
                std::size_t upper) {
    // 限制大小范围，并通过闭包过滤。
    if (nodes.size() < lower || nodes.size() > upper) {
        return;
    }
    std::vector<bool> in_set(graph.nodes.size(), false);
    for (std::size_t node : nodes) {
        in_set[node] = true;
    }
    if (!IsClosed(graph, in_set)) {
        return;
    }
    output.push_back(Subgraph{nodes});
}

void EnumerateDisconnectedRec(std::vector<Subgraph>& output,
                              const Graph& graph,
                              std::vector<std::size_t>& current,
                              std::size_t index,
                              std::size_t lower,
                              std::size_t upper) {
    // 递归枚举所有组合，剪枝控制上界。
    if (current.size() > upper) {
        return;
    }
    if (index == graph.nodes.size()) {
        AddIfValid(output, graph, current, lower, upper);
        return;
    }

    current.push_back(index);
    EnumerateDisconnectedRec(output, graph, current, index + 1, lower, upper);
    current.pop_back();

    EnumerateDisconnectedRec(output, graph, current, index + 1, lower, upper);
}

void EnumerateConnectedRec(std::vector<Subgraph>& output,
                           const Graph& graph,
                           std::vector<std::size_t>& current,
                           std::vector<std::size_t>& candidates,
                           std::vector<bool>& in_set,
                           std::size_t start,
                           std::size_t lower,
                           std::size_t upper) {
    // 在候选邻居中扩展连通子图，避免重复（只接受索引大于 start 的节点）。
    AddIfValid(output, graph, current, lower, upper);
    if (current.size() >= upper) {
        return;
    }

    std::vector<std::size_t> candidates_snapshot = candidates;
    for (std::size_t i = 0; i < candidates_snapshot.size(); ++i) {
        std::size_t candidate = candidates_snapshot[i];
        if (in_set[candidate]) {
            continue;
        }
        current.push_back(candidate);
        in_set[candidate] = true;

        std::vector<std::size_t> new_candidates = candidates;
        new_candidates.erase(std::remove(new_candidates.begin(), new_candidates.end(), candidate), new_candidates.end());
        for (std::size_t neighbor : graph.undirected_edges[candidate]) {
            if (neighbor > start && !in_set[neighbor]) {
                if (std::find(new_candidates.begin(), new_candidates.end(), neighbor) == new_candidates.end()) {
                    new_candidates.push_back(neighbor);
                }
            }
        }

        EnumerateConnectedRec(output, graph, current, new_candidates, in_set, start, lower, upper);

        in_set[candidate] = false;
        current.pop_back();
    }
}

}  // namespace

std::vector<Subgraph> EnumerateSubgraphs(const Graph& graph,
                                         std::size_t lower,
                                         std::size_t upper,
                                         bool allow_disconnected) {
    std::vector<Subgraph> output;
    // 不满足基本约束时直接返回空结果。
    if (graph.nodes.empty() || lower > upper || upper == 0) {
        return output;
    }

    if (allow_disconnected) {
        // 允许非连通时，直接枚举所有组合。
        std::vector<std::size_t> current;
        EnumerateDisconnectedRec(output, graph, current, 0, lower, upper);
        return output;
    }

    for (std::size_t start = 0; start < graph.nodes.size(); ++start) {
        // 以每个起点作为最小索引，避免重复枚举同一子图。
        std::vector<std::size_t> current{start};
        std::vector<bool> in_set(graph.nodes.size(), false);
        in_set[start] = true;

        std::vector<std::size_t> candidates;
        for (std::size_t neighbor : graph.undirected_edges[start]) {
            if (neighbor > start) {
                candidates.push_back(neighbor);
            }
        }
        EnumerateConnectedRec(output, graph, current, candidates, in_set, start, lower, upper);
    }

    return output;
}
