from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.exceptions import (
    BusinessException,
    http_exception_handler,
    validation_exception_handler,
    business_exception_handler,
    global_exception_handler
)
from app.api.v1 import api_router

settings = get_settings()

app = FastAPI(
    title="毕业论文选题管理系统API",
    version="1.0.0",
    description="""
## 苏州高等职业技术学校毕业论文选题管理系统API文档

### 📋 状态码约定

| 状态码 | 说明 |
|-------|------|
| **200** | 请求成功 |
| **400** | 请求参数错误或业务规则限制 |
| **401** | 未认证或Token无效 |
| **403** | 权限不足 |
| **404** | 资源不存在 |
| **500** | 服务器内部错误 |

### 📦 响应格式

所有接口统一返回以下格式：

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {...}
}
```

### 🔐 认证方式

使用JWT Bearer Token认证，在请求头添加：

```
Authorization: Bearer <your_token>
```

获取Token：调用 `POST /api/v1/auth/login` 接口

### 👥 角色说明

- **ADMIN** (管理员)：用户管理、系统配置、查看所有数据
- **TUTOR** (导师)：发布选题、审批申请、评审论文、指导学生
- **STUDENT** (学生)：浏览选题、提交申请、撰写论文、上传附件

### 📚 主要功能模块

1. **认证模块**：用户注册、登录、Token刷新
2. **选题管理**：导师发布选题、学生浏览申请
3. **申请审批**：导师审批学生申请（含并发控制）
4. **论文管理**：学生提交论文、导师评审
5. **文件管理**：附件上传下载（SHA256去重）
6. **用户管理**：管理员管理用户和角色
7. **操作日志**：关键操作审计追踪
    """,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_url="/api/openapi.json" if settings.debug else None,
    debug=settings.debug
)

# 配置CORS中间件
origins = settings.cors_allow_origins.split(",") if settings.cors_allow_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 注意: 不再使用 Base.metadata.create_all()，改用 Alembic 管理数据库迁移
# 请执行: alembic upgrade head 来应用数据库迁移

# 注册API路由
app.include_router(api_router)

@app.get("/health", summary="健康检查", tags=["系统"])
async def health():
    """健康检查接口"""
    return {"status": "ok", "message": "服务运行正常"}
