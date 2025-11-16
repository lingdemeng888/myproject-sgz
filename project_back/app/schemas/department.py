"""
系部数据验证模型
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class DepartmentBase(BaseModel):
    """系部基础字段"""
    dept_code: str = Field(..., min_length=1, max_length=32, description="系部编码")
    name: str = Field(..., min_length=1, max_length=128, description="系部名称")
    status: int = Field(1, ge=0, le=1, description="状态：1=启用，0=停用")


class DepartmentCreate(DepartmentBase):
    """创建系部"""
    @field_validator('dept_code', 'name')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('不能为空或仅包含空格')
        return v.strip()


class DepartmentUpdate(BaseModel):
    """更新系部（所有字段可选）"""
    dept_code: Optional[str] = Field(None, min_length=1, max_length=32)
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    status: Optional[int] = Field(None, ge=0, le=1)

    @field_validator('dept_code', 'name')
    @classmethod
    def not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError('不能为空或仅包含空格')
        return v.strip() if v else v


class DepartmentResponse(DepartmentBase):
    """系部响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentListQuery(BaseModel):
    """系部列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(None, description="搜索关键字（编码/名称）")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态筛选")
