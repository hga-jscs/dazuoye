#include "Config.hpp"

#include <fstream>
#include <iostream>

#include "third_party/json.hpp"

using nlohmann::json;

PlusConfig LoadPlusConfig(const std::filesystem::path& path) {
    PlusConfig config;
    if (!std::filesystem::exists(path)) {
        return config;
    }

    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "[WARN] 无法打开 plusconfig 文件: " << path << "，使用默认配置。" << std::endl;
        return config;
    }

    try {
        json data;
        file >> data;
        config.use_all_wires = data.value("use_all_wires", config.use_all_wires);
        config.allow_disconnected = data.value("allow_disconnected", config.allow_disconnected);
        config.verbose_debug = data.value("verbose_debug", config.verbose_debug);
    } catch (const std::exception& ex) {
        std::cerr << "[WARN] 解析 plusconfig 失败: " << ex.what() << "，使用默认配置。" << std::endl;
    }
    return config;
}
