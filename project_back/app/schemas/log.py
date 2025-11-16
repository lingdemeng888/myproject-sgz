"""
操作日志相关Schema定义
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class OperationLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = Field(None, description="操作人用户名")
    real_name: Optional[str] = Field(None, description="操作人姓名")
    action: str = Field(description="操作类型")
    resource_type: str = Field(description="资源类型")
    resource_id: Optional[int] = None
    detail: Optional[str] = Field(None, description="操作详情JSON")
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LogListQuery(BaseModel):
    """日志查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    user_id: Optional[int] = Field(None, gt=0, description="按用户ID筛选")
    action: Optional[str] = Field(None, max_length=64, description="操作类型筛选")
    resource_type: Optional[str] = Field(None, max_length=64, description="资源类型筛选")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")
    keyword: Optional[str] = Field(None, max_length=100, description="关键词搜索（用户名/姓名）")


class LogListResponse(BaseModel):
    """日志列表响应"""
    total: int
    page: int
    page_size: int
    items: list[OperationLogResponse]
