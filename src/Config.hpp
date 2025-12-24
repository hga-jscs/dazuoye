#pragma once

#include <filesystem>
#include <string>

struct PlusConfig {
    // true: 使用每个节点的所有 wires 连接信息来建图。
    // false: 仅使用 wires[0] 来建图，避免多余连接。
    bool use_all_wires = false;
    // true: 允许枚举非连通子图（会产生指数级组合）。
    bool allow_disconnected = false;
    // true: 输出更详细的调试信息，便于观察处理过程。
    bool verbose_debug = true;
};

// 读取 plusconfig.json 并覆盖默认配置。
// 如果文件不存在或解析失败，会保留默认值并输出警告。
PlusConfig LoadPlusConfig(const std::filesystem::path& path);
