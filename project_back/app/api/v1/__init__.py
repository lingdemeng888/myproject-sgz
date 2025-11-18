"""
API v1路由集合
"""
from fastapi import APIRouter
from app.api.v1 import departments, majors, auth, topics, student_topics, tutor_applications, student_papers, upload, tutor_papers, admin

api_router = APIRouter(prefix="/api/v1")

# ========== 认证模块 ==========
api_router.include_router(auth.router)

# ========== 基础数据模块 ==========
api_router.include_router(departments.router)
api_router.include_router(majors.router)

# ========== 学生模块 ==========
api_router.include_router(student_topics.router)
api_router.include_router(student_papers.router)

# ========== 导师模块 ==========
api_router.include_router(topics.router)
api_router.include_router(tutor_applications.router)
api_router.include_router(tutor_papers.router)

# ========== 管理员模块 ==========
api_router.include_router(admin.admin_router)

# ========== 文件模块 ==========
api_router.include_router(upload.router)

