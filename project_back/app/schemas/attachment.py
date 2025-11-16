"""
附件相关Schema定义
"""
from pydantic import BaseModel
from datetime import datetime


class AttachmentUploadResponse(BaseModel):
    """文件上传成功响应"""
    file_name: str
    storage_url: str
    file_hash: str
    file_size: int
    mime_type: str

    model_config = {
        "from_attributes": True
    }


class AttachmentResponse(BaseModel):
    """附件详情响应"""
    id: int
    paper_version_id: int
    file_name: str
    mime_type: str
    file_size: int
    storage_url: str
    file_hash: str
    uploaded_by: int
    uploaded_by_name: str  # 上传人姓名
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }


class AttachmentListResponse(BaseModel):
    """附件列表响应"""
    total: int
    items: list[AttachmentResponse]
