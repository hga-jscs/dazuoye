#pragma once

#include <string>
#include <unordered_map>
#include <vector>

#include "third_party/json.hpp"

// 单个节点，保存其 ID 与完整 JSON 数据，便于后续输出。
struct Node {
    std::string id;
    nlohmann::json data;
};

// 图结构：包含节点列表、索引映射与有向/无向邻接表。
struct Graph {
    std::vector<Node> nodes;
    std::unordered_map<std::string, std::size_t> id_to_index;
    std::vector<std::vector<std::size_t>> directed_edges;
    std::vector<std::vector<std::size_t>> undirected_edges;
};

// 根据 JSON 数组构建图结构。
// ignored_labels 控制跳过的字段名；use_all_wires 控制 wires 的读取方式。
Graph BuildGraph(const nlohmann::json& array,
                 const std::unordered_map<std::string, bool>& ignored_labels,
                 bool use_all_wires);
