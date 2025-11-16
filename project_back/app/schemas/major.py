"""
专业数据验证模型
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class MajorBase(BaseModel):
    """专业基础字段"""
    major_code: str = Field(..., min_length=1, max_length=32, description="专业编码")
    name: str = Field(..., min_length=1, max_length=128, description="专业名称")
    status: int = Field(1, ge=0, le=1, description="状态：1=启用，0=停用")


class MajorCreate(MajorBase):
    """创建专业"""
    department_id: int = Field(..., gt=0, description="所属系部ID")
    
    @field_validator('major_code', 'name')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('不能为空或仅包含空格')
        return v.strip()


class MajorUpdate(BaseModel):
    """更新专业（所有字段可选）"""
    department_id: Optional[int] = Field(None, gt=0)
    major_code: Optional[str] = Field(None, min_length=1, max_length=32)
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    status: Optional[int] = Field(None, ge=0, le=1)

    @field_validator('major_code', 'name')
    @classmethod
    def not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError('不能为空或仅包含空格')
        return v.strip() if v else v


class MajorResponse(MajorBase):
    """专业响应（含系部信息）"""
    id: int
    department_id: int
    department_name: str = Field(..., description="系部名称")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MajorListQuery(BaseModel):
    """专业列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    department_id: Optional[int] = Field(None, gt=0, description="按系部筛选")
    keyword: Optional[str] = Field(None, description="搜索关键字（编码/名称）")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态筛选")
