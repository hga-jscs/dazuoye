#pragma once

#include <string>
#include <unordered_map>
#include <vector>

#include "third_party/json.hpp"

struct Node {
    std::string id;
    nlohmann::json data;
};

struct Graph {
    std::vector<Node> nodes;
    std::unordered_map<std::string, std::size_t> id_to_index;
    std::vector<std::vector<std::size_t>> directed_edges;
    std::vector<std::vector<std::size_t>> undirected_edges;
};

Graph BuildGraph(const nlohmann::json& array,
                 const std::unordered_map<std::string, bool>& ignored_labels,
                 bool use_all_wires);
