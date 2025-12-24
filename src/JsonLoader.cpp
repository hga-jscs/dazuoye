#include "JsonLoader.hpp"

#include <fstream>
#include <iostream>

bool LoadJsonFile(const std::filesystem::path& path, nlohmann::json& out_json) {
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "[ERROR] 无法打开 JSON 文件: " << path << std::endl;
        return false;
    }

    try {
        // 直接使用 nlohmann::json 流式解析，保证格式错误可被捕获。
        file >> out_json;
    } catch (const std::exception& ex) {
        std::cerr << "[ERROR] JSON 解析失败: " << path << "，原因: " << ex.what() << std::endl;
        return false;
    }

    return true;
}
