from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from datetime import datetime
from typing import Optional

from app.constants.status import TopicStatus, ApplicationStatus
from app.models.topic import Topic
from app.models.major import Major
from app.models.department import Department
from app.models.user import User
from app.models.topic_application import TopicApplication
from app.schemas.topic import TopicCreateRequest, TopicUpdateRequest, TopicListQuery, TopicResponse, TopicListResponse
from app.core.exceptions import BusinessException


class TopicService:
    """选题服务"""

    @staticmethod
    def create_topic(db: Session, tutor_id: int, data: TopicCreateRequest) -> Topic:
        """
        创建选题
        
        Args:
            db: 数据库会话
            tutor_id: 导师ID
            data: 创建数据
            
        Returns:
            创建的选题对象
            
        Raises:
            BusinessException: 专业不存在
        """
        # 验证专业是否存在
        major = db.query(Major).filter(Major.id == data.major_id).first()
        if not major:
            raise BusinessException(message="专业不存在", code=404)
        
        # 创建选题
        topic = Topic(
            title=data.title,
            description=data.description,
            tutor_id=tutor_id,
            major_id=data.major_id,
            status=TopicStatus.DRAFT,
            max_students=data.max_students,
            current_students=0,
            academic_year=data.academic_year,
            term=data.term
        )
        
        db.add(topic)
        db.commit()
        db.refresh(topic)
        
        return topic

    @staticmethod
    def update_topic(db: Session, topic_id: int, tutor_id: int, data: TopicUpdateRequest) -> Topic:
        """
        更新选题（仅草稿状态可编辑）
        
        Args:
            db: 数据库会话
            topic_id: 选题ID
            tutor_id: 导师ID
            data: 更新数据
            
        Returns:
            更新后的选题对象
            
        Raises:
            BusinessException: 选题不存在、无权限、状态不允许编辑、专业不存在
        """
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        # 数据权限检查
        if topic.tutor_id != tutor_id:
            raise BusinessException(message="无权限操作此选题", code=403)
        
        # 仅草稿状态可编辑
        if topic.status != TopicStatus.DRAFT:
            raise BusinessException(message="仅草稿状态的选题可编辑", code=400)
        
        # 验证专业
        if data.major_id is not None:
            major = db.query(Major).filter(Major.id == data.major_id).first()
            if not major:
                raise BusinessException(message="专业不存在", code=404)
            topic.major_id = data.major_id
        
        # 更新字段
        if data.title is not None:
            topic.title = data.title
        if data.description is not None:
            topic.description = data.description
        if data.max_students is not None:
            topic.max_students = data.max_students
        if data.academic_year is not None:
            topic.academic_year = data.academic_year
        if data.term is not None:
            topic.term = data.term
        
        topic.updated_at = datetime.now()
        db.commit()
        db.refresh(topic)
        
        return topic

    @staticmethod
    def delete_topic(db: Session, topic_id: int, tutor_id: int) -> None:
        """
        删除选题（仅草稿状态且无申请记录可删除）
        
        Args:
            db: 数据库会话
            topic_id: 选题ID
            tutor_id: 导师ID
            
        Raises:
            BusinessException: 选题不存在、无权限、状态不允许删除、存在申请记录
        """
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        # 数据权限检查
        if topic.tutor_id != tutor_id:
            raise BusinessException(message="无权限操作此选题", code=403)
        
        # 仅草稿状态可删除
        if topic.status != TopicStatus.DRAFT:
            raise BusinessException(message="仅草稿状态的选题可删除", code=400)
        
        # 检查是否存在申请记录
        application_count = db.query(func.count(TopicApplication.id)).filter(
            TopicApplication.topic_id == topic_id
        ).scalar()
        
        if application_count > 0:
            raise BusinessException(message="存在申请记录，无法删除", code=400)
        
        db.delete(topic)
        db.commit()

    @staticmethod
    def publish_topic(db: Session, topic_id: int, tutor_id: int) -> Topic:
        """
        发布选题（DRAFT → PUBLISHED）
        
        Args:
            db: 数据库会话
            topic_id: 选题ID
            tutor_id: 导师ID
            
        Returns:
            更新后的选题对象
            
        Raises:
            BusinessException: 选题不存在、无权限、状态不允许发布
        """
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        # 数据权限检查
        if topic.tutor_id != tutor_id:
            raise BusinessException(message="无权限操作此选题", code=403)
        
        # 仅草稿状态可发布
        if topic.status != TopicStatus.DRAFT:
            raise BusinessException(message="仅草稿状态的选题可发布", code=400)
        
        topic.status = TopicStatus.PUBLISHED
        topic.published_at = datetime.now()
        topic.updated_at = datetime.now()
        
        db.commit()
        db.refresh(topic)
        
        return topic

    @staticmethod
    def lock_topic(db: Session, topic_id: int, tutor_id: int) -> Topic:
        """
        锁定选题（PUBLISHED → LOCKED）
        
        Args:
            db: 数据库会话
            topic_id: 选题ID
            tutor_id: 导师ID
            
        Returns:
            更新后的选题对象
            
        Raises:
            BusinessException: 选题不存在、无权限、状态不允许锁定
        """
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        # 数据权限检查
        if topic.tutor_id != tutor_id:
            raise BusinessException(message="无权限操作此选题", code=403)
        
        # 仅已发布状态可锁定
        if topic.status != TopicStatus.PUBLISHED:
            raise BusinessException(message="仅已发布状态的选题可锁定", code=400)
        
        topic.status = TopicStatus.LOCKED
        topic.locked_at = datetime.now()
        topic.updated_at = datetime.now()
        
        db.commit()
        db.refresh(topic)
        
        return topic

    @staticmethod
    def archive_topic(db: Session, topic_id: int, tutor_id: int) -> Topic:
        """
        归档选题（任意状态 → ARCHIVED）
        
        Args:
            db: 数据库会话
            topic_id: 选题ID
            tutor_id: 导师ID
            
        Returns:
            更新后的选题对象
            
        Raises:
            BusinessException: 选题不存在、无权限
        """
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        # 数据权限检查
        if topic.tutor_id != tutor_id:
            raise BusinessException(message="无权限操作此选题", code=403)
        
        topic.status = TopicStatus.ARCHIVED
        topic.archived_at = datetime.now()
        topic.updated_at = datetime.now()
        
        db.commit()
        db.refresh(topic)
        
        return topic

    @staticmethod
    def list_my_topics(db: Session, tutor_id: int, query: TopicListQuery) -> TopicListResponse:
        """
        查询导师的选题列表（分页）
        
        Args:
            db: 数据库会话
            tutor_id: 导师ID
            query: 查询参数
            
        Returns:
            分页后的选题列表
        """
        # 构建基础查询
        stmt = select(Topic).filter(Topic.tutor_id == tutor_id)
        
        # 状态筛选
        if query.status:
            stmt = stmt.filter(Topic.status == query.status)
        
        # 专业筛选
        if query.major_id:
            stmt = stmt.filter(Topic.major_id == query.major_id)
        
        # 学年筛选
        if query.academic_year:
            stmt = stmt.filter(Topic.academic_year == query.academic_year)
        
        # 学期筛选
        if query.term:
            stmt = stmt.filter(Topic.term == query.term)
        
        # 关键词搜索
        if query.keyword:
            keyword_pattern = f"%{query.keyword}%"
            stmt = stmt.filter(
                or_(
                    Topic.title.like(keyword_pattern),
                    Topic.description.like(keyword_pattern)
                )
            )
        
        # 统计总数
        total = db.query(func.count()).select_from(stmt.subquery()).scalar()
        
        # 分页查询
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(Topic.created_at.desc()).offset(offset).limit(query.page_size)
        
        topics = db.execute(stmt).scalars().all()
        
        # 转换为响应对象
        items = [TopicService._to_response(db, topic) for topic in topics]
        
        return TopicListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def get_topic_detail(db: Session, topic_id: int) -> TopicResponse:
        """
        获取选题详情（包含关联数据）
        
        Args:
            db: 数据库会话
            topic_id: 选题ID
            
        Returns:
            选题详情
            
        Raises:
            BusinessException: 选题不存在
        """
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        return TopicService._to_response(db, topic)

    @staticmethod
    def _to_response(db: Session, topic: Topic) -> TopicResponse:
        """
        将Topic对象转换为TopicResponse（联表查询关联数据）
        
        Args:
            db: 数据库会话
            topic: 选题对象
            
        Returns:
            选题响应对象
        """
        # 查询导师名
        tutor = db.query(User).filter(User.id == topic.tutor_id).first()
        tutor_name = tutor.real_name if tutor and tutor.real_name else "未知"
        
        # 查询专业和院系
        major = db.query(Major).filter(Major.id == topic.major_id).first()
        if major:
            major_name = major.name
            department = db.query(Department).filter(Department.id == major.department_id).first()
            department_name = department.name if department else "未知"
        else:
            major_name = "未知"
            department_name = "未知"
        
        return TopicResponse(
            id=topic.id,
            title=topic.title,
            description=topic.description,
            tutor_id=topic.tutor_id,
            tutor_name=tutor_name,
            major_id=topic.major_id,
            major_name=major_name,
            department_name=department_name,
            status=topic.status,
            max_students=topic.max_students,
            current_students=topic.current_students,
            academic_year=topic.academic_year,
            term=topic.term,
            published_at=topic.published_at,
            locked_at=topic.locked_at,
            archived_at=topic.archived_at,
            created_at=topic.created_at,
            updated_at=topic.updated_at
        )
