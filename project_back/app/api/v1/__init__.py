"""
API v1路由集合
"""
from fastapi import APIRouter
from app.core.config import get_settings
from app.api.v1 import departments, majors, auth, test_permissions, topics, student_topics, tutor_applications, student_papers, upload, tutor_papers, admin

settings = get_settings()
api_router = APIRouter(prefix="/api/v1")

# ========== 认证模块 ==========
api_router.include_router(auth.router)

# ========== 基础数据模块 ==========
api_router.include_router(departments.router)
api_router.include_router(majors.router)

# ========== 学生模块 ==========
api_router.include_router(student_topics.router, prefix="/student/topics")
api_router.include_router(student_papers.router, prefix="/student/papers")

# ========== 导师模块 ==========
api_router.include_router(topics.router, prefix="/tutor/topics")
api_router.include_router(tutor_applications.router, prefix="/tutor/applications")
api_router.include_router(tutor_papers.router, prefix="/tutor/papers")

# ========== 管理员模块 ==========
api_router.include_router(admin.admin_router)

# ========== 文件模块 ==========
api_router.include_router(upload.router)

# ========== 测试模块（仅开发环境） ==========
if settings.debug:
    api_router.include_router(test_permissions.router)

