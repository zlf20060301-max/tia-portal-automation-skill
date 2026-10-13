"""Check real MCP stdio transport without attaching to or changing a project."""
import asyncio
import json
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command=sys.executable,
        args=[str(Path(__file__).with_name("server.py"))], env=dict(os.environ))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()
            names = {t.name for t in (await client.list_tools()).tools}
            expected = {"list_processes", "attach_process", "list_projects", "list_plcs",
                        "list_blocks", "generate_scl", "compile_plc"}
            assert names == expected, names
            result = await client.call_tool("list_processes", {})
            assert not result.isError, result
            print(json.dumps({"protocol": "passed", "tools": sorted(names),
                              "processes": [c.model_dump() for c in result.content]}, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
