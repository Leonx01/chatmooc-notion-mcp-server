# Notion MCP Server (Multi-Tenant Fork)

支持**多租户架构**的 Notion MCP Server。与官方版本不同，本分支允许通过 HTTP 请求头动态传入 Notion API Token，使多个用户可以连接各自的 Notion 工作区，无需为每个用户部署独立实例。

## 核心特性

- **多租户支持** - 每个请求可携带不同 Notion Token
- **双认证模式** - 支持分离认证（生产）和合并认证（开发）
- **HTTP 传输** - Streamable HTTP 模式，便于 Web 应用集成
- **LangGraph 兼容** - 完美支持 langchain-mcp-adapters

---

## 快速开始

### Docker 部署

本项目提供两个 Docker Compose 配置，对应两种认证方式：

#### 方式一：分离认证（生产/多租户）

使用 `docker-compose.yml`：

```yaml
services:
  notion-mcp-server:
    build: .
    ports:
      - "3000:3000"
    command: ["--transport", "http", "--port", "3000", "--auth-token", "your-mcp-secret"]
```

启动：

```bash
docker compose -f docker-compose.yml up -d
```

**特点**：
- 需要 `--auth-token` 设置 MCP 服务器认证密钥
- 客户端需提供两个 Header：`Authorization`（MCP认证）+ `X-Notion-Token`（Notion认证）
- 适合多租户场景，一个服务支持多个 Notion 用户

#### 方式二：合并认证（开发/单用户）

使用 `docker-compose.simple.yml`：

```yaml
services:
  notion-mcp-server:
    build: .
    ports:
      - "3000:3000"
    command: ["--transport", "http", "--port", "3000", "--disable-auth"]
```

启动：

```bash
docker compose -f docker-compose.simple.yml up -d
```

**特点**：
- 使用 `--disable-auth` 关闭 MCP 服务器认证
- 客户端只需一个 Header：`Authorization: Bearer <ntn_xxxxx>`
- 适合个人开发测试

> **注意**：两种方式都不需要设置 `NOTION_TOKEN` 环境变量，Token 通过请求头动态传入！

### 本地运行

```bash
npm install
npm run build
npm start -- --transport http --port 3000 --auth-token your-mcp-secret
```

---

## 两种认证方式详解

本服务支持两种认证模式，根据你的使用场景选择：

### 方式一：分离认证（推荐用于生产/多租户）

**原理**：MCP 服务器认证 和 Notion API 认证 完全分离

```
┌─────────────┐  Authorization  ┌─────────────┐  X-Notion-Token  ┌─────────────┐
│  LangGraph  │ ──────────────> │  MCP Server │ ───────────────> │  Notion API │
│   Client    │  (你的服务密钥)  │   (本服务)   │  (用户Notion密钥) │   (官方)    │
└─────────────┘                 └─────────────┘                  └─────────────┘
```

**Headers**：
- `Authorization: Bearer <mcp-auth-token>` —— 验证有权连接此 MCP 服务器（由 `--auth-token` 参数设置）
- `X-Notion-Token: <notion-token>` —— 验证有权访问哪个 Notion 工作区（每个用户不同）

**cURL 示例**：

```bash
curl -H "Authorization: Bearer your-mcp-secret" \
     -H "X-Notion-Token: ntn_xxxxx" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     http://localhost:3000/mcp
```

**LangGraph 示例**：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# 用户 A 使用自己的 Notion Token
async with MultiServerMCPClient({
    "notion": {
        "transport": "http",
        "url": "http://localhost:3000/mcp",
        "headers": {
            "Authorization": "Bearer your-mcp-secret",      # 固定，你的服务密钥
            "X-Notion-Token": "ntn_user_a_token"            # 变化，用户A的Notion
        }
    }
}) as client:
    tools = await client.get_tools()
    agent = create_react_agent("claude-sonnet-4-6", tools)
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "列出我的数据库"}]
    })

