"""
全局异常处理
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
from typing import Any, Dict


class BusinessException(Exception):
    """业务异常基类"""
    def __init__(self, code: int = 400, message: str = "业务错误", data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """参数验证异常处理器"""
    errors = exc.errors()
    logger.error(f"参数验证失败: {errors} - Path: {request.url.path}")
    
    # 格式化错误信息
    error_details = []
    for error in errors:
        error_details.append({
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "data": {"errors": error_details}
        }
    )


async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    """业务异常处理器"""
    logger.warning(f"业务异常: {exc.code} - {exc.message} - Path: {request.url.path}")
    return JSONResponse(
        status_code=200,  # 业务异常使用200状态码，通过code区分
        content={
            "code": exc.code,
            "message": exc.message,
            "data": exc.data
        }
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局未知异常处理器"""
    logger.exception(f"未知异常: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误，请稍后重试",
            "data": None
        }
    )
