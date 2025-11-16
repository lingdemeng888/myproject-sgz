"""
Admin API 路由集合
"""
from fastapi import APIRouter
from app.api.v1.admin import users, logs

admin_router = APIRouter(prefix="/admin", tags=["管理员"])
admin_router.include_router(users.router)
admin_router.include_router(logs.router)
