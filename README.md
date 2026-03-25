# Notion MCP Server (Multi-Tenant Fork)

这是一个支持**多租户架构**的 Notion MCP Server 分支。与官方版本不同，本分支允许通过 HTTP 请求头动态传入 Notion API Token，使多个用户可以连接各自的 Notion 工作区，而无需为每个用户部署独立的服务器实例。

## 核心特性

- **多租户支持** - 每个请求可携带不同的 Notion Token，支持多用户场景
- **HTTP 传输模式** - 支持 Streamable HTTP 传输，便于 Web 应用集成
- **动态认证** - 支持 `X-Notion-Token` 头或 `Authorization` 头传递 Token
- **LangGraph 兼容** - 完美支持 LangGraph / langchain-mcp-adapters

## 快速开始

### Docker 部署（推荐）

```yaml
# docker-compose.yml
services:
  notion-mcp-server:
    build: .
    ports:
      - "3000:3000"
    command: ["--transport", "http", "--port", "3000", "--auth-token", "your-mcp-secret"]
```

启动：

```bash
docker compose up -d
```

**注意**：不需要设置 `NOTION_TOKEN` 环境变量，Token 将在请求时动态传入。

### 本地运行

```bash
# 安装依赖
npm install

# 构建
npm run build

# 启动 HTTP 模式
npm start -- --transport http --port 3000 --auth-token your-mcp-secret
```

## 使用方式

### 方式一：分离认证（推荐用于生产）

MCP 连接认证和 Notion API 认证分离：

```bash
curl -H "Authorization: Bearer your-mcp-auth-token" \
     -H "X-Notion-Token: ntn_xxxxx" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     http://localhost:3000/mcp
```

### 方式二：合并认证（开发便利）

直接用 Notion Token 作为 Bearer Token：

```bash
curl -H "Authorization: Bearer ntn_xxxxx" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     http://localhost:3000/mcp
```

## LangGraph 集成

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async with MultiServerMCPClient({
    "notion": {
        "transport": "http",
        "url": "http://localhost:3000/mcp",
        "headers": {
            "Authorization": "Bearer your-mcp-auth-token",
            "X-Notion-Token": "ntn_xxxxx"  # 每个用户不同的 Token
        }
    }
}) as client:
    tools = await client.get_tools()
    agent = create_react_agent("claude-sonnet-4-6", tools)

    # 使用 Agent 操作 Notion
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "列出我的所有数据库"}]
    })
```

## 获取 Notion Token

1. 访问 [Notion Integration](https://www.notion.so/profile/integrations)
2. 创建新的 Internal Integration
3. 复制 Token（格式为 `ntn_xxxx`）
4. 在要访问的页面点击「...」→「Connect to integration」授权

## 命令行参数

```
Options:
  --transport <type>     传输模式: stdio 或 http (默认: stdio)
  --port <number>        HTTP 模式端口 (默认: 3000)
  --auth-token <token>   MCP 连接认证 Token
  --disable-auth         禁用认证（仅开发使用）
  --help, -h             显示帮助
```

## 与官方版本的区别

| 特性 | 官方版本 | 本分支 |
|-----|---------|--------|
| Token 配置 | 环境变量 `NOTION_TOKEN` | HTTP 头动态传入 |
| 多租户 | 不支持 | 支持 |
| 适用场景 | 个人/单工作区 | SaaS/多用户应用 |
| 部署方式 | 每个用户独立部署 | 单个实例服务多用户 |

## 原项目

本项目基于 [Notion 官方 MCP Server](https://github.com/makenotion/notion-mcp-server) 修改，感谢 Notion 团队的开源贡献。

## License

MIT
