from fastmcp import FastMCP

import app.server as server

EXPECTED_TOOLS = {
    "get_protocols",
    "search_packets",
    "get_conversations",
    "follow_stream",
    "get_statistics",
    "analyze_behavior",
    "list_interfaces",
    "capture_live",
    "check_capture_status",
    "save_live_capture",
    "discard_live_capture",
}


def test_mcp_instanciado():
    assert isinstance(server.mcp, FastMCP)


async def test_todas_as_ferramentas_estao_registradas():
    tools = await server.mcp.list_tools()
    names = {tool.name for tool in tools}

    assert EXPECTED_TOOLS <= names
