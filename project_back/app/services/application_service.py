"""
选题申请业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, case
from datetime import datetime
from typing import Optional

from app.constants.status import TopicStatus, ApplicationStatus
from app.models.topic import Topic
from app.models.topic_application import TopicApplication
from app.models.user import User
from app.models.major import Major
from app.models.department import Department
from app.models.paper import Paper
from app.services.log_service import LogService
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationListQuery,
    ApplicationListResponse,
    StudentTopicListQuery,
    StudentTopicResponse,
    StudentTopicListResponse,
    ApplicationDecisionRequest,
    TutorApplicationListQuery
)
from app.core.exceptions import BusinessException


class ApplicationService:
    """申请服务类"""

    @staticmethod
    def list_available_topics(
        db: Session,
        student_id: int,
        query: StudentTopicListQuery
    ) -> StudentTopicListResponse:
        """
        学生端：查询可申请的选题列表
        
        筛选规则：
        1. 状态必须是PUBLISHED（1）
        2. 剩余名额 > 0（current_students < max_students）
        3. 专业匹配（可选筛选）
        
        Args:
            db: 数据库会话
            student_id: 当前学生ID
            query: 查询参数
            
        Returns:
            分页后的选题列表
        """
        # 获取学生的专业信息
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            raise BusinessException(message="学生不存在", code=404)
        
        # 构建基础查询（强制status=1，有名额）
        print(f"[DEBUG] 开始构建查询条件...")
        print(f"[DEBUG] TopicStatus.PUBLISHED = {TopicStatus.PUBLISHED}")
        
        stmt = select(Topic).filter(
            Topic.status == TopicStatus.PUBLISHED,
            Topic.current_students < Topic.max_students
        )
        
        # 调试日志：查询所有选题（不带筛选）
        all_topics = db.query(Topic).all()
        print(f"[DEBUG] 数据库中总选题数: {len(all_topics)}")
        for t in all_topics:
            print(f"  - ID:{t.id}, 标题:{t.title}, 状态:{t.status}({TopicStatus.get_name(t.status)}), 名额:{t.current_students}/{t.max_students}")
            print(f"    status == PUBLISHED? {t.status == TopicStatus.PUBLISHED}")
            print(f"    current_students < max_students? {t.current_students < t.max_students}")
            print(f"    应该被筛选? {t.status == TopicStatus.PUBLISHED and t.current_students < t.max_students}")
        
        # 系部筛选（按系部而非专业）
        if student.department_id:
            # 如果学生有设置系部，只显示该系部下所有专业的选题
            stmt = stmt.join(Major, Topic.major_id == Major.id).filter(
                Major.department_id == student.department_id
            )
            print(f"[DEBUG] 按系部筛选: student.department_id = {student.department_id}")
        
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
        
        # 调试日志
        print(f"[DEBUG] 学生 {student_id} 查询选题: total={total}, page={query.page}, page_size={query.page_size}")
        print(f"[DEBUG] 筛选条件: status=1(PUBLISHED), current_students < max_students")
        
        # 分页查询 - MySQL兼容的排序（使用CASE处理NULL值）
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(
            case((Topic.published_at.is_(None), 0), else_=1).desc(),
            Topic.published_at.desc(),
            Topic.created_at.desc()
        ).offset(offset).limit(query.page_size)
        
        # 调试：打印生成的SQL
        print(f"[DEBUG] 执行查询...")
        
        topics = db.execute(stmt).scalars().all()
        
        # 调试日志
        print(f"[DEBUG] 查询到 {len(topics)} 条选题数据")
        if len(topics) > 0:
            for t in topics:
                print(f"  - 返回选题: ID:{t.id}, 标题:{t.title}")
        
        # 转换为响应对象
        items = [ApplicationService._to_student_topic_response(db, topic) for topic in topics]
        
        return StudentTopicListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def create_application(
        db: Session,
        student_id: int,
        data: ApplicationCreateRequest
    ) -> TopicApplication:
        """
        学生端：创建选题申请
        
        8步验证流程：
        1. 检查学生申请数量限制（最多2个活跃申请）
        2. 使用悲观锁查询选题
        3. 检查选题状态（必须是PUBLISHED）
        4. 专业匹配校验
        5. 检查重复申请
        6. 检查选题名额
        7. 插入申请记录（status=PENDING）
        8. 提交事务（不更新current_students）
        
        Args:
            db: 数据库会话
            student_id: 学生ID
            data: 申请数据
            
        Returns:
            创建的申请对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：检查学生申请数量限制 ==========
        active_count = db.query(func.count(TopicApplication.id)).filter(
            TopicApplication.student_id == student_id,
            TopicApplication.status.in_(ApplicationStatus.ACTIVE_STATUSES)  # [0, 1]
        ).scalar()
        
        if active_count >= 2:
            raise BusinessException(
                message="您最多只能同时申请2个选题，请等待审批结果或撤回已有申请",
                code=400
            )
        
        # ========== 步骤2：使用悲观锁查询选题 ==========
        topic = db.query(Topic).filter(
            Topic.id == data.topic_id
        ).with_for_update().first()  # 行级锁，防止并发问题
        
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        # ========== 步骤3：检查选题状态 ==========
        if topic.status != TopicStatus.PUBLISHED:
            raise BusinessException(
                message="该选题未发布或已关闭，无法申请",
                code=400
            )
        
        # ========== 步骤4：专业匹配校验 ==========
        student = db.query(User).filter(User.id == student_id).first()
        
        if not student:
            raise BusinessException(message="学生信息不存在", code=404)
        
        if not student.primary_major_id:
            raise BusinessException(
                message="您尚未设置专业，请先完善个人信息",
                code=400
            )
        
        if student.primary_major_id != topic.major_id:
            raise BusinessException(
                message="只能申请本专业的选题",
                code=403
            )
        
        # ========== 步骤5：检查重复申请 ==========
        existing = db.query(TopicApplication).filter(
            TopicApplication.topic_id == data.topic_id,
            TopicApplication.student_id == student_id
        ).first()
        
        if existing:
            raise BusinessException(
                message="您已申请过该选题，请勿重复申请",
                code=400
            )
        
        # ========== 步骤6：检查选题名额 ==========
        if topic.current_students >= topic.max_students:
            raise BusinessException(
                message="该选题名额已满",
                code=400
            )
        
        # ========== 步骤7：插入申请记录 ==========
        application = TopicApplication(
            topic_id=data.topic_id,
            student_id=student_id,
            status=ApplicationStatus.PENDING,  # 待审批
            application_reason=data.application_reason
        )
        
        db.add(application)
        
        # ========== 步骤8：提交事务 ==========
        # 注意：不更新topic.current_students
        # 将在模块9（导师审批通过时）更新
        db.commit()
        db.refresh(application)
        
        return application

    @staticmethod
    def list_my_applications(
        db: Session,
        student_id: int,
        query: ApplicationListQuery
    ) -> ApplicationListResponse:
        """
        学生端：查询我的申请列表
        
        Args:
            db: 数据库会话
            student_id: 学生ID
            query: 查询参数
            
        Returns:
            分页后的申请列表
        """
        # 构建基础查询
        stmt = select(TopicApplication).filter(
            TopicApplication.student_id == student_id
        )
        
        # 状态筛选
        if query.status is not None:
            if not ApplicationStatus.is_valid(query.status):
                raise BusinessException(
                    message="状态值无效，允许的值：0=待审批,1=通过,2=拒绝,3=取消",
                    code=400
                )
            stmt = stmt.filter(TopicApplication.status == query.status)
        
        # 统计总数
        total = db.query(func.count()).select_from(stmt.subquery()).scalar()
        
        # 分页查询（按创建时间倒序）
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(TopicApplication.created_at.desc()).offset(offset).limit(query.page_size)
        
        applications = db.execute(stmt).scalars().all()
        
        # 转换为响应对象
        items = [ApplicationService._to_application_response(db, app) for app in applications]
        
        return ApplicationListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def get_application_detail(
        db: Session,
        application_id: int,
        student_id: int
    ) -> ApplicationResponse:
        """
        学生端：获取申请详情
        
        Args:
            db: 数据库会话
            application_id: 申请ID
            student_id: 学生ID（用于权限校验）
            
        Returns:
            申请详情
            
        Raises:
            BusinessException: 申请不存在或无权限
        """
        application = db.query(TopicApplication).filter(
            TopicApplication.id == application_id
        ).first()
        
        if not application:
            raise BusinessException(message="申请记录不存在", code=404)
        
        # 数据权限检查
        if application.student_id != student_id:
            raise BusinessException(message="无权限查看此申请", code=403)
        
        return ApplicationService._to_application_response(db, application)

    @staticmethod
    def _to_student_topic_response(db: Session, topic: Topic) -> StudentTopicResponse:
        """
        将Topic转换为StudentTopicResponse（学生端）
        
        Args:
            db: 数据库会话
            topic: 选题对象
            
        Returns:
            学生端选题响应对象
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
        
        # 计算剩余名额
        available_slots = topic.max_students - topic.current_students
        
        return StudentTopicResponse(
            id=topic.id,
            title=topic.title,
            description=topic.description,
            tutor_id=topic.tutor_id,
            tutor_name=tutor_name,
            major_id=topic.major_id,
            major_name=major_name,
            department_name=department_name,
            max_students=topic.max_students,
            current_students=topic.current_students,
            available_slots=available_slots,
            academic_year=topic.academic_year,
            term=topic.term,
            published_at=topic.published_at,
            created_at=topic.created_at
        )

    @staticmethod
    def _to_application_response(db: Session, application: TopicApplication) -> ApplicationResponse:
        """
        将TopicApplication转换为ApplicationResponse
        
        Args:
            db: 数据库会话
            application: 申请对象
            
        Returns:
            申请响应对象
        """
        # 查询选题标题
        topic = db.query(Topic).filter(Topic.id == application.topic_id).first()
        topic_title = topic.title if topic else "未知"
        
        # 查询学生信息
        student = db.query(User).filter(User.id == application.student_id).first()
        student_name = student.real_name if student and student.real_name else "未知"
        student_no = student.student_no if student else None
        
        # 查询审批人信息
        decision_by_name = None
        if application.decision_by:
            decision_user = db.query(User).filter(User.id == application.decision_by).first()
            decision_by_name = decision_user.real_name if decision_user and decision_user.real_name else "未知"
        
        # 获取状态名称
        status_name = ApplicationStatus.get_name(application.status)
        
        # 查询关联的论文ID（如果已创建）
        paper_id = None
        academic_year = None
        term = None
        if topic:
            paper = db.query(Paper).filter(
                Paper.student_id == application.student_id,
                Paper.topic_id == application.topic_id
            ).first()
            if paper:
                paper_id = paper.id
            academic_year = topic.academic_year
            term = topic.term
        
        return ApplicationResponse(
            id=application.id,
            topic_id=application.topic_id,
            topic_title=topic_title,
            student_id=application.student_id,
            student_name=student_name,
            student_no=student_no,
            status=application.status,
            status_name=status_name,
            application_reason=application.application_reason,
            decision_by=application.decision_by,
            decision_by_name=decision_by_name,
            decision_at=application.decision_at,
            decision_comment=application.decision_comment,
            academic_year=academic_year,
            term=term,
            paper_id=paper_id,
            created_at=application.created_at,
            updated_at=application.updated_at
        )

    @staticmethod
    def list_tutor_applications(
        db: Session,
        tutor_id: int,
        query: TutorApplicationListQuery
    ) -> ApplicationListResponse:
        """
        导师端：查询我的选题的申请列表
        
        筛选规则：
        1. 通过topic关联筛选tutor_id
        2. 可选状态筛选
        3. 可选选题筛选
        4. 可选学生姓名搜索
        5. 按创建时间升序（先来先审）
        
        Args:
            db: 数据库会话
            tutor_id: 导师ID
            query: 查询参数
            
        Returns:
            分页后的申请列表
        """
        # ========== 构建基础查询 ==========
        stmt = select(TopicApplication).join(
            Topic,
            TopicApplication.topic_id == Topic.id
        ).filter(
            Topic.tutor_id == tutor_id
        )
        
        # ========== 状态筛选 ==========
        if query.status is not None:
            if not ApplicationStatus.is_valid(query.status):
                raise BusinessException(
                    message="状态值无效，允许的值：0=待审批,1=通过,2=拒绝",
                    code=400
                )
            stmt = stmt.filter(TopicApplication.status == query.status)
        
        # ========== 选题筛选 ==========
        if query.topic_id:
            stmt = stmt.filter(TopicApplication.topic_id == query.topic_id)
        
        # ========== 学生姓名搜索 ==========
        if query.student_name:
            stmt = stmt.join(
                User,
                TopicApplication.student_id == User.id
            ).filter(
                User.real_name.like(f"%{query.student_name}%")
            )
        
        # ========== 统计总数 ==========
        total = db.query(func.count()).select_from(stmt.subquery()).scalar()
        
        # ========== 分页查询 ==========
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(TopicApplication.created_at.asc()).offset(offset).limit(query.page_size)
        
        applications = db.execute(stmt).scalars().all()
        
        # ========== 转换响应 ==========
        items = [ApplicationService._to_application_response(db, app) for app in applications]
        
        return ApplicationListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def approve_application(
        db: Session,
        application_id: int,
        tutor_id: int,
        data: ApplicationDecisionRequest
    ) -> TopicApplication:
        """
        导师端：审批通过申请（含并发控制）
        
        10步验证流程：
        1. 查询申请记录
        2. 数据权限检查
        3. 检查申请状态
        4. 使用悲观锁锁定选题
        5. 检查选题状态
        6. 并发安全的人数检查（重新查询approved_count）
        7. 更新申请记录
        8. 递增选题人数
        9. 自动锁定逻辑
        10. 自动拒绝该学生的其他待审批申请
        
        Args:
            db: 数据库会话
            application_id: 申请ID
            tutor_id: 导师ID
            data: 审批数据
            
        Returns:
            更新后的申请对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：查询申请记录 ==========
        application = db.query(TopicApplication).filter(
            TopicApplication.id == application_id
        ).first()
        
        if not application:
            raise BusinessException(message="申请记录不存在", code=404)
        
        # ========== 步骤2：数据权限检查 ==========
        topic = db.query(Topic).filter(Topic.id == application.topic_id).first()
        if not topic:
            raise BusinessException(message="关联选题不存在", code=404)
        
        if topic.tutor_id != tutor_id:
            raise BusinessException(message="无权限审批此申请", code=403)
        
        # ========== 步骤3：检查申请状态 ==========
        if application.status != ApplicationStatus.PENDING:
            status_name = ApplicationStatus.get_name(application.status)
            raise BusinessException(
                message=f"该申请已被处理（当前状态：{status_name}）",
                code=400
            )
        
        # ========== 步骤4：使用悲观锁锁定选题 ==========
        stmt = select(Topic).where(Topic.id == application.topic_id).with_for_update()
        topic = db.execute(stmt).scalar_one_or_none()
        
        if not topic:
            raise BusinessException(message="选题不存在", code=404)
        
        # ========== 步骤5：检查选题状态 ==========
        if topic.status != TopicStatus.PUBLISHED:
            raise BusinessException(
                message="该选题未发布，无法审批",
                code=400
            )
        
        # ========== 步骤6：并发安全的人数检查（关键） ==========
        # 在悲观锁保护下，重新查询已通过人数
        approved_count = db.query(func.count(TopicApplication.id)).filter(
            TopicApplication.topic_id == application.topic_id,
            TopicApplication.status == ApplicationStatus.APPROVED  # 1
        ).scalar()
        
        if approved_count >= topic.max_students:
            raise BusinessException(
                message="该选题名额已满，无法审批通过",
                code=400
            )
        
        # ========== 步骤7：更新申请记录 ==========
        application.status = ApplicationStatus.APPROVED  # 1
        application.decision_by = tutor_id
        application.decision_at = datetime.now()
        application.decision_comment = data.decision_comment
        
        # ========== 步骤8：递增选题人数 ==========
        topic.current_students += 1
        
        # ========== 步骤9：自动锁定逻辑 ==========
        if topic.current_students >= topic.max_students:
            topic.status = TopicStatus.LOCKED  # 2
            topic.locked_at = datetime.now()
        
        # ========== 步骤10：自动拒绝该学生的其他待审批申请 ==========
        other_pending = db.query(TopicApplication).filter(
            TopicApplication.student_id == application.student_id,
            TopicApplication.id != application.id,
            TopicApplication.status == ApplicationStatus.PENDING
        ).all()
        
        for other_app in other_pending:
            other_app.status = ApplicationStatus.REJECTED
            other_app.decision_by = tutor_id
            other_app.decision_at = datetime.now()
            other_app.decision_comment = "系统自动关闭：您的选题申请已通过其他导师审批"
        
        # ========== 提交事务 ==========
        db.commit()
        db.refresh(application)
        
        # ========== 记录操作日志 ==========
        LogService.record_log(
            db=db,
            user_id=tutor_id,
            action="approve_application",
            resource_type="application",
            resource_id=application.id,
            detail={
                "student_id": application.student_id,
                "topic_id": application.topic_id,
                "topic_title": topic.title,
                "decision_comment": data.decision_comment,
                "topic_current_students": topic.current_students,
                "topic_max_students": topic.max_students,
                "topic_locked": topic.status == TopicStatus.LOCKED
            },
            ip_address=None
        )
        
        return application

    @staticmethod
    def reject_application(
        db: Session,
        application_id: int,
        tutor_id: int,
        data: ApplicationDecisionRequest
    ) -> TopicApplication:
        """
        导师端：审批拒绝申请
        
        5步验证流程：
        1. 查询申请记录
        2. 数据权限检查
        3. 检查申请状态
        4. 更新申请记录
        5. 提交事务（不修改topic）
        
        Args:
            db: 数据库会话
            application_id: 申请ID
            tutor_id: 导师ID
            data: 审批数据
            
        Returns:
            更新后的申请对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：查询申请记录 ==========
        application = db.query(TopicApplication).filter(
            TopicApplication.id == application_id
        ).first()
        
        if not application:
            raise BusinessException(message="申请记录不存在", code=404)
        
        # ========== 步骤2：数据权限检查 ==========
        topic = db.query(Topic).filter(Topic.id == application.topic_id).first()
        if not topic:
            raise BusinessException(message="关联选题不存在", code=404)
        
        if topic.tutor_id != tutor_id:
            raise BusinessException(message="无权限审批此申请", code=403)
        
        # ========== 步骤3：检查申请状态 ==========
        if application.status != ApplicationStatus.PENDING:
            status_name = ApplicationStatus.get_name(application.status)
            raise BusinessException(
                message=f"该申请已被处理（当前状态：{status_name}）",
                code=400
            )
        
        # ========== 步骤4：更新申请记录 ==========
        application.status = ApplicationStatus.REJECTED  # 2
        application.decision_by = tutor_id
        application.decision_at = datetime.now()
        application.decision_comment = data.decision_comment
        
        # ========== 步骤5：提交事务 ==========
        # 注意：拒绝不修改topic的current_students
        db.commit()
        db.refresh(application)
        
        # ========== 记录操作日志 ==========
        LogService.record_log(
            db=db,
            user_id=tutor_id,
            action="reject_application",
            resource_type="application",
            resource_id=application.id,
            detail={
                "student_id": application.student_id,
                "topic_id": application.topic_id,
                "topic_title": topic.title,
                "decision_comment": data.decision_comment
            },
            ip_address=None
        )
        
        return application
