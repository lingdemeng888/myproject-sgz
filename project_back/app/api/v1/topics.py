from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.topic import TopicCreateRequest, TopicUpdateRequest, TopicListQuery, TopicResponse, TopicListResponse
from app.services.topic_service import TopicService

router = APIRouter(prefix="/tutor/topics", tags=["导师-选题管理"])


@router.post("", response_model=ApiResponse[TopicResponse], summary="创建选题")
def create_topic(
    data: TopicCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    创建选题（仅导师）
    
    - **title**: 选题标题
    - **description**: 选题描述（至少10字符）
    - **major_id**: 专业ID
    - **max_students**: 最大学生数（1-10）
    """
    topic = TopicService.create_topic(db, current_user.id, data)
    response = TopicService._to_response(db, topic)
    return ApiResponse.success(data=response, message="选题创建成功")


@router.get("", response_model=ApiResponse[TopicListResponse], summary="查询我的选题列表")
def list_my_topics(
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    major_id: int | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    查询我的选题列表（仅导师）
    
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认10，最大100）
    - **status**: 状态筛选（0=草稿/1=发布/2=锁定/3=归档）
    - **major_id**: 专业ID筛选
    - **keyword**: 关键词搜索（标题/描述）
    """
    query = TopicListQuery(
        page=page,
        page_size=page_size,
        status=status,
        major_id=major_id,
        keyword=keyword
    )
    result = TopicService.list_my_topics(db, current_user.id, query)
    return ApiResponse.success(data=result)


@router.get("/{topic_id}", response_model=ApiResponse[TopicResponse], summary="获取选题详情")
def get_topic_detail(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取选题详情
    
    - **topic_id**: 选题ID
    """
    response = TopicService.get_topic_detail(db, topic_id)
    return ApiResponse.success(data=response)


@router.put("/{topic_id}", response_model=ApiResponse[TopicResponse], summary="更新选题")
def update_topic(
    topic_id: int,
    data: TopicUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    更新选题（仅导师，仅草稿状态可编辑）
    
    - **topic_id**: 选题ID
    - **title**: 选题标题（可选）
    - **description**: 选题描述（可选）
    - **major_id**: 专业ID（可选）
    - **max_students**: 最大学生数（可选）
    """
    topic = TopicService.update_topic(db, topic_id, current_user.id, data)
    response = TopicService._to_response(db, topic)
    return ApiResponse.success(data=response, message="选题更新成功")


@router.delete("/{topic_id}", response_model=ApiResponse[None], summary="删除选题")
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    删除选题（仅导师，仅草稿状态且无申请记录可删除）
    
    - **topic_id**: 选题ID
    """
    TopicService.delete_topic(db, topic_id, current_user.id)
    return ApiResponse.success(message="选题删除成功")


@router.post("/{topic_id}/publish", response_model=ApiResponse[TopicResponse], summary="发布选题")
def publish_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    发布选题（仅导师，DRAFT → PUBLISHED）
    
    - **topic_id**: 选题ID
    """
    topic = TopicService.publish_topic(db, topic_id, current_user.id)
    response = TopicService._to_response(db, topic)
    return ApiResponse.success(data=response, message="选题发布成功")


@router.post("/{topic_id}/lock", response_model=ApiResponse[TopicResponse], summary="锁定选题")
def lock_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    锁定选题（仅导师，PUBLISHED → LOCKED）
    
    - **topic_id**: 选题ID
    """
    topic = TopicService.lock_topic(db, topic_id, current_user.id)
    response = TopicService._to_response(db, topic)
    return ApiResponse.success(data=response, message="选题锁定成功")


@router.post("/{topic_id}/archive", response_model=ApiResponse[TopicResponse], summary="归档选题")
def archive_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("TUTOR"))
):
    """
    归档选题（仅导师，任意状态 → ARCHIVED）
    
    - **topic_id**: 选题ID
    """
    topic = TopicService.archive_topic(db, topic_id, current_user.id)
    response = TopicService._to_response(db, topic)
    return ApiResponse.success(data=response, message="选题归档成功")
