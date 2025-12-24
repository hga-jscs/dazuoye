#pragma once

#include <filesystem>
#include <string>
#include <unordered_map>
#include <vector>

#include "Graph.hpp"
#include "SubgraphEnumerator.hpp"

// 将子图写回单独的 JSON 文件。
// 输出文件名包含原始文件名、忽略标签、节点数量与序号。
void WriteModules(const std::filesystem::path& input_path,
                  const Graph& graph,
                  const std::vector<Subgraph>& subgraphs,
                  const std::vector<std::string>& ignored_labels,
                  bool verbose_debug);
