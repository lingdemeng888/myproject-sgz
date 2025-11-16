"""
文件上传与下载API
包含：上传附件、下载附件、删除附件
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.attachment import AttachmentUploadResponse, AttachmentResponse, AttachmentListResponse
from app.services.paper_service import PaperService
from app.utils.file_storage import FileStorage
from app.core.exceptions import BusinessException

router = APIRouter(prefix="/upload", tags=["文件上传下载"])


@router.post("/attachment", response_model=ApiResponse[AttachmentResponse], summary="上传附件")
async def upload_attachment(
    version_id: int = Form(..., description="论文版本ID"),
    file: UploadFile = File(..., description="附件文件"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：上传论文附件
    
    **前置条件：**
    - 版本必须属于当前学生的论文
    
    **业务规则：**
    1. 验证文件大小（最大50MB）
    2. 验证文件类型（.pdf, .doc, .docx, .zip, .rar）
    3. 计算文件哈希（SHA256）
    4. 按 papers/年/月/ 目录结构存储
    5. 哈希去重：相同文件不重复存储
    6. 验证版本权限（version属于当前学生的论文）
    7. 插入附件记录到数据库
    
    **请求参数：**
    - **version_id**: 论文版本ID（Form参数）
    - **file**: 附件文件（File参数）
    
    **可能的错误：**
    - 400: 文件类型不支持
    - 400: 文件大小超过限制
    - 403: 无权限操作此版本
    - 404: 版本不存在
    """
    # 步骤1：保存文件到服务器
    file_info = FileStorage.save_attachment(file)
    
    # 步骤2：将附件关联到版本（含权限验证）
    attachment = PaperService.add_attachment(
        db, version_id, file_info, current_user.id
    )
    
    # 步骤3：转换响应
    response = PaperService._to_attachment_response(db, attachment)
    
    return ApiResponse.success(data=response, message="附件上传成功")


@router.get("/attachment/{id}", summary="下载附件")
async def download_attachment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    下载附件（含权限验证）
    
    **权限规则：**
    - 论文学生可以下载自己论文的附件
    - 导师可以下载指导学生论文的附件
    - 其他人无权下载
    
    **验证流程：**
    1. 查询附件记录
    2. 查询附件关联的版本和论文
    3. 获取论文的选题和导师信息
    4. 验证权限：student_id == current_user.id OR tutor_id == current_user.id
    5. 返回文件流
    
    **可能的错误：**
    - 404: 附件不存在
    - 404: 文件不存在
    - 403: 无权限下载
    """
    # 步骤1：获取附件详情（含权限验证）
    attachment = PaperService.get_attachment_detail(db, id, current_user.id)
    
    # 步骤2：获取文件路径
    file_path = FileStorage.get_file_path(attachment.storage_url)
    
    # 步骤3：验证文件是否存在
    if not file_path.exists():
        raise BusinessException(
            message="文件不存在，可能已被删除",
            code=404
        )
    
    # 步骤4：返回文件流
    return FileResponse(
        path=str(file_path),
        filename=attachment.file_name,
        media_type=attachment.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.file_name}"'
        }
    )


@router.delete("/attachment/{id}", response_model=ApiResponse[dict], summary="删除附件")
def delete_attachment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("STUDENT"))
):
    """
    学生端：删除附件
    
    **权限规则：**
    - 只能删除自己论文的附件
    
    **业务规则：**
    1. 查询附件是否存在
    2. 验证附件属于当前学生的论文
    3. 删除数据库记录
    4. 不删除物理文件（哈希去重场景，避免影响其他论文）
    
    **可能的错误：**
    - 404: 附件不存在
    - 403: 无权限删除
    """
    # 删除附件（含权限验证）
    PaperService.delete_attachment(db, id, current_user.id)
    
    return ApiResponse.success(data={}, message="附件删除成功")


@router.get("/version/{version_id}/attachments", response_model=ApiResponse[AttachmentListResponse], summary="查询版本的附件列表")
def list_version_attachments(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    查询论文版本的所有附件
    
    **权限规则：**
    - 论文学生或导师可查看
    
    **响应字段：**
    - 附件列表（按上传时间倒序）
    - 包含文件名、大小、上传人、上传时间等信息
    
    **可能的错误：**
    - 404: 版本不存在
    - 403: 无权限查看
    """
    result = PaperService.list_version_attachments(db, version_id, current_user.id)
    return ApiResponse.success(data=result)
