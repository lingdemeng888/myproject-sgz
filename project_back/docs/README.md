# API文档目录

本目录用于存放API相关文档。

## 文件说明

### openapi.json
OpenAPI 3.0 规范文件，可通过以下方式获取：

```powershell
# 启动开发服务器
cd project_back
uvicorn app.main:app --reload --port 8000

# 下载OpenAPI规范文件
Invoke-WebRequest -Uri http://localhost:8000/api/openapi.json -OutFile docs/openapi.json
```

**注意：** `openapi.json` 文件已添加到 `.gitignore`，不会纳入版本控制。

## 使用OpenAPI文件

### Postman
1. 打开Postman
2. 点击 Import
3. 选择 `openapi.json` 文件
4. 自动生成完整的API Collection

### Swagger Editor
1. 访问 https://editor.swagger.io/
2. 导入 `openapi.json` 文件
3. 在线编辑和预览

### VS Code
推荐安装插件：
- **OpenAPI (Swagger) Editor** - 语法高亮和验证
- **REST Client** - 直接在VS Code中测试API

## 在线文档访问

**开发环境：**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

**生产环境：**
- API文档已禁用（安全考虑）
- 需要OpenAPI文件请联系开发团队
