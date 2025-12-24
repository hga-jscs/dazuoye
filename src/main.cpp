#include <filesystem>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

#include "Config.hpp"
#include "Graph.hpp"
#include "JsonLoader.hpp"
#include "ModuleWriter.hpp"
#include "SubgraphEnumerator.hpp"

namespace {

void PrintUsage() {
    std::cout << "用法: mytool <目标文件/目录> <下界> <上界> [忽略标签1 忽略标签2 ...]\n";
    std::cout << "示例: mytool ./json 230902 5 6 z\n";
}

std::vector<std::filesystem::path> CollectJsonFiles(const std::filesystem::path& input_path) {
    std::vector<std::filesystem::path> files;
    if (std::filesystem::is_regular_file(input_path)) {
        if (input_path.extension() == ".json") {
            files.push_back(input_path);
        }
        return files;
    }

    if (!std::filesystem::is_directory(input_path)) {
        return files;
    }

    for (const auto& entry : std::filesystem::directory_iterator(input_path)) {
        if (!entry.is_regular_file()) {
            continue;
        }
        const auto& path = entry.path();
        if (path.extension() != ".json") {
            continue;
        }
        if (path.filename().string().rfind("module_", 0) == 0) {
            continue;
        }
        files.push_back(path);
    }
    return files;
}

std::unordered_map<std::string, bool> BuildIgnoreMap(const std::vector<std::string>& labels) {
    std::unordered_map<std::string, bool> ignored;
    for (const auto& label : labels) {
        ignored[label] = true;
    }
    return ignored;
}

void PrintGraphSummary(const Graph& graph) {
    std::cout << "[INFO] 节点数量: " << graph.nodes.size() << "\n";
    std::size_t edge_count = 0;
    for (const auto& edges : graph.directed_edges) {
        edge_count += edges.size();
    }
    std::cout << "[INFO] 有向连接数量: " << edge_count << "\n";
    std::cout << "[INFO] 节点列表:";
    for (const auto& node : graph.nodes) {
        std::cout << " " << node.id;
    }
    std::cout << "\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    if (argc < 4) {
        PrintUsage();
        return 1;
    }

    std::filesystem::path input_path = argv[1];
    std::size_t lower = 0;
    std::size_t upper = 0;
    try {
        lower = static_cast<std::size_t>(std::stoul(argv[2]));
        upper = static_cast<std::size_t>(std::stoul(argv[3]));
    } catch (const std::exception&) {
        std::cerr << "[ERROR] 下界和上界必须是非负整数。\n";
        return 1;
    }

    std::vector<std::string> ignored_labels;
    for (int i = 4; i < argc; ++i) {
        ignored_labels.push_back(argv[i]);
    }

    std::filesystem::path config_path;
    if (std::filesystem::is_directory(input_path)) {
        config_path = input_path / "plusconfig.json";
    } else {
        config_path = input_path.parent_path() / "plusconfig.json";
    }
    if (!std::filesystem::exists(config_path)) {
        config_path = std::filesystem::current_path() / "plusconfig.json";
    }
    PlusConfig config = LoadPlusConfig(config_path);
    auto files = CollectJsonFiles(input_path);
    if (files.empty()) {
        std::cerr << "[ERROR] 未找到可处理的 JSON 文件。\n";
        return 1;
    }

    std::unordered_map<std::string, bool> ignored_map = BuildIgnoreMap(ignored_labels);

    for (const auto& file_path : files) {
        nlohmann::json data;
        if (!LoadJsonFile(file_path, data)) {
            continue;
        }

        std::cout << "\n[FILE] " << file_path << "\n";
        Graph graph = BuildGraph(data, ignored_map, config.use_all_wires);
        if (config.verbose_debug) {
            PrintGraphSummary(graph);
        }

        auto subgraphs = EnumerateSubgraphs(graph, lower, upper, config.allow_disconnected);
        std::cout << "[INFO] 满足条件的子图数量: " << subgraphs.size() << "\n";

        WriteModules(file_path, graph, subgraphs, ignored_labels, config.verbose_debug);
    }

    return 0;
}
