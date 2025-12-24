#include "ModuleWriter.hpp"

#include <fstream>
#include <iostream>
#include <map>

namespace {

std::string JoinLabels(const std::vector<std::string>& labels) {
    if (labels.empty()) {
        return "";
    }
    std::string result;
    for (std::size_t i = 0; i < labels.size(); ++i) {
        if (i > 0) {
            result += "_";
        }
        result += labels[i];
    }
    return result;
}

}  // namespace

void WriteModules(const std::filesystem::path& input_path,
                  const Graph& graph,
                  const std::vector<Subgraph>& subgraphs,
                  const std::vector<std::string>& ignored_labels,
                  bool verbose_debug) {
    std::map<std::size_t, std::size_t> counter_by_size;
    const std::string base = input_path.stem().string();
    const std::string label_part = JoinLabels(ignored_labels);

    for (const auto& subgraph : subgraphs) {
        std::vector<Node> nodes;
        nodes.reserve(subgraph.nodes.size());
        for (std::size_t idx : subgraph.nodes) {
            nodes.push_back(graph.nodes[idx]);
        }

        nlohmann::json output = nlohmann::json::array();
        for (const auto& node : nodes) {
            output.push_back(node.data);
        }

        std::size_t size = nodes.size();
        std::size_t index = ++counter_by_size[size];

        std::string filename = "module_" + base + "_";
        if (!label_part.empty()) {
            filename += label_part + "_";
        }
        filename += std::to_string(size) + "_" + std::to_string(index) + ".json";

        std::filesystem::path out_path = input_path.parent_path() / filename;
        std::ofstream file(out_path);
        if (!file.is_open()) {
            std::cerr << "[WARN] 无法写入文件: " << out_path << std::endl;
            continue;
        }
        file << output.dump(4);
        if (verbose_debug) {
            std::cout << "[MODULE] " << out_path.filename().string() << "\n";
            std::cout << "  节点数量: " << size << "\n";
            std::cout << "  节点列表: ";
            for (std::size_t i = 0; i < nodes.size(); ++i) {
                if (i > 0) {
                    std::cout << ", ";
                }
                std::cout << nodes[i].id;
            }
            std::cout << "\n";
        }
    }
}
