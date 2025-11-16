"""
学生端选题API
包含：浏览选题、申请选题、查看申请
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationListQuery,
    ApplicationListResponse,
    StudentTopicListQuery,
    StudentTopicResponse,
    StudentTopicListResponse
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/student/topics", tags=["学生-选题浏览与申请"])


@router.get("", response_model=ApiResponse[StudentTopicListResponse], summary="浏览可申请的选题")
def list_available_topics(
    page: int = 1,
    page_size: int = 10,
    major_id: int | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：浏览可申请的选题列表
    
    筛选规则：
    - 仅显示已发布的选题（status=1）
    - 仅显示有剩余名额的选题
    - 默认筛选本专业的选题（如果学生已设置专业）
    
    **参数说明：**
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认10，最大100）
    - **major_id**: 专业ID筛选（可选，不传则默认本专业）
    - **keyword**: 关键词搜索（标题/描述）
    
    **响应字段：**
    - available_slots: 剩余名额（计算字段）
    - 不返回status字段（学生端只能看到已发布的）
    """
    query = StudentTopicListQuery(
        page=page,
        page_size=page_size,
        major_id=major_id,
        keyword=keyword
    )
    result = ApplicationService.list_available_topics(db, current_user.id, query)
    return ApiResponse.success(data=result)


@router.post("/applications", response_model=ApiResponse[ApplicationResponse], summary="申请选题")
def create_application(
    data: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：创建选题申请
    
    **请求参数：**
    - **topic_id**: 选题ID（必填）
    - **application_reason**: 申请理由（必填，10-500字符）
    
    **业务规则：**
    1. 学生最多同时申请2个选题（待审批或已通过状态）
    2. 只能申请本专业的选题
    3. 只能申请已发布且有名额的选题
    4. 不能重复申请同一选题
    
    **可能的错误：**
    - 400: 超过申请数量限制（2个）
    - 400: 选题未发布或已关闭
    - 400: 尚未设置专业
    - 403: 专业不匹配
    - 400: 重复申请
    - 400: 名额已满
    - 404: 选题不存在
    """
    application = ApplicationService.create_application(db, current_user.id, data)
    response = ApplicationService._to_application_response(db, application)
    return ApiResponse.success(data=response, message="申请提交成功，请等待导师审批")


@router.get("/applications", response_model=ApiResponse[ApplicationListResponse], summary="查看我的申请")
def list_my_applications(
    page: int = 1,
    page_size: int = 10,
    status: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：查看我的申请列表
    
    **参数说明：**
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认10，最大100）
    - **status**: 状态筛选（可选）
      - 0: 待审批
      - 1: 通过
      - 2: 拒绝
      - 3: 取消
    
    **响应字段：**
    - status: 数字类型（0/1/2/3）
    - status_name: 状态名称（待审批/通过/拒绝/取消）
    - topic_title: 选题标题
    - decision_by_name: 审批人姓名（如果已审批）
    - decision_comment: 审批意见（如果已审批）
    """
    query = ApplicationListQuery(
        page=page,
        page_size=page_size,
        status=status
    )
    result = ApplicationService.list_my_applications(db, current_user.id, query)
    return ApiResponse.success(data=result)


@router.get("/applications/{application_id}", response_model=ApiResponse[ApplicationResponse], summary="申请详情")
def get_application_detail(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：获取申请详情
    
    **参数说明：**
    - **application_id**: 申请ID
    
    **权限校验：**
    - 仅能查看自己的申请
    
    **可能的错误：**
    - 404: 申请不存在
    - 403: 无权限查看
    """
    response = ApplicationService.get_application_detail(db, application_id, current_user.id)
    return ApiResponse.success(data=response)
