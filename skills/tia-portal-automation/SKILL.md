---
name: tia-portal-automation
description: 使用本地 Siemens TIA Portal Openness MCP 检查博途工程、读取 PLC 程序块，并试验 SCL 导入和离线编译。适用于博途/TIA Portal 工程自动化；不适用于 STEP 7 Micro/WIN SMART。
---

# 博途工程自动化

通过 `tia-portal-openness` MCP 操作 Windows 上已运行的博途。先调用 `list_processes`，选择用户目标实例后 `attach_process`，再读取 `list_projects`、`list_plcs`、`list_blocks`。多个实例或目标工程不明确时先确定目标；不要自行选第一个。每次使用来自工具返回的精确 `plc_path`。

连接前按仓库 README 检查版本对应的 DLL 和 Windows Openness 组成员资格。权限失败时报告原始异常和修复方法，不自行提升权限或修改用户组。无进程时请用户打开博途及目标工程；当前 MCP 不负责启动、创建或打开工程。

## 能力与证据

- 本机 V18 SP1 的 DLL 加载与空进程枚举已通过；MCP 初始化、工具发现和枚举调用已通过。
- 附加实例、工程/PLC/块读取尚未在真实打开工程验证，属于 pilot。
- `generate_scl` 和 `compile_plc` 是 pilot。不得声称已实现完整自动编程、仿真或工程交付。
- 当前没有保存、下载、在线监控、PLC 启停、Safety 编程、WinCC 编辑工具。禁止用本技能推断这些能力已验证。

## SCL 编辑

确认 CPU 型号、博途版本、接口/I/O、运行逻辑和用户授权的工程修改范围。编写 SCL 时区分 OB/FB/FC/DB、实例状态和临时变量；根据实际工艺明确复位、互锁和故障行为。

在导入前为目标工程建立用户可恢复的备份，检查源文件中的块名与已有块冲突。`generate_scl` 会改变打开的离线工程，可能替换同名块；只在用户已授权该工程编辑且有备份时执行。工具不自动保存，失败后读取当前工程状态，避免盲目重试。

导入后运行 `compile_plc` 并审查全部错误/警告。编译通过只证明语法和工程兼容性，逻辑正确性需要另行工况验证。交付时分别说明源文件、导入结果、编译诊断和未验证项。

实际 PLC 下载、启停和写入需要用户明确授权具体目标与动作，并使用另行验证的工具；本 MCP 不提供这些操作。
