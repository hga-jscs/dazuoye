#pragma once

#include <filesystem>
#include <string>
#include <unordered_map>
#include <vector>

#include "Graph.hpp"
#include "SubgraphEnumerator.hpp"

void WriteModules(const std::filesystem::path& input_path,
                  const Graph& graph,
                  const std::vector<Subgraph>& subgraphs,
                  const std::vector<std::string>& ignored_labels,
                  bool verbose_debug);
