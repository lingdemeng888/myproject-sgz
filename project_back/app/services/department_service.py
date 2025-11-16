"""
系部业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from app.models.department import Department
from app.models.major import Major
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.core.exceptions import BusinessException


class DepartmentService:
    """系部业务逻辑服务"""

    def create(self, db: Session, data: DepartmentCreate) -> Department:
        """创建系部"""
        # 检查编码是否已存在
        stmt = select(Department).where(Department.dept_code == data.dept_code)
        if db.execute(stmt).scalar_one_or_none():
            raise BusinessException(code=400, message=f"系部编码 {data.dept_code} 已存在")
        
        dept = Department(**data.model_dump())
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return dept

    def get_list(self, db: Session, page: int, page_size: int, 
                 keyword: str = None, status: int = None):
        """获取系部列表（分页）"""
        stmt = select(Department)
        
        # 关键字搜索
        if keyword:
            stmt = stmt.where(
                or_(
                    Department.dept_code.contains(keyword),
                    Department.name.contains(keyword)
                )
            )
        # 状态筛选
        if status is not None:
            stmt = stmt.where(Department.status == status)
        
        # 总数
        total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar()
        
        # 分页
        items = db.execute(
            stmt.order_by(Department.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        ).scalars().all()
        
        return {"total": total, "items": items}

    def get_by_id(self, db: Session, dept_id: int) -> Department:
        """根据ID查询"""
        dept = db.get(Department, dept_id)
        if not dept:
            raise BusinessException(code=404, message="系部不存在")
        return dept

    def update(self, db: Session, dept_id: int, data: DepartmentUpdate) -> Department:
        """更新系部"""
        dept = self.get_by_id(db, dept_id)
        
        # 检查编码唯一性
        if data.dept_code and data.dept_code != dept.dept_code:
            stmt = select(Department).where(Department.dept_code == data.dept_code)
            if db.execute(stmt).scalar_one_or_none():
                raise BusinessException(code=400, message=f"系部编码 {data.dept_code} 已存在")
        
        # 更新字段
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(dept, key, value)
        
        db.commit()
        db.refresh(dept)
        return dept

    def delete(self, db: Session, dept_id: int):
        """删除系部（检查关联专业）"""
        dept = self.get_by_id(db, dept_id)
        
        # 检查是否有关联专业
        stmt = select(func.count()).select_from(Major).where(Major.department_id == dept_id)
        major_count = db.execute(stmt).scalar()
        if major_count > 0:
            raise BusinessException(
                code=400, 
                message=f"该系部下有 {major_count} 个专业，无法删除。请先删除或转移专业。"
            )
        
        db.delete(dept)
        db.commit()


department_service = DepartmentService()
