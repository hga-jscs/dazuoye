# 使用说明（傻瓜版）

> 本工具用于从 JSON 节点数组中枚举子图，并输出独立的 module_*.json 文件。
> **调试输出非常重要**：如果你想确认程序到底做了什么，请确保 `verbose_debug` 为 `true`。

## 0. 环境准备（Python）

本工具使用 **Python 3** 直接运行，无需编译。

### Linux / macOS

```bash
python3 mytool ./json 5 6 z
```

### Windows（PowerShell）

```powershell
python .\mytool .\json 5 6 z
```

> 如果系统已允许执行脚本，也可以使用 `./mytool`（类 Unix）或 `.\mytool`（PowerShell）。

## 1. 准备输入

1. **准备 JSON 文件或目录**
   - 输入可以是单个 `.json` 文件，或者包含多个 `.json` 的目录。
   - 目录里以 `module_` 开头的文件会被自动跳过，避免重复处理。

2. **准备配置文件（可选，但强烈推荐）**
   - 在输入目录或文件同级放一个 `plusconfig.json`。
   - 如果找不到，会尝试使用当前目录的 `plusconfig.json`。

示例配置：

```json
{
  "use_all_wires": false,
  "allow_disconnected": false,
  "verbose_debug": true
}
```

字段说明：

- `use_all_wires`：是否使用所有 wires 连接（true 更全面，false 更保守）。
- `allow_disconnected`：是否允许非连通子图（true 会爆炸性增长，谨慎）。
- `verbose_debug`：是否输出详细调试信息（建议保持 true，便于核对）。

## 2. 运行方式

进入项目根目录，执行：

```bash
python3 mytool <目标文件或目录> <下界> <上界> [忽略标签...]
```

### 示例

```bash
python3 mytool ./json 5 6 z
```

解释：

- `./json`：目标目录（也可替换为单文件路径）。
- `5 6`：子图大小范围（下界=5，上界=6）。
- `z`：忽略标签（可多个），会跳过 JSON 中 key 为 `z` 的字段。

## 3. 运行时你会看到什么（可视化调试输出）

当 `verbose_debug = true` 时，输出会包含：

- 使用的配置文件路径
- 当前配置项
- 忽略标签列表
- 待处理文件数量
- 每个文件的节点数量、连接数量、节点列表
- 每个输出 module 的节点列表

示例输出（节选）：

```
[DEBUG] 使用配置文件: /path/to/plusconfig.json
[DEBUG] use_all_wires=false, allow_disconnected=false, verbose_debug=true
[DEBUG] 忽略标签: z
[DEBUG] 待处理文件数量: 3

[FILE] /path/to/input.json
[INFO] 节点数量: 12
[INFO] 有向连接数量: 18
[INFO] 节点列表: 1 2 3 4 5 6 7 8 9 10 11 12
[INFO] 满足条件的子图数量: 2
[MODULE] module_input_5_1.json
  节点数量: 5
  节点列表: 2, 3, 4, 7, 8
```

> 如果你只关心生成结果，可以将 `verbose_debug` 设为 `false`。

## 4. 输出文件在哪里？

输出文件会写到**输入文件所在目录**，命名规则如下：

```
module_<原始文件名>_<忽略标签>_<节点数量>_<序号>.json
```

示例：

```
module_input_z_5_1.json
```

## 5. 常见问题

**Q1: 运行后没有输出文件？**

- 确认输入 JSON 格式正确。
- 查看 `[ERROR]` 或 `[WARN]` 日志。
- 确认子图大小范围是否太严格。
- Windows 下请确认 `mytool.exe` 是否真的生成在当前目录。

**Q2: 输出太多文件？**

- 将 `allow_disconnected` 设置为 `false`。
- 缩小子图大小范围。
- 加入更多忽略标签过滤无关字段。

**Q3: 我看不懂输出？**

- 确保 `verbose_debug` 为 `true`，这样日志最完整。
- 查看 `[MODULE]` 段落，里面会列出每个子图的节点 ID。

**Q4: PowerShell 报“无法识别 mytool.exe”？**

- 确认已编译生成 `mytool.exe`（见“0. 编译”）。
- 确认当前目录在 `mytool.exe` 所在路径（`ls`/`dir` 应能看到它）。
- 运行时用 `.\mytool.exe` 而不是 `./mytool`。

## 6. 自测建议（更完整的测试集）

项目自带测试 JSON（见 `test/`），建议至少跑以下组合：

```bash
python3 mytool test/simple.json 2 3
python3 mytool test/ignore_label.json 2 4 z
python3 mytool test/disconnected.json 2 3
```

如果要压力测试，建议开启 `verbose_debug` 先观察规模，再决定是否打开 `allow_disconnected`。
