"""
管理员服务
"""
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func, or_
from typing import Optional

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.department import Department
from app.models.major import Major
from app.schemas.user import (
    UserListQuery,
    UserListResponse,
    UserDetailResponse
)
from app.constants.status import UserStatus
from app.core.exceptions import BusinessException
from app.services.log_service import LogService


class AdminService:
    """管理员服务类"""

    @staticmethod
    def list_users(
        db: Session,
        query: UserListQuery
    ) -> UserListResponse:
        """
        查询用户列表（带筛选和分页）
        
        验证流程：
        1. 构建基础查询（排除deleted_at不为空的用户）
        2. 应用角色筛选（通过UserRole关联）
        3. 应用院系筛选（department_id）
        4. 应用状态筛选（status）
        5. 应用关键词搜索（username/real_name/student_no/teacher_no）
        6. 统计总数
        7. 分页查询并加载关联数据（roles, department, major）
        8. 转换为响应对象
        
        Args:
            db: 数据库会话
            query: 查询参数
            
        Returns:
            UserListResponse（含total, page, page_size, items）
        """
        # ========== 步骤1：构建基础查询（排除软删除） ==========
        stmt = select(User).options(selectinload(User.roles)).filter(
            User.deleted_at.is_(None)
        )
        
        # ========== 步骤2：应用角色筛选 ==========
        if query.role_key:
            stmt = stmt.join(UserRole, User.id == UserRole.user_id).join(
                Role, UserRole.role_id == Role.id
            ).filter(Role.role_key == query.role_key)
        
        # ========== 步骤3：应用院系筛选 ==========
        if query.department_id:
            stmt = stmt.filter(User.department_id == query.department_id)
        
        # ========== 步骤4：应用状态筛选 ==========
        if query.status is not None:
            stmt = stmt.filter(User.status == query.status)
        
        # ========== 步骤5：应用关键词搜索 ==========
        if query.keyword:
            stmt = stmt.filter(
                or_(
                    User.username.like(f"%{query.keyword}%"),
                    User.real_name.like(f"%{query.keyword}%"),
                    User.student_no.like(f"%{query.keyword}%"),
                    User.teacher_no.like(f"%{query.keyword}%")
                )
            )
        
        # ========== 步骤6：统计总数 ==========
        total = db.query(func.count()).select_from(stmt.subquery()).scalar()
        
        # ========== 步骤7：分页查询 ==========
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(User.created_at.desc()).offset(offset).limit(query.page_size)
        
        users = db.execute(stmt).scalars().unique().all()
        
        # ========== 步骤8：转换响应 ==========
        items = [AdminService._to_user_detail_response(db, user) for user in users]
        
        return UserListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def update_user_status(
        db: Session,
        user_id: int,
        status: int,
        operator_id: int,
        ip_address: Optional[str] = None
    ) -> User:
        """
        更新用户状态
        
        验证流程：
        1. 查询用户是否存在
        2. 检查是否已软删除
        3. 检查是否修改自己的状态（禁止）
        4. 记录旧状态
        5. 更新status字段
        6. 提交事务
        7. 记录操作日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            status: 新状态（0=禁用，1=启用）
            operator_id: 操作人ID
            ip_address: 操作IP地址
            
        Returns:
            更新后的User对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：查询用户 ==========
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise BusinessException(message="用户不存在", code=404)
        
        # ========== 步骤2：检查是否已软删除 ==========
        if user.deleted_at is not None:
            raise BusinessException(message="用户已被删除，无法修改状态", code=400)
        
        # ========== 步骤3：检查是否修改自己的状态 ==========
        if user_id == operator_id:
            raise BusinessException(message="不能修改自己的状态", code=403)
        
        # ========== 步骤4：记录旧状态 ==========
        old_status = user.status
        old_status_name = UserStatus.get_name(old_status)
        new_status_name = UserStatus.get_name(status)
        
        # ========== 步骤5：更新status字段 ==========
        user.status = status
        
        # ========== 步骤6：提交事务 ==========
        db.commit()
        db.refresh(user)
        
        # ========== 步骤7：记录操作日志 ==========
        LogService.record_log(
            db=db,
            user_id=operator_id,
            action="update_user_status",
            resource_type="user",
            resource_id=user_id,
            detail={
                "old_status": old_status,
                "old_status_name": old_status_name,
                "new_status": status,
                "new_status_name": new_status_name,
                "target_username": user.username,
                "target_real_name": user.real_name
            },
            ip_address=ip_address
        )
        
        return user

    @staticmethod
    def assign_role(
        db: Session,
        user_id: int,
        role_id: int,
        operator_id: int,
        ip_address: Optional[str] = None
    ) -> User:
        """
        分配角色给用户
        
        验证流程：
        1. 查询用户是否存在
        2. 查询角色是否存在
        3. 检查用户是否已软删除
        4. 检查是否已分配该角色（去重）
        5. 插入user_role记录
        6. 刷新用户对象（加载最新角色列表）
        7. 记录操作日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            role_id: 角色ID
            operator_id: 操作人ID
            ip_address: 操作IP地址
            
        Returns:
            更新后的User对象（含roles关系）
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：查询用户 ==========
        user = db.query(User).options(selectinload(User.roles)).filter(User.id == user_id).first()
        
        if not user:
            raise BusinessException(message="用户不存在", code=404)
        
        # ========== 步骤2：查询角色 ==========
        role = db.query(Role).filter(Role.id == role_id).first()
        
        if not role:
            raise BusinessException(message="角色不存在", code=404)
        
        # ========== 步骤3：检查用户是否已软删除 ==========
        if user.deleted_at is not None:
            raise BusinessException(message="用户已被删除，无法分配角色", code=400)
        
        # ========== 步骤4：检查是否已分配该角色 ==========
        existing = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if existing:
            # 幂等操作，已分配则直接返回
            return user
        
        # ========== 步骤5：插入user_role记录 ==========
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
        db.commit()
        
        # ========== 步骤6：刷新用户对象 ==========
        db.refresh(user)
        
        # ========== 步骤7：记录操作日志 ==========
        LogService.record_log(
            db=db,
            user_id=operator_id,
            action="assign_role",
            resource_type="user",
            resource_id=user_id,
            detail={
                "role_id": role_id,
                "role_key": role.role_key,
                "role_name": role.name,
                "target_username": user.username,
                "target_real_name": user.real_name
            },
            ip_address=ip_address
        )
        
        return user

    # ========== 辅助方法 ==========

    @staticmethod
    def _to_user_detail_response(db: Session, user: User) -> UserDetailResponse:
        """转换为用户详情响应对象"""
        # 查询院系名称
        department_name = None
        if user.department_id:
            dept = db.query(Department).filter(Department.id == user.department_id).first()
            if dept:
                department_name = dept.name
        
        # 查询专业名称
        major_name = None
        if user.primary_major_id:
            major = db.query(Major).filter(Major.id == user.primary_major_id).first()
            if major:
                major_name = major.name
        
        # 提取角色key列表
        role_keys = [role.role_key for role in user.roles]
        
        # 获取状态名称
        status_name = UserStatus.get_name(user.status)
        
        return UserDetailResponse(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            student_no=user.student_no,
            teacher_no=user.teacher_no,
            phone=user.phone,
            email=user.email,
            department_id=user.department_id,
            department_name=department_name,
            primary_major_id=user.primary_major_id,
            major_name=major_name,
            status=user.status,
            status_name=status_name,
            roles=role_keys,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
