# 环境配置要求（原子级说明）

本文件用于明确**能成功运行**所需的最小环境配置。请按自己的平台逐项核对。

## 1. 通用要求（所有平台）

- **Python 3**（必须）：建议 3.8+。
- **文件编码**：源代码为 UTF-8（包含中文日志），终端建议设置为 UTF-8。
- **运行目录权限**：需具备写权限（输出 `module_*.json`）。

## 2. Windows（PowerShell）

### 2.1 Python 3（推荐上手快）

**必需项**

- `python`（Python 3）
- PowerShell 5+（或 Windows Terminal）

**检查命令**

```powershell
python --version
```

**编译命令**

```powershell
python .\mytool .\json 5 6 z
```

**运行命令**

```powershell
.\mytool .\json 5 6 z
```

**常见问题**

- 报 “无法识别 mytool.exe”：
  - 确认 `mytool.exe` 是否真的生成在当前目录。
  - 确认执行时使用 `.\mytool.exe`。

### 2.2 Windows 备注

- 如果直接执行 `.\mytool` 提示权限问题，请使用 `python .\mytool`。

## 3. Linux / macOS

**必需项**

- `python3`

**检查命令**

```bash
python3 --version
```

**运行命令**

```bash
python3 mytool ./json 5 6 z
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
