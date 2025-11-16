"""
导师端申请审批API
包含：查询待审批申请、审批通过、审批拒绝
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.application import (
    ApplicationDecisionRequest,
    ApplicationResponse,
    ApplicationListResponse,
    TutorApplicationListQuery
)
from app.services.application_service import ApplicationService
from app.constants.status import ApplicationStatus
from app.core.exceptions import BusinessException

router = APIRouter(prefix="/tutor/applications", tags=["导师-申请审批"])


@router.get("", response_model=ApiResponse[ApplicationListResponse], summary="查询待审批申请")
def list_tutor_applications(
    page: int = 1,
    page_size: int = 10,
    status: int | None = None,
    topic_id: int | None = None,
    student_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    导师端：查询我的选题的申请列表
    
    **筛选条件：**
    - 自动筛选当前导师的选题
    - **status**: 状态筛选（默认显示全部，传0只显示待审批）
    - **topic_id**: 按选题ID筛选
    - **student_name**: 学生姓名模糊搜索
    
    **排序规则：**
    - 按申请时间升序（先来先审）
    
    **响应字段：**
    - 包含学生基本信息（姓名、学号）
    - 包含申请理由
    - 包含选题标题
    - 包含审批信息（已审批的记录）
    """
    query = TutorApplicationListQuery(
        page=page,
        page_size=page_size,
        status=status,
        topic_id=topic_id,
        student_name=student_name
    )
    result = ApplicationService.list_tutor_applications(db, current_user.id, query)
    return ApiResponse.success(data=result)


@router.put("/{id}/approve", response_model=ApiResponse[ApplicationResponse], summary="审批通过")
def approve_application(
    id: int,
    data: ApplicationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    导师端：审批通过申请
    
    **请求参数：**
    - **status**: 必须是1（通过）
    - **decision_comment**: 审批意见（必填，至少1字符）
    
    **业务规则：**
    1. 使用悲观锁检查名额（并发安全）
    2. 审批通过后递增current_students
    3. 名额满时自动锁定选题（status=2）
    4. 自动拒绝该学生的其他待审批申请
    
    **可能的错误：**
    - 400: 该申请已被处理
    - 400: 选题未发布
    - 400: 名额已满
    - 403: 无权限审批
    - 404: 申请不存在
    
    **并发控制：**
    - 使用行级锁（FOR UPDATE）防止超额录取
    - 在锁内重新查询已通过人数，确保数据准确性
    """
    # 验证status必须是1
    if data.status != ApplicationStatus.APPROVED:
        raise BusinessException(message="审批通过接口的status必须为1", code=400)
    
    application = ApplicationService.approve_application(
        db, id, current_user.id, data
    )
    response = ApplicationService._to_application_response(db, application)
    return ApiResponse.success(data=response, message="审批通过成功")


@router.put("/{id}/reject", response_model=ApiResponse[ApplicationResponse], summary="审批拒绝")
def reject_application(
    id: int,
    data: ApplicationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    导师端：审批拒绝申请
    
    **请求参数：**
    - **status**: 必须是2（拒绝）
    - **decision_comment**: 审批意见（必填，至少20字符）
    
    **业务规则：**
    1. 不修改选题人数
    2. 不触发自动锁定
    
    **可能的错误：**
    - 400: 该申请已被处理
    - 400: 审批意见少于20字符
    - 403: 无权限审批
    - 404: 申请不存在
    """
    # 验证status必须是2
    if data.status != ApplicationStatus.REJECTED:
        raise BusinessException(message="审批拒绝接口的status必须为2", code=400)
    
    application = ApplicationService.reject_application(
        db, id, current_user.id, data
    )
    response = ApplicationService._to_application_response(db, application)
    return ApiResponse.success(data=response, message="已拒绝该申请")
