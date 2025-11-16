"""
管理员-操作日志查询API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.log import LogListQuery, LogListResponse
from app.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["管理员-操作日志"])


@router.get("", response_model=ApiResponse[LogListResponse], summary="查询操作日志")
def query_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, gt=0, description="按用户ID筛选"),
    action: Optional[str] = Query(None, max_length=64, description="操作类型筛选"),
    resource_type: Optional[str] = Query(None, max_length=64, description="资源类型筛选"),
    start_date: Optional[datetime] = Query(None, description="开始时间"),
    end_date: Optional[datetime] = Query(None, description="结束时间"),
    keyword: Optional[str] = Query(None, max_length=100, description="关键词搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("ADMIN"))
):
    """
    管理员查询操作日志
    
    **权限要求：** ADMIN角色
    
    **查询参数：**
    - **page**: 页码（默认1）
    - **page_size**: 每页数量（默认20，最大100）
    - **user_id**: 按用户ID筛选
    - **action**: 操作类型筛选（CREATE/UPDATE/DELETE等）
    - **resource_type**: 资源类型筛选（user/topic/paper等）
    - **start_date**: 开始时间（ISO 8601格式）
    - **end_date**: 结束时间（ISO 8601格式）
    - **keyword**: 关键词搜索（操作人姓名/用户名）
    
    **响应字段：**
    - 操作人信息（username, real_name）
    - 操作类型和资源类型
    - 详细信息JSON
    - IP地址
    - 操作时间
    
    **排序：** 按操作时间降序（最新的在前）
    """
    query_obj = LogListQuery(
        page=page,
        page_size=page_size,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        keyword=keyword
    )
    
    result = LogService.query_logs(db=db, query=query_obj)
    return ApiResponse.success(data=result)
