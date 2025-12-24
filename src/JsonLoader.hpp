#pragma once

#include <filesystem>

#include "third_party/json.hpp"

// 从指定路径读取 JSON 文件。
// 成功返回 true 并将结果写入 out_json，失败返回 false 并输出错误信息。
bool LoadJsonFile(const std::filesystem::path& path, nlohmann::json& out_json);
