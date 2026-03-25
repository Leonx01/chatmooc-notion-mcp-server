"""
直接测试 MCP HTTP 连接，确认 headers 是否正确传递
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "ntn_xxxxx")
MCP_SERVER_URL = "http://localhost:3000/mcp"


async def test_with_mcp_client():
    """使用原生 mcp.client 测试"""
    print("=" * 50)
    print("使用原生 MCP HTTP Client 测试")
    print("=" * 50)

    try:
        from mcp.client.streamable_http import streamablehttp_client
        from mcp import ClientSession

        print(f"Notion Token: {NOTION_TOKEN[:15]}...")
        print(f"URL: {MCP_SERVER_URL}")
        print()

        # 创建 HTTP 连接，带自定义 headers
        async with streamablehttp_client(
            MCP_SERVER_URL,
            headers={
                "Authorization": f"Bearer {NOTION_TOKEN}"
            }
        ) as (read_stream, write_stream, _):
            print("✅ HTTP 连接成功")

            # 创建 MCP 会话
            async with ClientSession(read_stream, write_stream) as session:
                print("✅ MCP 会话创建成功")

                # 初始化
                init_result = await session.initialize()
                print(f"✅ MCP 初始化成功")
                print(f"   Server: {init_result.serverInfo.name}")
                print()

                # 获取工具列表
                print("正在获取工具列表...")
                tools = await session.list_tools()
                print(f"✅ 获取到 {len(tools.tools)} 个工具:")
                for tool in tools.tools[:5]:
                    print(f"  - {tool.name}")
                if len(tools.tools) > 5:
                    print(f"  ... 还有 {len(tools.tools) - 5} 个")
                print()

                # 尝试调用一个工具
                print("测试调用 search...")
                try:
                    result = await session.call_tool(
                        "API-post-search",
                        {"query": ""}
                    )
                    print(f"✅ 调用成功!")
                    # 解析结果
                    if result.content:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            import json
                            data = json.loads(content.text)
                            print(f"   找到 {len(data.get('results', []))} 个结果")
                except Exception as e:
                    print(f"⚠️  调用失败: {e}")

    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请先安装: pip install mcp python-dotenv")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def test_langgraph_client():
    """测试 langchain_mcp_adapters 是否正确传递 headers"""
    print("=" * 50)
    print("使用 LangGraph MultiServerMCPClient 测试")
    print("=" * 50)

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        print(f"Notion Token: {NOTION_TOKEN[:15]}...")
        print()

        # 方式一：尝试在顶层传 headers
        client = MultiServerMCPClient({
            "notion": {
                "transport": "http",
                "url": MCP_SERVER_URL,
                "headers": {  # 这里传 headers
                    "Authorization": f"Bearer {NOTION_TOKEN}"
                }
            }
        })

        print("正在获取工具...")
        tools = await client.get_tools()
        print(f"✅ 获取到 {len(tools)} 个工具")

        # 尝试调用第一个工具
        if tools:
            print(f"\n测试调用工具: {tools[0].name}")
            try:
                result = await tools[0].ainvoke({})
                print(f"✅ 调用成功: {result[:100]}...")
            except Exception as e:
                print(f"⚠️  调用失败: {e}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def main():
    print("MCP HTTP Headers 测试")
    print()

    # 先测试原生客户端
    await test_with_mcp_client()
    print()

    # 再测试 LangGraph 客户端
    await test_langgraph_client()


if __name__ == "__main__":
    asyncio.run(main())
