# LangGraph Client 测试指南

## 前置条件

1. **启动 MCP Server**
   ```bash
   # Docker 方式
   docker compose up -d

   # 或本地方式
   npm start -- --transport http --port 3000 --auth-token your-mcp-secret
   ```

2. **安装 Python 依赖**
   ```bash
   pip install langchain-mcp-adapters langgraph python-dotenv
   ```

3. **配置 .env 文件**
   ```bash
   cp .env.example .env
   # 编辑 .env 填入你的 NOTION_TOKEN
   ```

## 运行测试

```bash
python test_langgraph.py
```

## 预期输出

```
LangGraph Client 测试脚本

==================================================
测试方式二：合并认证
==================================================
Notion Token: ntn_12345...
MCP Server: http://localhost:3000/mcp

正在连接 MCP Server...
✅ 连接成功!

正在获取工具列表...
✅ 获取到 22 个工具:
  - search: Search for pages and databases...
  - query-data-source: Query a data source...
  ...
```

## 故障排除

| 错误 | 解决方案 |
|-----|---------|
| `Connection refused` | 确认 MCP Server 已启动在 localhost:3000 |
| `Unauthorized` | 检查 Token 是否正确 |
| `ImportError` | 安装依赖: `pip install langchain-mcp-adapters` |
| `403 Forbidden` | 检查 --auth-token 是否匹配 |
