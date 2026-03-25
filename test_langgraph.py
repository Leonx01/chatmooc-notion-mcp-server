# -*- coding: utf-8 -*-
"""
Test LangGraph Client connection to Notion MCP Server
Usage: python test_langgraph.py
"""
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "your-mcp-secret")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")


async def test_call_tool():
    """Test calling a Notion tool via MCP"""
    print("=" * 50)
    print("Test: Call Notion Tool")
    print("=" * 50)

    if not NOTION_TOKEN:
        print("Error: Please set NOTION_TOKEN environment variable")
        sys.exit(1)

    print(f"Notion Token: {NOTION_TOKEN[:10]}...")
    print()

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        client = MultiServerMCPClient({
            "notion": {
                "transport": "http",
                "url": MCP_SERVER_URL,
                "headers": {
                    "Authorization": f"Bearer {NOTION_TOKEN}"
                }
            }
        })

        # Get tools
        print("Getting tools...")
        tools = await client.get_tools()
        print(f"[OK] Got {len(tools)} tools")
        print()

        # Find the search tool
        search_tool = None
        for tool in tools:
            if "search" in tool.name.lower():
                search_tool = tool
                break

        if not search_tool:
            print("[ERROR] Search tool not found")
            return

        print(f"Calling tool: {search_tool.name}")
        print()

        # Call the search tool
        result = await search_tool.ainvoke({"query": "", "page_size": 5})

        # Parse result - result is a list of content items
        if result:
            # Extract text from result
            if isinstance(result, list):
                text_content = result[0].get("text", "{}") if result else "{}"
                data = json.loads(text_content)
            else:
                data = json.loads(result)

            results = data.get("results", [])
            print(f"[OK] Found {len(results)} results:")
            for item in results[:5]:
                obj_type = item.get("object", "unknown")
                if obj_type == "page":
                    title = ""
                    props = item.get("properties", {})
                    for v in props.values():
                        if v.get("type") == "title":
                            title_list = v.get("title", [])
                            if title_list:
                                title = title_list[0].get("plain_text", "")
                    print(f"  Page: {title or '(untitled)'}")
                elif obj_type == "database":
                    print(f"  Database: {item.get('id', 'unknown')[:8]}...")
                else:
                    print(f"  {obj_type}: {item.get('id', 'unknown')[:8]}...")

        print()
        print("[OK] Tool call test passed!")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


async def main():
    print("LangGraph Client Test Script")
    print()

    if not NOTION_TOKEN:
        print("Please set NOTION_TOKEN in .env file")
        sys.exit(1)

    await test_call_tool()


if __name__ == "__main__":
    asyncio.run(main())
