"""
选题申请相关Schema定义
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.constants.status import ApplicationStatus


class ApplicationCreateRequest(BaseModel):
    """学生创建申请请求"""
    topic_id: int = Field(..., gt=0, description="选题ID")
    application_reason: str = Field(..., min_length=10, max_length=500, description="申请理由")

    @field_validator('application_reason')
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """验证申请理由"""
        v = v.strip()
        if not v:
            raise ValueError("申请理由不能为空")
        if len(v) < 10:
            raise ValueError("申请理由至少需要10个字符")
        if len(v) > 500:
            raise ValueError("申请理由不能超过500个字符")
        return v


class ApplicationResponse(BaseModel):
    """申请详情响应"""
    id: int
    topic_id: int
    topic_title: str  # 关联选题标题
    student_id: int
    student_name: str  # 关联学生姓名
    student_no: str | None  # 学号
    status: int  # 0=待审批,1=通过,2=拒绝,3=取消
    status_name: str  # 状态名称（中文）
    application_reason: str | None
    decision_by: int | None
    decision_by_name: str | None  # 审批人姓名
    decision_at: datetime | None
    decision_comment: str | None
    academic_year: str | None  # 学年
    term: int | None  # 学期
    paper_id: int | None  # 关联的论文ID（如果已创建）
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ApplicationListQuery(BaseModel):
    """申请列表查询参数（学生端）"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    status: Optional[int] = Field(None, description="状态筛选: 0=待审批,1=通过,2=拒绝,3=取消")


class ApplicationListResponse(BaseModel):
    """申请列表响应"""
    total: int
    page: int
    page_size: int
    items: list[ApplicationResponse]


class StudentTopicListQuery(BaseModel):
    """学生端选题列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    major_id: Optional[int] = Field(None, gt=0, description="专业ID筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索（标题/描述）")
    # 注意：不暴露status参数，后端强制status=1（已发布）


class StudentTopicResponse(BaseModel):
    """学生端选题详情响应"""
    id: int
    title: str
    description: str
    tutor_id: int
    tutor_name: str
    major_id: int
    major_name: str
    department_name: str
    max_students: int
    current_students: int
    available_slots: int  # 剩余名额（计算字段）
    academic_year: str
    term: int
    published_at: datetime | None
    created_at: datetime
    # 注意：不返回status字段（学生端只能看到已发布的）

    model_config = {
        "from_attributes": True
    }


class StudentTopicListResponse(BaseModel):
    """学生端选题列表响应"""
    total: int
    page: int
    page_size: int
    items: list[StudentTopicResponse]


class ApplicationDecisionRequest(BaseModel):
    """导师审批申请请求"""
    status: int = Field(..., description="审批决策: 1=通过, 2=拒绝")
    decision_comment: str = Field(..., min_length=1, max_length=500, description="审批意见")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: int) -> int:
        """验证审批状态"""
        if v not in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]:  # [1, 2]
            raise ValueError("审批状态只能是1(通过)或2(拒绝)")
        return v

    @field_validator('decision_comment')
    @classmethod
    def validate_comment(cls, v: str, info) -> str:
        """验证审批意见"""
        v = v.strip()
        if not v:
            raise ValueError("审批意见不能为空")
        
        # 拒绝时必须填写详细理由（至少20字符）
        status = info.data.get('status')
        if status == ApplicationStatus.REJECTED and len(v) < 20:
            raise ValueError("拒绝申请时，审批意见至少需要20个字符")
        
        if len(v) > 500:
            raise ValueError("审批意见不能超过500个字符")
        return v


class TutorApplicationListQuery(BaseModel):
    """导师端申请列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    status: Optional[int] = Field(None, description="状态筛选: 0=待审批,1=通过,2=拒绝")
    topic_id: Optional[int] = Field(None, gt=0, description="按选题ID筛选")
    student_name: Optional[str] = Field(None, description="学生姓名搜索（模糊）")
