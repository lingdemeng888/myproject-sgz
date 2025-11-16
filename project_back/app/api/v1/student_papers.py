"""
学生端论文管理API
包含：创建论文、添加版本、提交论文、查询论文
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.paper import (
    PaperCreateRequest,
    PaperVersionCreateRequest,
    PaperResponse,
    PaperListQuery,
    PaperListResponse
)
from app.services.paper_service import PaperService

router = APIRouter(prefix="/student/papers", tags=["学生-论文管理"])


@router.post("", response_model=ApiResponse[PaperResponse], summary="创建论文")
def create_paper(
    data: PaperCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：创建论文
    
    **前置条件：**
    - 学生必须有该选题的已通过申请（status=1）
    
    **业务规则：**
    1. 验证学生对topic_id有通过的申请
    2. 检查唯一性约束（同一学年学期只能有一篇论文）
    3. 创建论文，默认status=0（编辑中）
    
    **请求参数：**
    - **topic_id**: 选题ID
    - **title**: 论文标题（5-255字符）
    - **abstract**: 摘要（可选，最多2000字符）
    - **keywords**: 关键词（可选，多个用逗号分隔）
    - **academic_year**: 学年，格式：2024-2025
    - **term**: 学期，1=上学期, 2=下学期
    
    **可能的错误：**
    - 403: 没有该选题的通过申请
    - 400: 该学年学期已有论文
    """
    paper = PaperService.create_paper(db, current_user.id, data)
    response = PaperService._to_paper_response(db, paper)
    return ApiResponse.success(data=response, message="论文创建成功")


@router.post("/{id}/versions", response_model=ApiResponse[PaperResponse], summary="添加论文版本")
def create_version(
    id: int,
    data: PaperVersionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：为论文添加新版本
    
    **业务规则：**
    1. 验证论文属于当前学生
    2. 自动计算版本号（MAX(version_no)+1）
    3. 插入新版本记录
    
    **请求参数：**
    - **content_text**: 正文内容（可选）
    - **content_format**: 内容格式，0=无,1=markdown,2=html,3=text
    - **notes**: 版本说明备注（可选，最多255字符）
    
    **可能的错误：**
    - 404: 论文不存在
    - 403: 无权限操作此论文
    """
    version = PaperService.create_version(db, id, current_user.id, data)
    # 返回完整的论文信息（含所有版本）
    paper_detail = PaperService.get_paper_detail(db, id, current_user.id)
    return ApiResponse.success(data=paper_detail, message=f"版本 v{version.version_no} 添加成功")


@router.put("/{id}/submit", response_model=ApiResponse[PaperResponse], summary="正式提交论文")
def submit_paper(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：正式提交论文
    
    **业务规则：**
    1. 验证论文属于当前学生
    2. 验证至少有一个版本
    3. 验证当前状态为"编辑中"（0）
    4. 更新status=1（已提交），设置submitted_at
    
    **可能的错误：**
    - 404: 论文不存在
    - 403: 无权限操作此论文
    - 400: 论文尚未添加版本
    - 400: 论文当前状态不允许提交
    """
    paper = PaperService.submit_paper(db, id, current_user.id)
    response = PaperService._to_paper_response(db, paper)
    return ApiResponse.success(data=response, message="论文提交成功")


@router.get("", response_model=ApiResponse[PaperListResponse], summary="查询我的论文列表")
def list_my_papers(
    page: int = 1,
    page_size: int = 10,
    status: int | None = None,
    academic_year: str | None = None,
    term: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：查询我的论文列表
    
    **筛选条件：**
    - 自动筛选当前学生的论文
    - **status**: 状态筛选（可选）
    - **academic_year**: 学年筛选（可选）
    - **term**: 学期筛选（可选，1=上学期, 2=下学期）
    
    **排序规则：**
    - 按创建时间倒序（最新的在前）
    
    **响应字段：**
    - 包含论文基本信息
    - 版本统计（version_count, latest_version_no）
    - 不含版本详细内容（列表接口优化）
    """
    query = PaperListQuery(
        page=page,
        page_size=page_size,
        status=status,
        academic_year=academic_year,
        term=term
    )
    result = PaperService.list_my_papers(db, current_user.id, query)
    return ApiResponse.success(data=result)


@router.get("/{id}", response_model=ApiResponse[PaperResponse], summary="查询论文详情")
def get_paper_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：查询论文详情（含所有版本）
    
    **响应字段：**
    - 论文基本信息
    - 关联选题信息
    - 所有版本列表（按版本号倒序）
    - 版本详情（不含content_text正文内容）
    
    **可能的错误：**
    - 404: 论文不存在
    - 403: 无权限查看此论文
    """
    result = PaperService.get_paper_detail(db, id, current_user.id)
    return ApiResponse.success(data=result)
