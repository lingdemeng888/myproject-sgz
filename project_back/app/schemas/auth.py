"""
认证相关的Pydantic模式
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class UserInfo(BaseModel):
    """用户基本信息"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., description="真实姓名")
    roles: List[str] = Field(..., description="角色列表")
    status: int = Field(..., description="状态（1：启用，0：禁用）")
    student_no: Optional[str] = Field(None, description="学号")
    teacher_no: Optional[str] = Field(None, description="教师编号")
    department_id: Optional[int] = Field(None, description="所属院系ID")
    primary_major_id: Optional[int] = Field(None, description="主修专业ID")

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(default=86400, description="过期时间（秒），默认24小时")
    user: UserInfo = Field(..., description="用户基本信息")
