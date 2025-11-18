"""
用户服务层逻辑
"""
import secrets
import hashlib
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.role import Role
from app.models.major import Major
from app.models.department import Department
from app.schemas.user import StudentRegisterRequest, TutorRegisterRequest
from app.core.exceptions import BusinessException


def generate_salt() -> str:
    """生成随机盐值"""
    return secrets.token_hex(16)


def hash_password(password: str, salt: str) -> str:
    """使用盐值对密码进行SHA256哈希"""
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    """验证密码（使用盐值+SHA256）"""
    return hash_password(plain_password, salt) == hashed_password


class UserService:
    """用户服务类"""

    @staticmethod
    def register_student(db: Session, request: StudentRegisterRequest) -> User:
        """
        学生注册
        
        Args:
            db: 数据库会话
            request: 学生注册请求
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            BusinessException: 业务异常
        """
        # 1. 验证主修专业是否存在且启用
        stmt = select(Major).where(Major.id == request.primary_major_id)
        result = db.execute(stmt)
        major = result.scalar_one_or_none()
        
        if not major:
            raise BusinessException(f"主修专业不存在（ID: {request.primary_major_id}）")
        
        if major.status != 1:
            raise BusinessException(f"主修专业已被禁用，无法注册")
        
        # 2. 验证院系是否存在且启用
        stmt = select(Department).where(Department.id == major.department_id)
        result = db.execute(stmt)
        department = result.scalar_one_or_none()

        if not department:
            raise BusinessException(f"主修专业所属院系不存在（ID: {major.department_id}）")

        if department.status != 1:
            raise BusinessException("主修专业所属院系已被禁用，无法注册")

        # 3. 查询STUDENT角色
        stmt = select(Role).where(Role.role_key == 'STUDENT')
        result = db.execute(stmt)
        student_role = result.scalar_one_or_none()
        
        if not student_role:
            raise BusinessException("系统角色配置错误：缺少STUDENT角色")
        
        # 4. 生成盐值和密码哈希
        salt = generate_salt()
        password_hash = hash_password(request.password, salt)
        
        # 5. 创建用户对象
        user = User(
            username=request.username,
            real_name=request.real_name,
            student_no=request.student_no,
            phone=request.phone,
            email=request.email,
            password_hash=password_hash,
            password_salt=salt,
            primary_major_id=request.primary_major_id,
            department_id=department.id,
            status=1
        )
        
        # 6. 分配STUDENT角色
        user.roles.append(student_role)
        
        # 7. 保存到数据库
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig)
            
            # 解析唯一性约束冲突
            if 'username' in error_msg:
                raise BusinessException(f"用户名 '{request.username}' 已被使用")
            elif 'student_no' in error_msg:
                raise BusinessException(f"学号 '{request.student_no}' 已被注册")
            elif 'phone' in error_msg:
                raise BusinessException(f"手机号 '{request.phone}' 已被注册")
            elif 'email' in error_msg and request.email:
                raise BusinessException(f"邮箱 '{request.email}' 已被注册")
            else:
                raise BusinessException(f"数据保存失败：{error_msg}")

    @staticmethod
    def register_tutor(db: Session, request: TutorRegisterRequest) -> User:
        """
        导师注册
        
        Args:
            db: 数据库会话
            request: 导师注册请求
            
        Returns:
            User: 创建的用户对象
            
        Raises:
            BusinessException: 业务异常
        """
        # 1. 验证所属院系是否存在且启用
        stmt = select(Department).where(Department.id == request.department_id)
        result = db.execute(stmt)
        department = result.scalar_one_or_none()
        
        if not department:
            raise BusinessException(f"所属院系不存在（ID: {request.department_id}）")
        
        if department.status != 1:
            raise BusinessException(f"所属院系已被禁用，无法注册")
        
        # 2. 查询TUTOR角色
        stmt = select(Role).where(Role.role_key == 'TUTOR')
        result = db.execute(stmt)
        tutor_role = result.scalar_one_or_none()
        
        if not tutor_role:
            raise BusinessException("系统角色配置错误：缺少TUTOR角色")
        
        # 3. 生成盐值和密码哈希
        salt = generate_salt()
        password_hash = hash_password(request.password, salt)
        
        # 4. 创建用户对象
        user = User(
            username=request.username,
            real_name=request.real_name,
            teacher_no=request.teacher_no,
            phone=request.phone,
            email=request.email,
            password_hash=password_hash,
            password_salt=salt,
            department_id=request.department_id,
            status=1
        )
        
        # 5. 分配TUTOR角色
        user.roles.append(tutor_role)
        
        # 6. 保存到数据库
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig)
            
            # 解析唯一性约束冲突
            if 'username' in error_msg:
                raise BusinessException(f"用户名 '{request.username}' 已被使用")
            elif 'teacher_no' in error_msg:
                raise BusinessException(f"教师编号 '{request.teacher_no}' 已被注册")
            elif 'phone' in error_msg:
                raise BusinessException(f"手机号 '{request.phone}' 已被注册")
            elif 'email' in error_msg and request.email:
                raise BusinessException(f"邮箱 '{request.email}' 已被注册")
            else:
                raise BusinessException(f"数据保存失败：{error_msg}")

    @staticmethod
    def login(db: Session, username: str, password: str) -> User:
        """
        用户登录
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码（明文）
            
        Returns:
            User: 登录成功的用户对象
            
        Raises:
            BusinessException: 业务异常
        """
        # 1. 查询用户（排除已软删除的用户）
        stmt = select(User).where(
            User.username == username,
            User.deleted_at.is_(None)
        )
        result = db.execute(stmt)
        user = result.scalar_one_or_none()
        
        # 2. 用户不存在
        if not user:
            raise BusinessException(code=401, message="用户名或密码错误")
        
        # 3. 验证密码
        if not verify_password(password, user.password_salt, user.password_hash):
            raise BusinessException(code=401, message="用户名或密码错误")
        
        # 4. 检查账户状态
        if user.status == 0:
            raise BusinessException(code=403, message="账户已被锁定，请联系管理员")
        
        # 5. 更新最后登录时间
        user.last_login_at = datetime.now()
        db.commit()
        db.refresh(user)
        
        return user

