# 毕业论文选题管理系统 - 后端API

基于 FastAPI + SQLAlchemy 2.0 + Alembic 的后端服务，采用模块化开发，支持学生、导师、管理员三角色业务流程。

## ✨ 项目特性

- **现代架构**: FastAPI + SQLAlchemy 2.0 + Pydantic
- **数据库迁移**: Alembic 版本管理
- **统一响应**: RESTful 标准响应格式
- **异常处理**: 全局异常处理器
- **CORS支持**: 跨域资源共享配置
- **文件上传**: 本地存储（可扩展对象存储）
- **权限控制**: RBAC 角色权限系统

## 📁 目录结构

```
project_back/
├── alembic/              # 数据库迁移脚本
│   ├── versions/        # 迁移版本文件
│   ├── env.py          # 迁移环境配置
│   └── README.md       # Alembic使用说明
├── app/
│   ├── api/            # API路由层（待开发）
│   ├── core/           # 核心配置
│   │   ├── config.py      # 应用配置
│   │   ├── database.py    # 数据库连接
│   │   ├── security.py    # JWT & 密码加密
│   │   └── exceptions.py  # 全局异常处理
│   ├── models/         # SQLAlchemy ORM模型
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── department.py
│   │   └── major.py
│   ├── schemas/        # Pydantic数据验证模型
│   │   └── response.py    # 统一响应格式
│   ├── services/       # 业务逻辑层（待开发）
│   └── main.py         # 应用入口
├── db/
│   ├── schema.sql      # 数据库初始化脚本
│   └── README.md       # 数据库设计文档
├── uploads/            # 文件存储目录
│   ├── papers/        # 论文附件
│   ├── avatars/       # 用户头像
│   └── temp/          # 临时文件
├── .env.example        # 环境变量模板
├── .gitignore
├── alembic.ini         # Alembic配置
├── requirements.txt    # Python依赖
└── README.md          # 本文件
```

## 🚀 快速开始

### 1. 环境准备

```powershell
# 克隆项目后进入后端目录
cd project_back

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```powershell
# 复制环境变量模板
Copy-Item .env.example .env

# 编辑 .env 文件，修改以下配置：
# - DATABASE_URL: 数据库连接地址
# - JWT_SECRET_KEY: JWT密钥（生产环境务必修改）
```

### 3. 初始化数据库

```powershell
# 方式1: 使用已有的 schema.sql（推荐首次使用）
# 在MySQL中执行 db/schema.sql

# 方式2: 使用 Alembic 迁移（模型2完成后）
alembic upgrade head
```

### 4. 运行开发服务器

```powershell
uvicorn app.main:app --reload --port 8000
```

### 5. 访问API文档

**开发环境：**
- Swagger UI: http://127.0.0.1:8000/api/docs
- ReDoc: http://127.0.0.1:8000/api/redoc
- OpenAPI JSON: http://127.0.0.1:8000/api/openapi.json

**注意：** 
- 所有API路径已统一前缀为 `/api/v1`
- 生产环境（`DEBUG=false`）将禁用API文档访问以确保安全
- OpenAPI规范文件可通过上述地址下载用于API测试工具（如Postman）

## 🔌 主要API端点

### 认证模块
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register/student` - 学生注册
- `POST /api/v1/auth/register/tutor` - 导师注册

### 基础数据模块
- `GET /api/v1/departments` - 系部列表
- `GET /api/v1/majors` - 专业列表

### 学生模块
- `GET /api/v1/student/topics` - 浏览选题
- `POST /api/v1/student/topics/applications` - 申请选题
- `POST /api/v1/student/papers` - 创建论文
- `POST /api/v1/student/papers/{id}/submit` - 提交论文

### 导师模块
- `POST /api/v1/tutor/topics` - 发布选题
- `PUT /api/v1/tutor/applications/{id}/approve` - 审批申请
- `POST /api/v1/tutor/papers/{id}/review` - 评审论文

### 管理员模块
- `GET /api/v1/admin/users` - 用户列表
- `GET /api/v1/admin/logs` - 操作日志

### 文件模块
- `POST /api/v1/upload/attachment` - 上传附件
- `GET /api/v1/upload/attachment/{hash}` - 下载附件

