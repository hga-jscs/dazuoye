#pragma once

#include <filesystem>
#include <string>

struct PlusConfig {
    bool use_all_wires = false;
    bool allow_disconnected = false;
    bool verbose_debug = true;
};

PlusConfig LoadPlusConfig(const std::filesystem::path& path);
