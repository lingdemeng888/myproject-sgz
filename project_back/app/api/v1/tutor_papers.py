"""
导师端论文管理API
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import BusinessException
from app.services.paper_service import PaperService
from app.schemas.paper import (
    PaperReviewRequest,
    TutorPaperListQuery,
    PaperResponse,
    PaperListResponse
)
from app.models.user import User

router = APIRouter(prefix="/tutor/papers", tags=["导师-论文管理"])


@router.get("", response_model=PaperListResponse, summary="查询指导学生的论文列表")
def list_student_papers(
    page: int = 1,
    page_size: int = 10,
    status: int | None = None,
    academic_year: str | None = None,
    term: int | None = None,
    student_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导师查询指导学生的论文列表
    
    - **page**: 页码，默认1
    - **page_size**: 每页数量，默认10
    - **status**: 状态筛选（可选）
    - **academic_year**: 学年筛选，格式：2024-2025（可选）
    - **term**: 学期筛选，1=上学期，2=下学期（可选）
    - **student_name**: 学生姓名模糊搜索（可选）
    """
    # 验证导师角色
    if current_user.role_id != 2:  # 2=导师
        raise BusinessException(message="只有导师可以访问此接口", code=403)
    
    # 构建查询参数
    query = TutorPaperListQuery(
        page=page,
        page_size=page_size,
        status=status,
        academic_year=academic_year,
        term=term,
        student_name=student_name
    )
    
    # 调用服务层
    return PaperService.list_student_papers(
        db=db,
        tutor_id=current_user.id,
        query=query
    )


@router.put("/{paper_id}/review", response_model=PaperResponse, summary="评审论文")
def review_paper(
    paper_id: int,
    data: PaperReviewRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导师评审论文
    
    - **paper_id**: 论文ID
    - **status**: 评审状态，2=评审中，3=待修改，4=通过
    - **review_comment**: 评审意见（通过≥20字符，待修改≥50字符）
    
    状态流转规则：
    - 已提交（1）→ 评审中（2）/待修改（3）/通过（4）
    - 评审中（2）→ 待修改（3）/通过（4）
    - 待修改（3）→ 评审中（2）/通过（4）
    - 通过（4）→ 不可再评审
    """
    # 验证导师角色
    if current_user.role_id != 2:  # 2=导师
        raise BusinessException(message="只有导师可以评审论文", code=403)
    
    # 获取IP地址
    ip_address = request.client.host if request.client else None
    
    # 调用服务层
    paper = PaperService.review_paper(
        db=db,
        paper_id=paper_id,
        tutor_id=current_user.id,
        status=data.status,
        review_comment=data.review_comment,
        ip_address=ip_address
    )
    
    # 返回完整论文详情
    return PaperService.get_paper_detail_for_tutor(
        db=db,
        paper_id=paper.id,
        tutor_id=current_user.id
    )


@router.get("/{paper_id}", response_model=PaperResponse, summary="查看论文详情")
def get_paper_detail(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导师查看论文详情（含所有版本）
    
    - **paper_id**: 论文ID
    """
    # 验证导师角色
    if current_user.role_id != 2:  # 2=导师
        raise BusinessException(message="只有导师可以访问此接口", code=403)
    
    # 调用服务层
    return PaperService.get_paper_detail_for_tutor(
        db=db,
        paper_id=paper_id,
        tutor_id=current_user.id
    )