## 📦 模块开发进度

### ✅ 已完成模块

- [x] **模块1**: 基础设施搭建
  - Alembic 初始化配置
  - 统一响应格式 (`ApiResponse`, `PaginatedResponse`)
  - 全局异常处理器（HTTP/验证/业务/未知异常）
  - CORS 中间件配置
  - 文件上传目录结构

- [x] **模块2**: ORM模型补全（11个模型）
  - 用户、系部、专业、选题、申请、论文、版本、附件、评审、角色、操作日志

- [x] **模块3**: 系部与专业管理（管理员）
  - 系部/专业的增删改查
  - 数据验证与业务规则

- [x] **模块4**: 用户注册模块
  - 学生注册（专业验证、学号唯一性）
  - 导师注册（职工号唯一性）

- [x] **模块5**: 用户登录模块
  - JWT Token认证
  - 角色权限加载

- [x] **模块6**: 权限控制模块
  - RBAC角色权限系统
  - 接口权限装饰器

- [x] **模块7**: 选题管理（导师）
  - 发布选题（名额控制）
  - 更新选题状态

- [x] **模块8**: 选题申请（学生）
  - 专业匹配验证
  - 重复申请检测

- [x] **模块9**: 申请审批（导师）
  - 悲观锁并发控制
  - 自动拒绝超额申请

- [x] **模块10**: 论文提交（学生）
  - 论文创建与版本管理
  - 正式提交流转

- [x] **模块11**: 文件上传与下载
  - SHA256哈希去重
  - 权限验证与访问控制

- [x] **模块12**: 论文评审（导师）
  - 评审意见与状态流转
  - 操作日志记录

- [x] **模块13**: 用户与日志管理（管理员）
  - 用户状态管理与角色分配
  - 操作日志查询与审计

- [x] **模块14**: 路由集成与API文档
  - 统一路由前缀 `/api/v1`
  - 环境变量控制文档安全
  - 全局错误响应模板

### 🔄 后续模块（待开发）

- [ ] 模块15: 数据统计与导出
- [ ] 模块16: 消息通知系统
- [ ] 模块17: 系统配置管理
- [ ] 模块18: 单元测试与集成测试

## 🔧 Alembic 常用命令

```powershell
# 生成迁移脚本（自动检测模型变化）
alembic revision --autogenerate -m "描述信息"

# 升级到最新版本
alembic upgrade head

# 回滚一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history --verbose
```

## 🎯 API响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 业务数据
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

### 分页响应

```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [
    // 数据列表
  ]
}
```

## 📝 开发规范

### 异常处理

```python
from app.core.exceptions import BusinessException

# 抛出业务异常
raise BusinessException(code=400, message="用户名已存在")
```

### 使用统一响应

```python
from app.schemas.response import ApiResponse

@router.get("/users")
async def list_users() -> ApiResponse[List[UserOut]]:
    users = get_users()
    return ApiResponse(data=users)
```

## 🔐 环境变量说明

| 变量名 | 说明 | 默认值 |
|-------|------|-------|
| `DATABASE_URL` | 数据库连接地址 | - |
| `JWT_SECRET_KEY` | JWT密钥 | PLEASE_CHANGE_ME |
| `JWT_ALGORITHM` | JWT算法 | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token过期时间（分钟） | 1440 |
| `CORS_ALLOW_ORIGINS` | CORS允许源 | * |
| `UPLOAD_DIR` | 文件上传目录 | uploads |
| `MAX_UPLOAD_SIZE` | 最大上传大小（字节） | 52428800 |
| `ALLOWED_EXTENSIONS` | 允许的文件扩展名 | .pdf,.doc,.docx,.zip,.rar |

## 📚 相关文档

- [数据库设计文档](db/README.md)
- [Alembic使用说明](alembic/README.md)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0文档](https://docs.sqlalchemy.org/)

## 🤝 贡献指南

1. 按照模块顺序开发（见开发进度）
2. 每个模块完成后更新此文档
3. 提交前确保代码通过测试
4. 遵循项目代码规范

## 📄 许可证

本项目仅供学习使用。
