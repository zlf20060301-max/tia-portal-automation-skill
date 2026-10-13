# 博途 TIA Portal Automation Skill + MCP

用于 Windows 本地 Siemens TIA Portal Openness 的 Codex Skill 和 Python stdio MCP。目标版本 V18 SP1，其他版本未测试。此项目为初始 pilot，尚未完成真实工程的读写验证。

## 验证范围

已验证：V18 SP1 `Siemens.Engineering.dll` 加载、没有运行实例时的进程枚举、MCP 初始化/工具发现/枚举请求。

待验证：实例附加、工程读取、PLC/程序块遍历、SCL 导入及离线编译。当前工具没有工程创建/打开/保存、下载、PLC 启停、仿真控制、Safety 或 WinCC 编辑能力。编译通过不代表现场逻辑验证通过。

## 安装

需要 Windows、Python 3.10+（64 位）、.NET Framework，以及已安装的 TIA Portal 和相同版本的 Openness。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

找到安装目录 `PublicAPI\V18\Siemens.Engineering.dll`，设置 `TIA_ENGINEERING_DLL`。DLL 属于西门子软件，本仓库不分发。

Windows 用户需加入 `Siemens TIA Openness` 本地组，并按西门子要求重新登录使组令牌生效。由有权限的用户或管理员完成，MCP 不自动修改权限。首次附加可能在博途中出现访问授权提示。

使用真实绝对路径注册：

```powershell
codex mcp add tia-portal-openness --env 'TIA_ENGINEERING_DLL=C:\Program Files\Siemens\Automation\Portal V18\PublicAPI\V18\Siemens.Engineering.dll' -- 'C:\path\to\repo\.venv\Scripts\python.exe' 'C:\path\to\repo\server.py'
```

将 `skills/tia-portal-automation` 文件夹复制到 `$CODEX_HOME/skills`（未设置时为用户目录 `.codex/skills`），在新聊天中使用 `$tia-portal-automation`。注册后的 MCP 通常也需要新聊天或应用重新加载才能发现。

## 工具

| 工具 | 作用 |
| --- | --- |
| list_processes | 枚举运行实例 |
| attach_process | 附加指定实例 |
| list_projects | 读取打开工程 |
| list_plcs | 读取 PLC software 容器 |
| list_blocks | 读取程序块及组 |
| generate_scl | 导入 SCL 并生成块，会修改离线工程，可能替换同名块 |
| compile_plc | 离线编译及诊断，不下载 |

操作采用进程内锁串行执行。附加后不能切换实例，需要重启 MCP。仅支持恰好一个打开工程；SCL 导入前应建立可恢复备份。源文件与目标工程均为运行 MCP 的用户可访问的本地资源。

真实 PLC 下载、启停、写入不属于本项目能力或默认授权范围。不要将本工具当作安全功能或现场验证的替代品。

## 协议烟雾测试

```powershell
$env:TIA_ENGINEERING_DLL='实际 DLL 的绝对路径'
.\.venv\Scripts\python.exe smoke_test.py
```

此测试启动 MCP、初始化、发现工具并调用只读进程枚举，不会附加实例或修改工程。

参考：[Siemens Openness](https://contentpath.siemens.com/efficient_engineering/en_automated-engineering)、[官方代码示例](https://github.com/siemens/tia-portal-openness-code-snippets)。
