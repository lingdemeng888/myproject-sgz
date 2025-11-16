"""
统一响应格式定义
"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """标准API响应格式"""
    code: int = Field(default=200, description="业务状态码")
    message: str = Field(default="success", description="提示信息")
    data: Optional[T] = Field(default=None, description="业务数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {}
            }
        }

    @classmethod
    def success(cls, data: T = None, message: str = "success") -> "ApiResponse[T]":
        """成功响应的快捷方法"""
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 400, message: str = "error", data: T = None) -> "ApiResponse[T]":
        """错误响应的快捷方法"""
        return cls(code=code, message=message, data=data)


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    items: List[T] = Field(description="数据列表")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "items": []
            }
        }


class ErrorDetail(BaseModel):
    """错误详情"""
    field: Optional[str] = Field(default=None, description="错误字段")
    message: str = Field(description="错误信息")
    type: Optional[str] = Field(default=None, description="错误类型")


# ========== 全局错误响应模板 ==========
COMMON_RESPONSES = {
    400: {
        "description": "请求参数错误或业务规则限制",
        "content": {
            "application/json": {
                "example": {
                    "code": 400,
                    "message": "请求参数错误或不满足业务规则",
                    "data": None
                }
            }
        }
    },
    401: {
        "description": "未认证或Token无效",
        "content": {
            "application/json": {
                "example": {
                    "code": 401,
                    "message": "未提供认证信息或Token已失效",
                    "data": None
                }
            }
        }
    },
    403: {
        "description": "权限不足",
        "content": {
            "application/json": {
                "example": {
                    "code": 403,
                    "message": "您没有权限执行此操作",
                    "data": None
                }
            }
        }
    },
    404: {
        "description": "资源不存在",
        "content": {
            "application/json": {
                "example": {
                    "code": 404,
                    "message": "请求的资源不存在",
                    "data": None
                }
            }
        }
    }
}
