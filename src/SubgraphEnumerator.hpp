#pragma once

#include <cstddef>
#include <vector>

#include "Graph.hpp"

// 子图由节点索引组成。
struct Subgraph {
    std::vector<std::size_t> nodes;
};

// 根据大小上下界枚举子图。
// allow_disconnected 为 true 时枚举所有组合，为 false 时仅枚举连通子图。
std::vector<Subgraph> EnumerateSubgraphs(const Graph& graph,
                                         std::size_t lower,
                                         std::size_t upper,
                                         bool allow_disconnected);
