from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class TopicCreateRequest(BaseModel):
    """创建选题请求"""
    title: str = Field(..., min_length=1, max_length=200, description="选题标题")
    description: str = Field(..., min_length=1, description="选题描述")
    major_id: int = Field(..., gt=0, description="专业ID")
    max_students: int = Field(..., ge=1, le=10, description="最大学生数，1-10")
    academic_year: str = Field(..., pattern=r'^\d{4}-\d{4}$', description="学年，格式：2024-2025")
    term: int = Field(..., ge=1, le=2, description="学期：1=上学期，2=下学期")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("选题标题不能为空")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("选题描述不能为空")
        if len(v) < 10:
            raise ValueError("选题描述至少需要10个字符")
        return v


class TopicUpdateRequest(BaseModel):
    """更新选题请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="选题标题")
    description: Optional[str] = Field(None, min_length=1, description="选题描述")
    major_id: Optional[int] = Field(None, gt=0, description="专业ID")
    max_students: Optional[int] = Field(None, ge=1, le=10, description="最大学生数")
    academic_year: Optional[str] = Field(None, pattern=r'^\d{4}-\d{4}$', description="学年，格式：2024-2025")
    term: Optional[int] = Field(None, ge=1, le=2, description="学期：1=上学期，2=下学期")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("选题标题不能为空")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("选题描述不能为空")
            if len(v) < 10:
                raise ValueError("选题描述至少需要10个字符")
        return v


class TopicListQuery(BaseModel):
    """选题列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    status: Optional[int] = Field(None, description="状态筛选: 0=草稿,1=发布,2=锁定,3=归档")
    major_id: Optional[int] = Field(None, gt=0, description="专业ID筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索（标题/描述）")
    academic_year: Optional[str] = Field(None, description="学年筛选")
    term: Optional[int] = Field(None, ge=1, le=2, description="学期筛选")


class TopicResponse(BaseModel):
    """选题响应"""
    id: int
    title: str
    description: str
    tutor_id: int
    tutor_name: str
    major_id: int
    major_name: str
    department_name: str
    status: int  # 0=草稿,1=发布,2=锁定,3=归档
    max_students: int
    current_students: int
    academic_year: str
    term: int
    published_at: Optional[datetime]
    locked_at: Optional[datetime]
    archived_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class TopicListResponse(BaseModel):
    """选题列表响应"""
    total: int
    page: int
    page_size: int
    items: list[TopicResponse]
