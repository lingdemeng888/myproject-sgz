"""
用户相关的Pydantic模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class StudentRegisterRequest(BaseModel):
    """学生注册请求"""
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    real_name: str = Field(..., min_length=1, max_length=64, description="真实姓名")
    student_no: str = Field(..., min_length=1, max_length=64, description="学号")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    primary_major_id: int = Field(..., gt=0, description="主修专业ID")
    email: Optional[str] = Field(None, max_length=128, description="电子邮箱")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式：只允许字母、数字、下划线"""
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @field_validator('real_name', 'student_no')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """去除首尾空格"""
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """验证邮箱格式"""
        if v is None:
            return v
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('邮箱格式不正确')
        return v


class TutorRegisterRequest(BaseModel):
    """导师注册请求"""
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    real_name: str = Field(..., min_length=1, max_length=64, description="真实姓名")
    teacher_no: str = Field(..., min_length=1, max_length=64, description="教师编号")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    department_id: int = Field(..., gt=0, description="所属院系ID")
    email: Optional[str] = Field(None, max_length=128, description="电子邮箱")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式：只允许字母、数字、下划线"""
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    @field_validator('real_name', 'teacher_no')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """去除首尾空格"""
        return v.strip()

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """验证邮箱格式"""
        if v is None:
            return v
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('邮箱格式不正确')
        return v


class UserRegisterResponse(BaseModel):
    """用户注册响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., description="真实姓名")
    student_no: Optional[str] = Field(None, description="学号")
    teacher_no: Optional[str] = Field(None, description="教师编号")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="电子邮箱")
    department_id: Optional[int] = Field(None, description="所属院系ID")
    primary_major_id: Optional[int] = Field(None, description="主修专业ID")
    status: int = Field(..., description="状态（1：启用，0：禁用）")

    class Config:
        from_attributes = True


class UserListQuery(BaseModel):
    """管理员用户列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    role_key: Optional[str] = Field(None, description="角色筛选: ADMIN/TUTOR/STUDENT")
    department_id: Optional[int] = Field(None, gt=0, description="按院系筛选")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态筛选: 1=启用, 0=禁用")
    keyword: Optional[str] = Field(None, max_length=100, description="关键词搜索（用户名/姓名/学号/工号）")
    
    @field_validator('role_key')
    @classmethod
    def validate_role_key(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ['ADMIN', 'TUTOR', 'STUDENT']:
            raise ValueError("角色只能是ADMIN/TUTOR/STUDENT")
        return v


class UserUpdateStatusRequest(BaseModel):
    """管理员更新用户状态请求"""
    status: int = Field(..., ge=0, le=1, description="状态: 1=启用, 0=禁用")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: int) -> int:
        if v not in [0, 1]:
            raise ValueError("状态只能是0(禁用)或1(启用)")
        return v


class UserDetailResponse(BaseModel):
    """用户详情响应（管理员查看）"""
    id: int
    username: str
    real_name: str
    student_no: Optional[str] = None
    teacher_no: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    primary_major_id: Optional[int] = None
    major_name: Optional[str] = None
    status: int
    status_name: str
    roles: list[str] = Field(default_factory=list, description="角色key列表")
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    page: int
    page_size: int
    items: list[UserDetailResponse]


class AssignRoleRequest(BaseModel):
    """分配角色请求"""
    role_id: int = Field(..., gt=0, description="角色ID")
