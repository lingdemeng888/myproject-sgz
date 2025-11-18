"""
论文相关Schema定义
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.constants.status import PaperStatus


class PaperCreateRequest(BaseModel):
    """创建论文请求"""
    topic_id: int = Field(..., gt=0, description="选题ID")
    title: str = Field(..., min_length=5, max_length=255, description="论文标题")
    abstract: Optional[str] = Field(None, max_length=2000, description="摘要")
    keywords: Optional[str] = Field(None, max_length=255, description="关键词，多个用逗号分隔")
    academic_year: str = Field(..., pattern=r'^\d{4}-\d{4}$', description="学年，格式：2024-2025")
    term: int = Field(..., ge=1, le=2, description="学期: 1=上学期, 2=下学期")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """验证论文标题"""
        v = v.strip()
        if not v:
            raise ValueError("论文标题不能为空")
        if len(v) < 5:
            raise ValueError("论文标题至少需要5个字符")
        if len(v) > 255:
            raise ValueError("论文标题不能超过255个字符")
        return v

    @field_validator('abstract')
    @classmethod
    def validate_abstract(cls, v: Optional[str]) -> Optional[str]:
        """验证摘要"""
        if v:
            v = v.strip()
            if len(v) > 2000:
                raise ValueError("摘要不能超过2000个字符")
            return v if v else None
        return None

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v: Optional[str]) -> Optional[str]:
        """验证关键词"""
        if v:
            v = v.strip()
            if len(v) > 255:
                raise ValueError("关键词不能超过255个字符")
            return v if v else None
        return None


class PaperVersionCreateRequest(BaseModel):
    """创建论文版本请求"""
    content_text: Optional[str] = Field(None, description="正文内容")
    content_format: int = Field(0, ge=0, le=3, description="内容格式: 0=无,1=markdown,2=html,3=text")
    notes: Optional[str] = Field(None, max_length=255, description="版本说明备注")

    @field_validator('content_text')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """验证正文内容"""
        if v:
            v = v.strip()
            return v if v else None
        return None

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """验证备注"""
        if v:
            v = v.strip()
            if len(v) > 255:
                raise ValueError("备注不能超过255个字符")
            return v if v else None
        return None


class PaperVersionResponse(BaseModel):
    """论文版本响应"""
    id: int
    paper_id: int
    version_no: int
    content: str | None  # 论文内容（详情时返回）
    content_format: int
    content_format_name: str  # 格式名称
    is_final: int
    submitted_by: int
    submitted_by_name: str  # 提交人姓名
    submitted_at: datetime
    notes: str | None
    attachments: list = []  # 附件列表
    review_comment: str | None = None  # 导师评审意见
    reviewed_by: int | None = None  # 评审导师ID
    reviewed_by_name: str | None = None  # 评审导师姓名
    reviewed_at: datetime | None = None  # 评审时间

    model_config = {
        "from_attributes": True
    }


class PaperResponse(BaseModel):
    """论文详情响应"""
    id: int
    topic_id: int
    topic_title: str  # 关联选题标题
    student_id: int
    student_name: str  # 学生姓名
    student_no: str | None  # 学号
    title: str
    abstract: str | None
    keywords: str | None
    status: int
    status_name: str  # 状态名称
    academic_year: str
    term: int
    term_name: str  # 学期名称
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    versions: list[PaperVersionResponse]  # 版本列表

    model_config = {
        "from_attributes": True
    }


class PaperListQuery(BaseModel):
    """论文列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    status: Optional[int] = Field(None, description="状态筛选")
    academic_year: Optional[str] = Field(None, description="学年筛选")
    term: Optional[int] = Field(None, ge=1, le=2, description="学期筛选")


class PaperListItemResponse(BaseModel):
    """论文列表项响应（不含版本列表）"""
    id: int
    topic_id: int
    topic_title: str
    student_id: int
    student_name: str
    student_no: str | None
    title: str
    status: int
    status_name: str
    academic_year: str
    term: int
    term_name: str
    version_count: int  # 版本数量
    latest_version_no: int | None  # 最新版本号
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class PaperListResponse(BaseModel):
    """论文列表响应"""
    total: int
    page: int
    page_size: int
    items: list[PaperListItemResponse]


class PaperReviewRequest(BaseModel):
    """导师评审论文请求"""
    status: int = Field(..., ge=2, le=4, description="评审状态: 2=评审中, 3=待修改, 4=通过")
    review_comment: str = Field(..., min_length=1, max_length=2000, description="评审意见")

    @field_validator('review_comment')
    @classmethod
    def validate_review_comment(cls, v: str, info) -> str:
        """验证评审意见长度规则"""
        v = v.strip()
        if not v:
            raise ValueError("评审意见不能为空")
        
        # 根据状态验证评审意见长度
        status = info.data.get('status')
        if status == 4:  # 通过
            if len(v) < 20:
                raise ValueError("通过评审意见至少需要20个字符")
        elif status == 3:  # 待修改
            if len(v) < 50:
                raise ValueError("待修改评审意见至少需要50个字符，请详细说明修改要求")
        
        if len(v) > 2000:
            raise ValueError("评审意见不能超过2000个字符")
        
        return v


class TutorPaperListQuery(BaseModel):
    """导师查询学生论文列表参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    status: Optional[int] = Field(None, description="状态筛选")
    academic_year: Optional[str] = Field(None, description="学年筛选")
    term: Optional[int] = Field(None, ge=1, le=2, description="学期筛选")
    student_name: Optional[str] = Field(None, max_length=50, description="学生姓名模糊搜索")
