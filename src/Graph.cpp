#include "Graph.hpp"

#include <iostream>
#include <unordered_set>

namespace {

void AddEdge(std::vector<std::vector<std::size_t>>& directed,
             std::vector<std::vector<std::size_t>>& undirected,
             std::size_t from,
             std::size_t to) {
    directed[from].push_back(to);
    undirected[from].push_back(to);
    undirected[to].push_back(from);
}

void ScanJsonForIds(const nlohmann::json& value,
                    const std::string& key,
                    std::size_t from,
                    const std::unordered_map<std::string, std::size_t>& id_to_index,
                    const std::unordered_map<std::string, bool>& ignored_labels,
                    std::unordered_set<std::size_t>& seen,
                    std::vector<std::vector<std::size_t>>& directed,
                    std::vector<std::vector<std::size_t>>& undirected) {
    if (!key.empty() && ignored_labels.count(key)) {
        return;
    }

    if (value.is_object()) {
        for (const auto& item : value.items()) {
            const std::string& child_key = item.key();
            if (child_key == "wires" || child_key == "id") {
                continue;
            }
            ScanJsonForIds(item.value(), child_key, from, id_to_index, ignored_labels, seen, directed, undirected);
        }
        return;
    }

    if (value.is_array()) {
        for (const auto& child : value) {
            ScanJsonForIds(child, key, from, id_to_index, ignored_labels, seen, directed, undirected);
        }
        return;
    }

    if (value.is_string()) {
        const std::string target = value.get<std::string>();
        auto it = id_to_index.find(target);
        if (it != id_to_index.end()) {
            std::size_t to = it->second;
            if (!seen.count(to)) {
                seen.insert(to);
                AddEdge(directed, undirected, from, to);
            }
        }
    }
}

}  // namespace

Graph BuildGraph(const nlohmann::json& array,
                 const std::unordered_map<std::string, bool>& ignored_labels,
                 bool use_all_wires) {
    Graph graph;
    if (!array.is_array()) {
        return graph;
    }

    for (const auto& node_json : array) {
        if (!node_json.is_object()) {
            continue;
        }
        if (!node_json.contains("id") || !node_json["id"].is_string()) {
            continue;
        }
        Node node;
        node.id = node_json["id"].get<std::string>();
        node.data = node_json;
        graph.id_to_index[node.id] = graph.nodes.size();
        graph.nodes.push_back(std::move(node));
    }

    graph.directed_edges.resize(graph.nodes.size());
    graph.undirected_edges.resize(graph.nodes.size());

    for (std::size_t i = 0; i < graph.nodes.size(); ++i) {
        const auto& node_json = graph.nodes[i].data;
        std::unordered_set<std::size_t> seen;

        if (node_json.contains("wires") && node_json["wires"].is_array()) {
            const auto& wires = node_json["wires"];
            if (use_all_wires) {
                for (const auto& group : wires) {
                    if (!group.is_array()) {
                        continue;
                    }
                    for (const auto& target : group) {
                        if (!target.is_string()) {
                            continue;
                        }
                        auto it = graph.id_to_index.find(target.get<std::string>());
                        if (it != graph.id_to_index.end()) {
                            if (!seen.count(it->second)) {
                                seen.insert(it->second);
                                AddEdge(graph.directed_edges, graph.undirected_edges, i, it->second);
                            }
                        }
                    }
                }
            } else if (!wires.empty()) {
                const auto& group = wires[0];
                if (group.is_array()) {
                    for (const auto& target : group) {
                        if (!target.is_string()) {
                            continue;
                        }
                        auto it = graph.id_to_index.find(target.get<std::string>());
                        if (it != graph.id_to_index.end()) {
                            if (!seen.count(it->second)) {
                                seen.insert(it->second);
                                AddEdge(graph.directed_edges, graph.undirected_edges, i, it->second);
                            }
                        }
                    }
                }
            }
        }

        for (const auto& item : node_json.items()) {
            const std::string& key = item.key();
            if (key == "wires" || key == "id") {
                continue;
            }
            ScanJsonForIds(item.value(), key, i, graph.id_to_index, ignored_labels, seen,
                           graph.directed_edges, graph.undirected_edges);
        }
    }

    return graph;
}
