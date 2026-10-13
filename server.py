"""Local Siemens TIA Portal Openness MCP (Windows / .NET Framework)."""
import os
from pathlib import Path
from threading import RLock
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tia-portal-openness")
lock = RLock()
portal = None

def api():
    import clr
    dll = os.environ.get("TIA_ENGINEERING_DLL")
    if not dll or not Path(dll).is_file():
        raise RuntimeError("Set TIA_ENGINEERING_DLL to your version's PublicAPI/Siemens.Engineering.dll")
    clr.AddReference(str(Path(dll).resolve()))
    from Siemens.Engineering import TiaPortal
    return TiaPortal

def connected():
    if portal is None:
        raise RuntimeError("Call attach_process first; keep the selected TIA instance open")
    return portal

def project():
    projects = list(connected().Projects)
    if len(projects) != 1:
        raise RuntimeError("Exactly one open project is required")
    return projects[0]

def items(collection, prefix=""):
    for item in collection:
        path = prefix + "/" + str(item.Name)
        yield path, item
        yield from items(item.DeviceItems, path)

def software_objects():
    from Siemens.Engineering.HW.Features import SoftwareContainer
    from Siemens.Engineering.SW import PlcSoftware
    p = project()
    def devices(group):
        yield from group.Devices
        for child in group.Groups:
            yield from devices(child)
    all_devices = list(p.Devices) + list(p.UngroupedDevicesGroup.Devices)
    for group in p.DeviceGroups:
        all_devices.extend(devices(group))
    for device in all_devices:
        for path, item in items(device.DeviceItems, str(device.Name)):
            container = item.GetService[SoftwareContainer]()
            if container is not None and isinstance(container.Software, PlcSoftware):
                yield path, container.Software

def plc(path):
    matches = [sw for key, sw in software_objects() if key == path]
    if len(matches) != 1:
        raise ValueError("Use an exact plc_path returned by list_plcs")
    return matches[0]

@mcp.tool()
def list_processes() -> list[dict]:
    """Read running TIA instances. Does not start TIA or modify projects."""
    with lock:
        return [{"process_id": int(p.Id)} for p in api().GetProcesses()]

@mcp.tool()
def attach_process(process_id: int) -> dict:
    """Attach to an existing instance; TIA may request Openness access approval."""
    global portal
    with lock:
        if portal is not None:
            raise RuntimeError("Already attached; restart MCP to select another instance")
        match = [p for p in api().GetProcesses() if int(p.Id) == process_id]
        if len(match) != 1:
            raise ValueError("Process not found")
        portal = match[0].Attach()
        return {"attached": process_id}

@mcp.tool()
def list_projects() -> list[dict]:
    """Read names and paths of open projects."""
    with lock:
        return [{"name": str(p.Name), "path": str(p.Path)} for p in connected().Projects]

@mcp.tool()
def list_plcs() -> list[dict]:
    """Read PLC software containers in the selected open project."""
    with lock:
        return [{"plc_path": path, "name": str(sw.Name)} for path, sw in software_objects()]

@mcp.tool()
def list_blocks(plc_path: str) -> list[dict]:
    """Read PLC block names, including nested block groups."""
    with lock:
        def walk(group, prefix=""):
            for block in group.Blocks:
                yield {"path": prefix + str(block.Name), "language": str(block.ProgrammingLanguage)}
            for child in group.Groups:
                yield from walk(child, prefix + str(child.Name) + "/")
        return list(walk(plc(plc_path).BlockGroup))

@mcp.tool()
def generate_scl(plc_path: str, source_path: str) -> dict:
    """PILOT: import .scl and generate blocks in the open offline project. May replace existing blocks; backup and explicit project-edit scope required."""
    with lock:
        from System.IO import FileInfo
        path = Path(source_path).resolve(strict=True)
        if path.suffix.lower() != ".scl":
            raise ValueError("A .scl file is required")
        source = plc(plc_path).ExternalSourceGroup.ExternalSources.CreateFromFile(FileInfo(str(path)))
        source.GenerateBlocksFromSource()
        return {"generated_from": str(path), "compile_required": True}

@mcp.tool()
def compile_plc(plc_path: str) -> dict:
    """PILOT: compile offline PLC software and return compiler diagnostics; does not download."""
    with lock:
        from Siemens.Engineering.Compiler import ICompilable
        result = plc(plc_path).GetService[ICompilable]().Compile()
        def messages(entries):
            return [{"description": str(x.Description), "state": str(x.State),
                     "children": messages(x.Messages)} for x in entries]
        return {"state": str(result.State), "errors": int(result.ErrorCount),
                "warnings": int(result.WarningCount), "messages": messages(result.Messages)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
