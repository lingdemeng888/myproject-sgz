"""
专业业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from app.models.major import Major
from app.models.department import Department
from app.models.user import User
from app.models.user_major import UserMajor
from app.models.topic import Topic
from app.schemas.major import MajorCreate, MajorUpdate
from app.core.exceptions import BusinessException


class MajorService:
    """专业业务逻辑服务"""

    def create(self, db: Session, data: MajorCreate) -> dict:
        """创建专业"""
        # 检查系部是否存在
        dept = db.get(Department, data.department_id)
        if not dept:
            raise BusinessException(code=404, message="所属系部不存在")
        if dept.status == 0:
            raise BusinessException(code=400, message="所属系部已停用，无法创建专业")
        
        # 检查编码唯一性
        stmt = select(Major).where(Major.major_code == data.major_code)
        if db.execute(stmt).scalar_one_or_none():
            raise BusinessException(code=400, message=f"专业编码 {data.major_code} 已存在")
        
        major = Major(**data.model_dump())
        db.add(major)
        db.commit()
        db.refresh(major)
        
        # 返回带系部名称的数据
        return {
            "id": major.id,
            "department_id": major.department_id,
            "major_code": major.major_code,
            "name": major.name,
            "status": major.status,
            "created_at": major.created_at,
            "updated_at": major.updated_at,
            "department_name": dept.name
        }

    def get_list(self, db: Session, page: int, page_size: int,
                 department_id: int = None, keyword: str = None, status: int = None):
        """获取专业列表（带系部名称）"""
        # 使用join查询系部名称
        stmt = select(Major, Department.name.label('department_name')).\
            join(Department, Major.department_id == Department.id)
        
        # 筛选条件
        if department_id:
            stmt = stmt.where(Major.department_id == department_id)
        if keyword:
            stmt = stmt.where(
                or_(
                    Major.major_code.contains(keyword),
                    Major.name.contains(keyword)
                )
            )
        if status is not None:
            stmt = stmt.where(Major.status == status)
        
        # 总数
        total = db.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar()
        
        # 分页查询
        results = db.execute(
            stmt.order_by(Major.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        ).all()
        
        # 构造响应（手动添加department_name）
        items = []
        for major, dept_name in results:
            major_dict = {
                "id": major.id,
                "department_id": major.department_id,
                "major_code": major.major_code,
                "name": major.name,
                "status": major.status,
                "created_at": major.created_at,
                "updated_at": major.updated_at,
                "department_name": dept_name
            }
            items.append(major_dict)
        
        return {"total": total, "items": items}

    def get_by_id(self, db: Session, major_id: int):
        """查询详情（含系部名称）"""
        result = db.execute(
            select(Major, Department.name.label('department_name'))
            .join(Department, Major.department_id == Department.id)
            .where(Major.id == major_id)
        ).first()
        
        if not result:
            raise BusinessException(code=404, message="专业不存在")
        
        major, dept_name = result
        return {
            "id": major.id,
            "department_id": major.department_id,
            "major_code": major.major_code,
            "name": major.name,
            "status": major.status,
            "created_at": major.created_at,
            "updated_at": major.updated_at,
            "department_name": dept_name
        }

    def update(self, db: Session, major_id: int, data: MajorUpdate):
        """更新专业"""
        major = db.get(Major, major_id)
        if not major:
            raise BusinessException(code=404, message="专业不存在")
        
        # 检查系部
        if data.department_id and data.department_id != major.department_id:
            dept = db.get(Department, data.department_id)
            if not dept:
                raise BusinessException(code=404, message="所属系部不存在")
        
        # 检查编码唯一性
        if data.major_code and data.major_code != major.major_code:
            stmt = select(Major).where(Major.major_code == data.major_code)
            if db.execute(stmt).scalar_one_or_none():
                raise BusinessException(code=400, message=f"专业编码 {data.major_code} 已存在")
        
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(major, key, value)
        
        db.commit()
        db.refresh(major)
        
        # 返回带系部名称的数据
        return self.get_by_id(db, major_id)

    def delete(self, db: Session, major_id: int):
        """删除专业（检查关联）"""
        major = db.get(Major, major_id)
        if not major:
            raise BusinessException(code=404, message="专业不存在")
        
        # 检查是否有用户的主专业
        user_count = db.execute(
            select(func.count()).select_from(User).where(User.primary_major_id == major_id)
        ).scalar()
        if user_count > 0:
            raise BusinessException(
                code=400,
                message=f"该专业是 {user_count} 个用户的主专业，无法删除"
            )
        
        # 检查用户-专业关联
        um_count = db.execute(
            select(func.count()).select_from(UserMajor).where(UserMajor.major_id == major_id)
        ).scalar()
        if um_count > 0:
            raise BusinessException(
                code=400,
                message=f"该专业与 {um_count} 个用户关联，无法删除"
            )
        
        # 检查选题
        topic_count = db.execute(
            select(func.count()).select_from(Topic).where(Topic.major_id == major_id)
        ).scalar()
        if topic_count > 0:
            raise BusinessException(
                code=400,
                message=f"该专业下有 {topic_count} 个选题，无法删除"
            )
        
        db.delete(major)
        db.commit()


major_service = MajorService()