# 用户 B 使用不同的 Notion Token，同一个服务器
async with MultiServerMCPClient({
    "notion": {
        "transport": "http",
        "url": "http://localhost:3000/mcp",
        "headers": {
            "Authorization": "Bearer your-mcp-secret",      # 相同的服务密钥
            "X-Notion-Token": "ntn_user_b_token"            # 不同的Notion密钥
        }
    }
}) as client:
    tools = await client.get_tools()
    # ... 操作用户 B 的 Notion
```

**适用场景**：
- ✅ SaaS 应用，多个用户各自连接自己的 Notion
- ✅ 团队协作平台，按用户区分权限
- ✅ 共享 MCP 服务基础设施

---

### 方式二：合并认证（开发便利）

**原理**：直接用 Notion Token 作为 Bearer Token，一举两得

```
┌─────────────┐  Authorization  ┌─────────────┐  (same token)   ┌─────────────┐
│  LangGraph  │ ──────────────> │  MCP Server │ ──────────────> │  Notion API │
│   Client    │  (notion token) │   (本服务)   │                 │   (官方)    │
└─────────────┘                 └─────────────┘                 └─────────────┘
```

**Headers**：
- `Authorization: Bearer <notion-token>` —— 既是 MCP 认证又是 Notion 认证

**cURL 示例**：

```bash
curl -H "Authorization: Bearer ntn_xxxxx" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' \
     http://localhost:3000/mcp
```

**LangGraph 示例**：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async with MultiServerMCPClient({
    "notion": {
        "transport": "http",
        "url": "http://localhost:3000/mcp",
        "headers": {
            # 直接用 Notion Token 作为 Bearer，省一个 Header
            "Authorization": "Bearer ntn_xxxxx"
        }
    }
}) as client:
    tools = await client.get_tools()
    agent = create_react_agent("claude-sonnet-4-6", tools)
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "列出我的数据库"}]
    })
```

**适用场景**：
- ✅ 个人开发测试
- ✅ 单机部署，只服务一个用户
- ✅ 快速原型，懒得配置两个 Token

---

## 对比总结

| 特性 | 方式一（分离） | 方式二（合并） |
|------|--------------|--------------|
| Headers 数量 | 2 个 | 1 个 |
| 多租户支持 | ✅ 支持 | ❌ 不支持 |
| 部署方式 | 一个服务 + 多用户 | 一个服务 + 一个用户 |
| 安全性 | 🔒 高（服务密钥不暴露） | ⚠️ 中（Notion Token 即服务密钥）|
| 适用场景 | 生产/SaaS | 开发/个人 |

---

## 测试验证

运行 `python test_langgraph.py` 后，如果看到类似下面的输出，说明**连接成功**：

```
==================================================
测试方式二：合并认证
==================================================
Notion Token: ntn_12345...
MCP Server: http://localhost:3000/mcp

正在连接 MCP Server...
正在获取工具列表...
✅ 获取到 22 个工具:
  - API-post-search: Search by title...
  - API-get-block-children: Retrieve block children...
  - API-query-data-source: Query a data source...
  ...
✅ 测试通过!
```

> **注意**：工具列表中的 `Error Responses: 400: Bad...` 是 OpenAPI 文档中的**错误说明**，不是实际错误。表示该工具在参数错误时会返回 400 状态码。

---

## 获取 Notion Token

1. 访问 [Notion Integration](https://www.notion.so/profile/integrations)
2. 创建 **Internal Integration**
3. 复制 Token（格式 `ntn_xxxx`）
4. 在目标页面点击「...」→「Connect to integration」授权

---

## 命令行参数

```bash
Options:
  --transport <type>     传输模式: stdio 或 http (默认: stdio)
  --port <number>        HTTP 模式端口 (默认: 3000)
  --auth-token <token>   MCP 连接认证 Token（方式一必需，方式二可选）
  --disable-auth         禁用认证（仅开发使用）
  --help, -h             显示帮助
```

---

## 原项目

基于 [Notion 官方 MCP Server](https://github.com/makenotion/notion-mcp-server) 修改。

## License

MIT
