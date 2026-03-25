"""
测试 LangGraph Client 连接 Notion MCP Server
用法: python test_langgraph.py
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境变量获取 Token
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
MCP_AUTH_TOKEN = os.getenv("MCP_AUTH_TOKEN", "your-mcp-secret")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp")

async def test_with_merged_auth():
    """测试方式二：合并认证（直接用 Notion Token 作为 Bearer）"""
    print("=" * 50)
    print("测试方式二：合并认证")
    print("=" * 50)

    if not NOTION_TOKEN:
        print("错误：请设置 NOTION_TOKEN 环境变量")
        sys.exit(1)

    print(f"Notion Token: {NOTION_TOKEN[:10]}...")
    print(f"MCP Server: {MCP_SERVER_URL}")
    print()

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        print("正在连接 MCP Server...")

        # 新版本 API：先创建 client，再获取 tools
        client = MultiServerMCPClient({
            "notion": {
                "transport": "http",
                "url": MCP_SERVER_URL,
                "headers": {
                    # 方式二：直接用 Notion Token 作为 Bearer
                    "Authorization": f"Bearer {NOTION_TOKEN}"
                }
            }
        })

        # 获取工具列表
        print("正在获取工具列表...")
        tools = await client.get_tools()
        print(f"✅ 获取到 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")
        print()

        print("✅ 测试通过!")

    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请先安装: pip install langchain-mcp-adapters langgraph")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

async def test_with_separated_auth():
    """测试方式一：分离认证"""
    print("=" * 50)
    print("测试方式一：分离认证")
    print("=" * 50)

    if not NOTION_TOKEN:
        print("错误：请设置 NOTION_TOKEN 环境变量")
        sys.exit(1)

    print(f"MCP Auth Token: {MCP_AUTH_TOKEN[:10]}...")
    print(f"Notion Token: {NOTION_TOKEN[:10]}...")
    print(f"MCP Server: {MCP_SERVER_URL}")
    print()

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        print("正在连接 MCP Server...")

        # 新版本 API：先创建 client，再获取 tools
        client = MultiServerMCPClient({
            "notion": {
                "transport": "http",
                "url": MCP_SERVER_URL,
                "headers": {
                    # 方式一：分离认证
                    "Authorization": f"Bearer {MCP_AUTH_TOKEN}",  # MCP 服务认证
                    "X-Notion-Token": NOTION_TOKEN                # Notion API 认证
                }
            }
        })

        # 获取工具列表
        print("正在获取工具列表...")
        tools = await client.get_tools()
        print(f"✅ 获取到 {len(tools)} 个工具")
        for tool in tools[:5]:  # 只显示前5个
            print(f"  - {tool.name}")
        if len(tools) > 5:
            print(f"  ... 还有 {len(tools) - 5} 个工具")
        print()

        print("✅ 测试通过!")

    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请先安装: pip install langchain-mcp-adapters langgraph")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

async def main():
    print("LangGraph Client 测试脚本")
    print()

    # 检查环境变量
    if not NOTION_TOKEN:
        print("⚠️  请先在 .env 文件中设置 NOTION_TOKEN=ntn_xxxxx")
        print()
        print("示例 .env 文件:")
        print("  NOTION_TOKEN=ntn_xxxxx")
        print("  MCP_AUTH_TOKEN=your-mcp-secret")
        print("  MCP_SERVER_URL=http://localhost:3000/mcp")
        sys.exit(1)

    # 测试方式二（合并认证）
    await test_with_merged_auth()
    print()

    # 测试方式一（分离认证）
    # await test_with_separated_auth()

if __name__ == "__main__":
    asyncio.run(main())
