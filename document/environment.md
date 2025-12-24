# 环境配置要求（原子级说明）

本文件用于明确**能成功编译与运行**所需的最小环境配置。请按自己的平台逐项核对。

## 1. 通用要求（所有平台）

- **C++17 编译器**（必须）：支持 `std::filesystem`。
- **构建工具**：命令行可用 `g++` 或 `cl`。
- **文件编码**：源代码为 UTF-8（包含中文日志），终端建议设置为 UTF-8。
- **运行目录权限**：需具备写权限（输出 `module_*.json`）。

## 2. Windows（PowerShell）

### 2.1 MinGW-w64（推荐上手快）

**必需项**

- `g++`（MinGW-w64 版，支持 C++17）
- PowerShell 5+（或 Windows Terminal）

**检查命令**

```powershell
g++ --version
```

**编译命令**

```powershell
g++ -std=c++17 -O2 -Wall -Wextra -pedantic -I.\src -o mytool.exe `
  src\main.cpp src\Config.cpp src\Graph.cpp src\JsonLoader.cpp `
  src\SubgraphEnumerator.cpp src\ModuleWriter.cpp
```

**运行命令**

```powershell
.\mytool.exe .\json 5 6 z
```

**常见问题**

- 报 “无法识别 mytool.exe”：
  - 确认 `mytool.exe` 是否真的生成在当前目录。
  - 确认执行时使用 `.\mytool.exe`。

### 2.2 MSVC（Visual Studio）

**必需项**

- Visual Studio（C++ 桌面开发）
- “x64 Native Tools Command Prompt for VS”

**检查命令**

```powershell
cl
```

**编译命令**

```powershell
cl /std:c++17 /O2 /W4 /EHsc /I.\src `
  src\main.cpp src\Config.cpp src\Graph.cpp src\JsonLoader.cpp `
  src\SubgraphEnumerator.cpp src\ModuleWriter.cpp `
  /Fe:mytool.exe
```

**运行命令**

```powershell
.\mytool.exe .\json 5 6 z
```

## 3. Linux / macOS

**必需项**

- `g++`（支持 C++17）

**检查命令**

```bash
g++ --version
```

**编译命令**

```bash
g++ -std=c++17 -O2 -Wall -Wextra -pedantic -I./src -o mytool \
  src/main.cpp src/Config.cpp src/Graph.cpp src/JsonLoader.cpp \
  src/SubgraphEnumerator.cpp src/ModuleWriter.cpp
```

**运行命令**

```bash
./mytool ./json 5 6 z
```

## 4. 目录与输入约束（运行级别）

- 输入可以是**单个 `.json` 文件**或**包含 `.json` 的目录**。
- 目录中以 `module_` 开头的文件会被自动跳过（避免重复处理）。
- 配置文件 `plusconfig.json` 可放在：
  - 输入文件的同级目录；或
  - 输入目录内；或
  - 当前工作目录。

## 5. 调试输出建议

- 默认 `verbose_debug=true`，会输出节点数、边数、子图列表等可视化信息。
- 如果输出太多，可将其设为 `false`。
