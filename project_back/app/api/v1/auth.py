"""
用户认证相关API
"""
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.schemas.response import ApiResponse
from app.schemas.user import StudentRegisterRequest, TutorRegisterRequest, UserRegisterResponse
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.user_service import UserService
from app.models.user import User
from app.models.department import Department
from app.models.major import Major

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/register/student", response_model=ApiResponse[UserRegisterResponse], summary="学生注册")
def register_student(
    request: StudentRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    学生注册接口（公开，无需认证）
    
    - **username**: 用户名（3-64字符，仅字母数字下划线）
    - **real_name**: 真实姓名
    - **student_no**: 学号（唯一）
    - **phone**: 手机号（11位，唯一）
    - **password**: 密码（6-128字符）
    - **primary_major_id**: 主修专业ID（必须存在且已启用）
    - **email**: 电子邮箱（可选，唯一）
    
    **业务规则：**
    - 主修专业必须存在且状态为启用
    - username、student_no、phone、email 必须唯一
    - 自动分配 STUDENT 角色
    - 默认状态为启用（status=1）
    """
    user = UserService.register_student(db, request)
    return ApiResponse.success(
        data=UserRegisterResponse.model_validate(user),
        message="学生注册成功"
    )


@router.post("/register/tutor", response_model=ApiResponse[UserRegisterResponse], summary="导师注册")
def register_tutor(
    request: TutorRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    导师注册接口（公开，无需认证）
    
    - **username**: 用户名（3-64字符，仅字母数字下划线）
    - **real_name**: 真实姓名
    - **teacher_no**: 教师编号（唯一）
    - **phone**: 手机号（11位，唯一）
    - **password**: 密码（6-128字符）
    - **department_id**: 所属院系ID（必须存在且已启用）
    - **email**: 电子邮箱（可选，唯一）
    
    **业务规则：**
    - 所属院系必须存在且状态为启用
    - username、teacher_no、phone、email 必须唯一
    - 自动分配 TUTOR 角色
    - 默认状态为启用（status=1）
    """
    user = UserService.register_tutor(db, request)
    return ApiResponse.success(
        data=UserRegisterResponse.model_validate(user),
        message="导师注册成功"
    )


@router.post("/login", response_model=ApiResponse[LoginResponse], summary="用户登录")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口（公开，无需认证）
    
    - **username**: 用户名
    - **password**: 密码
    
    **业务规则：**
    - 验证用户名和密码
    - 检查账户状态（锁定/删除）
    - 更新最后登录时间
    - 生成JWT访问令牌
    - 返回用户信息和令牌
    
    **返回数据：**
    - access_token: JWT访问令牌
    - token_type: 令牌类型（bearer）
    - expires_in: 过期时间（秒）
    - user: 用户基本信息（包含角色列表）
    """
    # 1. 执行登录验证
    user = UserService.login(db, request.username, request.password)
    
    # 2. 生成JWT token
    access_token = create_access_token(subject=user.username)
    
    # 3. 查询院系名称和专业名称
    department_name = None
    if user.department_id:
        department = db.query(Department).filter(Department.id == user.department_id).first()
        if department:
            department_name = department.name
    
    primary_major_name = None
    if user.primary_major_id:
        major = db.query(Major).filter(Major.id == user.primary_major_id).first()
        if major:
            primary_major_name = major.name
    
    # 4. 构造用户信息
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        roles=[role.role_key for role in user.roles],  # 提取角色列表
        status=user.status,
        student_no=user.student_no,
        teacher_no=user.teacher_no,
        department_id=user.department_id,
        department_name=department_name,
        primary_major_id=user.primary_major_id,
        primary_major_name=primary_major_name
    )
    
    # 5. 构造登录响应
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,  # 转换为秒
        user=user_info
    )
    
    return ApiResponse.success(
        data=login_response,
        message="登录成功"
    )


@router.get("/me", response_model=ApiResponse[UserInfo], summary="获取当前用户信息")
def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户信息（需要认证）
    
    **请求头：**
    - Authorization: Bearer {access_token}
    
    **返回数据：**
    - 用户基本信息（包含角色列表、院系名称、专业名称）
    
    **使用场景：**
    - 页面加载时获取用户信息
    - 验证token有效性
    - 获取用户权限信息
    """
    # 查询院系名称和专业名称
    department_name = None
    if current_user.department_id:
        department = db.query(Department).filter(Department.id == current_user.department_id).first()
        if department:
            department_name = department.name
    
    primary_major_name = None
    if current_user.primary_major_id:
        major = db.query(Major).filter(Major.id == current_user.primary_major_id).first()
        if major:
            primary_major_name = major.name
    
    user_info = UserInfo(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        roles=[role.role_key for role in current_user.roles],
        status=current_user.status,
        student_no=current_user.student_no,
        teacher_no=current_user.teacher_no,
        department_id=current_user.department_id,
        department_name=department_name,
        primary_major_id=current_user.primary_major_id,
        primary_major_name=primary_major_name
    )
    
    return ApiResponse.success(
        data=user_info,
        message="获取成功"
    )


