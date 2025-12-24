#pragma once

#include <filesystem>

#include "third_party/json.hpp"

bool LoadJsonFile(const std::filesystem::path& path, nlohmann::json& out_json);
