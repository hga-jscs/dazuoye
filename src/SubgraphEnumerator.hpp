#pragma once

#include <cstddef>
#include <vector>

#include "Graph.hpp"

struct Subgraph {
    std::vector<std::size_t> nodes;
};

std::vector<Subgraph> EnumerateSubgraphs(const Graph& graph,
                                         std::size_t lower,
                                         std::size_t upper,
                                         bool allow_disconnected);
