"""
论文业务逻辑服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case
from datetime import datetime
from typing import Optional

from app.constants.status import PaperStatus, ApplicationStatus
from app.models.paper import Paper
from app.models.paper_version import PaperVersion
from app.models.paper_attachment import PaperAttachment
from app.models.topic_application import TopicApplication
from app.models.topic import Topic
from app.models.user import User
from app.schemas.paper import (
    PaperCreateRequest,
    PaperVersionCreateRequest,
    PaperResponse,
    PaperVersionResponse,
    PaperListQuery,
    PaperListItemResponse,
    PaperListResponse,
    PaperReviewRequest,
    TutorPaperListQuery
)
from app.schemas.attachment import AttachmentResponse, AttachmentListResponse
from app.core.exceptions import BusinessException


class PaperService:
    """论文服务类"""

    @staticmethod
    def create_paper(
        db: Session,
        student_id: int,
        data: PaperCreateRequest
    ) -> Paper:
        """
        学生端：创建论文
        
        验证流程：
        1. 验证学生对该topic_id有已通过的申请（status=1）
        2. 检查唯一性约束（uq_paper_student_term）
        3. 创建论文记录，默认status=0（编辑中）
        
        Args:
            db: 数据库会话
            student_id: 学生ID
            data: 论文创建数据
            
        Returns:
            创建的论文对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：验证学生有已通过的申请 ==========
        application = db.query(TopicApplication).filter(
            TopicApplication.topic_id == data.topic_id,
            TopicApplication.student_id == student_id,
            TopicApplication.status == ApplicationStatus.APPROVED  # 1
        ).first()
        
        if not application:
            raise BusinessException(
                message="您没有该选题的通过申请，无法创建论文",
                code=403
            )
        
        # ========== 步骤2：检查唯一性约束 ==========
        # 同一学生、同一学年学期只能有一篇论文
        existing = db.query(Paper).filter(
            Paper.student_id == student_id,
            Paper.academic_year == data.academic_year,
            Paper.term == data.term
        ).first()
        
        if existing:
            raise BusinessException(
                message=f"您在 {data.academic_year} 学年第 {data.term} 学期已有论文，不能重复创建",
                code=400
            )
        
        # ========== 步骤3：创建论文记录 ==========
        paper = Paper(
            topic_id=data.topic_id,
            student_id=student_id,
            title=data.title,
            abstract=data.abstract,
            keywords=data.keywords,
            status=PaperStatus.EDITING,  # 0
            academic_year=data.academic_year,
            term=data.term
        )
        
        db.add(paper)
        db.commit()
        db.refresh(paper)
        
        return paper

    @staticmethod
    def create_version(
        db: Session,
        paper_id: int,
        student_id: int,
        data: PaperVersionCreateRequest
    ) -> PaperVersion:
        """
        学生端：创建论文版本
        
        验证流程：
        1. 验证论文存在且属于当前学生
        2. 查询 MAX(version_no)+1 作为新版本号
        3. 插入 PaperVersion
        
        Args:
            db: 数据库会话
            paper_id: 论文ID
            student_id: 学生ID
            data: 版本数据
            
        Returns:
            创建的版本对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：验证论文存在且属于当前学生 ==========
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        
        if not paper:
            raise BusinessException(message="论文不存在", code=404)
        
        if paper.student_id != student_id:
            raise BusinessException(message="无权限操作此论文", code=403)
        
        # ========== 步骤2：查询最大版本号 ==========
        max_version = db.query(func.max(PaperVersion.version_no)).filter(
            PaperVersion.paper_id == paper_id
        ).scalar()
        
        new_version_no = (max_version or 0) + 1
        
        # ========== 步骤3：创建版本记录 ==========
        version = PaperVersion(
            paper_id=paper_id,
            version_no=new_version_no,
            content_text=data.content_text,
            content_format=data.content_format,
            submitted_by=student_id,
            notes=data.notes
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        return version

    @staticmethod
    def submit_paper(
        db: Session,
        paper_id: int,
        student_id: int
    ) -> Paper:
        """
        学生端：正式提交论文
        
        验证流程：
        1. 验证论文存在且属于当前学生
        2. 验证论文至少有一个版本
        3. 验证论文当前状态为编辑中（0）
        4. 更新status=1（已提交），设置submitted_at
        
        Args:
            db: 数据库会话
            paper_id: 论文ID
            student_id: 学生ID
            
        Returns:
            更新后的论文对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        # ========== 步骤1：验证论文存在且属于当前学生 ==========
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        
        if not paper:
            raise BusinessException(message="论文不存在", code=404)
        
        if paper.student_id != student_id:
            raise BusinessException(message="无权限操作此论文", code=403)
        
        # ========== 步骤2：验证至少有一个版本 ==========
        version_count = db.query(func.count(PaperVersion.id)).filter(
            PaperVersion.paper_id == paper_id
        ).scalar()
        
        if version_count == 0:
            raise BusinessException(
                message="论文尚未添加版本内容，无法提交",
                code=400
            )
        
        # ========== 步骤3：验证当前状态 ==========
        if paper.status != PaperStatus.EDITING:
            status_name = PaperStatus.get_name(paper.status)
            raise BusinessException(
                message=f"论文当前状态为 {status_name}，无法提交",
                code=400
            )
        
        # ========== 步骤4：更新状态 ==========
        paper.status = PaperStatus.SUBMITTED  # 1
        paper.submitted_at = datetime.now()
        
        db.commit()
        db.refresh(paper)
        
        return paper

    @staticmethod
    def list_my_papers(
        db: Session,
        student_id: int,
        query: PaperListQuery
    ) -> PaperListResponse:
        """
        学生端：查询我的论文列表
        
        筛选规则：
        1. 只显示当前学生的论文
        2. 可选状态筛选
        3. 可选学年学期筛选
        4. 按创建时间倒序
        
        Args:
            db: 数据库会话
            student_id: 学生ID
            query: 查询参数
            
        Returns:
            分页后的论文列表
        """
        # ========== 构建基础查询 ==========
        stmt = select(Paper).filter(Paper.student_id == student_id)
        
        # ========== 状态筛选 ==========
        if query.status is not None:
            if not PaperStatus.is_valid(query.status):
                raise BusinessException(
                    message="状态值无效",
                    code=400
                )
            stmt = stmt.filter(Paper.status == query.status)
        
        # ========== 学年筛选 ==========
        if query.academic_year:
            stmt = stmt.filter(Paper.academic_year == query.academic_year)
        
        # ========== 学期筛选 ==========
        if query.term:
            stmt = stmt.filter(Paper.term == query.term)
        
        # ========== 统计总数 ==========
        total = db.query(func.count()).select_from(stmt.subquery()).scalar()
        
        # ========== 分页查询 ==========
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(Paper.created_at.desc()).offset(offset).limit(query.page_size)
        
        papers = db.execute(stmt).scalars().all()
        
        # ========== 转换响应 ==========
        items = [PaperService._to_list_item_response(db, p) for p in papers]
        
        return PaperListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def get_paper_detail(
        db: Session,
        paper_id: int,
        student_id: int
    ) -> PaperResponse:
        """
        学生端：获取论文详情（含所有版本）
        
        Args:
            db: 数据库会话
            paper_id: 论文ID
            student_id: 学生ID
            
        Returns:
            论文详情
            
        Raises:
            BusinessException: 论文不存在或无权限
        """
        # ========== 查询论文 ==========
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        
        if not paper:
            raise BusinessException(message="论文不存在", code=404)
        
        if paper.student_id != student_id:
            raise BusinessException(message="无权限查看此论文", code=403)
        
        # ========== 转换响应 ==========
        return PaperService._to_paper_response(db, paper)

    # ========== 辅助方法 ==========

    @staticmethod
    def _to_paper_response(db: Session, paper: Paper) -> PaperResponse:
        """转换为完整的论文响应对象（含版本列表）"""
        # 查询选题标题
        topic = db.query(Topic).filter(Topic.id == paper.topic_id).first()
        topic_title = topic.title if topic else "未知"
        
        # 查询学生信息
        student = db.query(User).filter(User.id == paper.student_id).first()
        student_name = student.real_name if student and student.real_name else "未知"
        student_no = student.student_no if student else None
        
        # 查询所有版本
        versions = db.query(PaperVersion).filter(
            PaperVersion.paper_id == paper.id
        ).order_by(PaperVersion.version_no.desc()).all()
        
        version_responses = [
            PaperService._to_version_response(db, v) for v in versions
        ]
        
        # 获取状态名称
        status_name = PaperStatus.get_name(paper.status)
        term_name = "上学期" if paper.term == 1 else "下学期"
        
        return PaperResponse(
            id=paper.id,
            topic_id=paper.topic_id,
            topic_title=topic_title,
            student_id=paper.student_id,
            student_name=student_name,
            student_no=student_no,
            title=paper.title,
            abstract=paper.abstract,
            keywords=paper.keywords,
            status=paper.status,
            status_name=status_name,
            academic_year=paper.academic_year,
            term=paper.term,
            term_name=term_name,
            submitted_at=paper.submitted_at,
            created_at=paper.created_at,
            updated_at=paper.updated_at,
            versions=version_responses
        )

    @staticmethod
    def _to_list_item_response(db: Session, paper: Paper) -> PaperListItemResponse:
        """转换为列表项响应对象（不含版本内容）"""
        # 查询选题标题
        topic = db.query(Topic).filter(Topic.id == paper.topic_id).first()
        topic_title = topic.title if topic else "未知"
        
        # 查询学生信息
        student = db.query(User).filter(User.id == paper.student_id).first()
        student_name = student.real_name if student and student.real_name else "未知"
        student_no = student.student_no if student else None
        
        # 查询版本统计
        version_count = db.query(func.count(PaperVersion.id)).filter(
            PaperVersion.paper_id == paper.id
        ).scalar()
        
        latest_version_no = db.query(func.max(PaperVersion.version_no)).filter(
            PaperVersion.paper_id == paper.id
        ).scalar()
        
        # 获取状态名称
        status_name = PaperStatus.get_name(paper.status)
        term_name = "上学期" if paper.term == 1 else "下学期"
        
        return PaperListItemResponse(
            id=paper.id,
            topic_id=paper.topic_id,
            topic_title=topic_title,
            student_id=paper.student_id,
            student_name=student_name,
            student_no=student_no,
            title=paper.title,
            status=paper.status,
            status_name=status_name,
            academic_year=paper.academic_year,
            term=paper.term,
            term_name=term_name,
            version_count=version_count,
            latest_version_no=latest_version_no,
            created_at=paper.created_at,
            updated_at=paper.updated_at,
            submitted_at=paper.submitted_at
        )

    @staticmethod
    def _to_version_response(db: Session, version: PaperVersion, include_content: bool = True) -> PaperVersionResponse:
        """转换为版本响应对象"""
        # 查询提交人信息
        submitter = db.query(User).filter(User.id == version.submitted_by).first()
        submitter_name = submitter.real_name if submitter and submitter.real_name else "未知"
        
        # 查询评审人信息
        reviewer_name = None
        if version.reviewed_by:
            reviewer = db.query(User).filter(User.id == version.reviewed_by).first()
            reviewer_name = reviewer.real_name if reviewer and reviewer.real_name else "未知"
        
        # 格式名称映射
        format_names = {
            0: "无",
            1: "Markdown",
            2: "HTML",
            3: "纯文本"
        }
        content_format_name = format_names.get(version.content_format, "未知")
        
        # 查询附件列表
        from app.models.paper_attachment import PaperAttachment
        attachments = db.query(PaperAttachment).filter(
            PaperAttachment.paper_version_id == version.id
        ).all()
        
        attachment_list = [{
            'id': att.id,
            'file_name': att.file_name,
            'file_size': att.file_size,
            'storage_url': att.storage_url,
            'mime_type': att.mime_type,
            'uploaded_at': att.uploaded_at
        } for att in attachments]
        
        return PaperVersionResponse(
            id=version.id,
            paper_id=version.paper_id,
            version_no=version.version_no,
            content=version.content_text if include_content else None,
            content_format=version.content_format,
            content_format_name=content_format_name,
            is_final=version.is_final,
            submitted_by=version.submitted_by,
            submitted_by_name=submitter_name,
            submitted_at=version.submitted_at,
            notes=version.notes,
            attachments=attachment_list,
            review_comment=version.review_comment,
            reviewed_by=version.reviewed_by,
            reviewed_by_name=reviewer_name,
            reviewed_at=version.reviewed_at
        )

    # ========== 附件管理方法 ==========

    @staticmethod
    def add_attachment(
        db: Session,
        version_id: int,
        file_info: dict,
        user_id: int
    ) -> PaperAttachment:
        """
        添加论文附件（含权限验证）
        
        验证流程：
        1. 查询版本是否存在
        2. 查询版本关联的论文
        3. 验证论文属于当前用户（关键权限验证）
        4. 插入附件记录
        
        Args:
            db: 数据库会话
            version_id: 论文版本ID
            file_info: 文件信息字典（来自FileStorage.save_attachment）
            user_id: 当前用户ID
            
        Returns:
            创建的附件对象
            
        Raises:
            BusinessException: 版本不存在、无权限、其他错误
        """
        # ========== 步骤1：查询版本 ==========
        version = db.query(PaperVersion).filter(
            PaperVersion.id == version_id
        ).first()
        
        if not version:
            raise BusinessException(message="论文版本不存在", code=404)
        
        # ========== 步骤2：查询版本关联的论文 ==========
        paper = db.query(Paper).filter(Paper.id == version.paper_id).first()
        
        if not paper:
            raise BusinessException(message="关联论文不存在", code=404)
        
        # ========== 步骤3：验证论文属于当前用户（关键） ==========
        if paper.student_id != user_id:
            raise BusinessException(
                message="无权限操作此版本，只能为自己的论文添加附件",
                code=403
            )
        
        # ========== 步骤4：插入附件记录 ==========
        attachment = PaperAttachment(
            paper_version_id=version_id,
            file_name=file_info['file_name'],
            mime_type=file_info['mime_type'],
            file_size=file_info['file_size'],
            storage_url=file_info['storage_url'],
            file_hash=file_info['file_hash'],
            uploaded_by=user_id
        )
        
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        
        return attachment

    @staticmethod
    def delete_attachment(
        db: Session,
        attachment_id: int,
        user_id: int
    ) -> bool:
        """
        删除附件（仅删除数据库记录，不删除物理文件）
        
        验证流程：
        1. 查询附件是否存在
        2. 查询附件关联的版本和论文
        3. 验证论文属于当前用户
        4. 删除附件记录
        
        注意：由于哈希去重，不删除物理文件，避免影响其他论文
        
        Args:
            db: 数据库会话
            attachment_id: 附件ID
            user_id: 当前用户ID
            
        Returns:
            是否删除成功
            
        Raises:
            BusinessException: 附件不存在、无权限
        """
        # ========== 步骤1：查询附件 ==========
        attachment = db.query(PaperAttachment).filter(
            PaperAttachment.id == attachment_id
        ).first()
        
        if not attachment:
            raise BusinessException(message="附件不存在", code=404)
        
        # ========== 步骤2：查询版本和论文 ==========
        version = db.query(PaperVersion).filter(
            PaperVersion.id == attachment.paper_version_id
        ).first()
        
        if not version:
            raise BusinessException(message="关联版本不存在", code=404)
        
        paper = db.query(Paper).filter(Paper.id == version.paper_id).first()
        
        if not paper:
            raise BusinessException(message="关联论文不存在", code=404)
        
        # ========== 步骤3：验证权限 ==========
        if paper.student_id != user_id:
            raise BusinessException(
                message="无权限删除此附件，只能删除自己的附件",
                code=403
            )
        
        # ========== 步骤4：删除附件记录 ==========
        db.delete(attachment)
        db.commit()
        
        return True

    @staticmethod
    def get_attachment_detail(
        db: Session,
        attachment_id: int,
        user_id: int
    ) -> PaperAttachment:
        """
        获取附件详情（含权限验证）
        
        权限：论文学生或导师可查看
        
        Args:
            db: 数据库会话
            attachment_id: 附件ID
            user_id: 当前用户ID
            
        Returns:
            附件对象
            
        Raises:
            BusinessException: 附件不存在、无权限
        """
        # ========== 查询附件 ==========
        attachment = db.query(PaperAttachment).filter(
            PaperAttachment.id == attachment_id
        ).first()
        
        if not attachment:
            raise BusinessException(message="附件不存在", code=404)
        
        # ========== 查询版本和论文 ==========
        version = db.query(PaperVersion).filter(
            PaperVersion.id == attachment.paper_version_id
        ).first()
        
        if not version:
            raise BusinessException(message="关联版本不存在", code=404)
        
        paper = db.query(Paper).filter(Paper.id == version.paper_id).first()
        
        if not paper:
            raise BusinessException(message="关联论文不存在", code=404)
        
        # ========== 权限验证：学生本人或导师 ==========
        # 获取导师ID
        topic = db.query(Topic).filter(Topic.id == paper.topic_id).first()
        tutor_id = topic.tutor_id if topic else None
        
        if paper.student_id != user_id and tutor_id != user_id:
            raise BusinessException(
                message="无权限查看此附件，只有论文学生或导师可查看",
                code=403
            )
        
        return attachment

    @staticmethod
    def list_version_attachments(
        db: Session,
        version_id: int,
        user_id: int
    ) -> AttachmentListResponse:
        """
        查询版本的所有附件（含权限验证）
        
        Args:
            db: 数据库会话
            version_id: 版本ID
            user_id: 当前用户ID
            
        Returns:
            附件列表
            
        Raises:
            BusinessException: 版本不存在、无权限
        """
        # ========== 查询版本和论文 ==========
        version = db.query(PaperVersion).filter(
            PaperVersion.id == version_id
        ).first()
        
        if not version:
            raise BusinessException(message="版本不存在", code=404)
        
        paper = db.query(Paper).filter(Paper.id == version.paper_id).first()
        
        if not paper:
            raise BusinessException(message="关联论文不存在", code=404)
        
        # ========== 权限验证 ==========
        topic = db.query(Topic).filter(Topic.id == paper.topic_id).first()
        tutor_id = topic.tutor_id if topic else None
        
        if paper.student_id != user_id and tutor_id != user_id:
            raise BusinessException(
                message="无权限查看此版本的附件",
                code=403
            )
        
        # ========== 查询附件列表 ==========
        attachments = db.query(PaperAttachment).filter(
            PaperAttachment.paper_version_id == version_id
        ).order_by(PaperAttachment.uploaded_at.desc()).all()
        
        # ========== 转换响应 ==========
        items = [PaperService._to_attachment_response(db, att) for att in attachments]
        
        return AttachmentListResponse(
            total=len(items),
            items=items
        )

    @staticmethod
    def _to_attachment_response(db: Session, attachment: PaperAttachment) -> AttachmentResponse:
        """转换为附件响应对象"""
        # 查询上传人信息
        uploader = db.query(User).filter(User.id == attachment.uploaded_by).first()
        uploader_name = uploader.real_name if uploader and uploader.real_name else "未知"
        
        return AttachmentResponse(
            id=attachment.id,
            paper_version_id=attachment.paper_version_id,
            file_name=attachment.file_name,
            mime_type=attachment.mime_type,
            file_size=attachment.file_size,
            storage_url=attachment.storage_url,
            file_hash=attachment.file_hash,
            uploaded_by=attachment.uploaded_by,
            uploaded_by_name=uploader_name,
            uploaded_at=attachment.uploaded_at
        )

    # ========== 导师评审方法 ==========

    @staticmethod
    def review_paper(
        db: Session,
        paper_id: int,
        tutor_id: int,
        status: int,
        review_comment: str,
        ip_address: Optional[str] = None
    ) -> Paper:
        """
        导师端：评审论文
        
        验证流程：
        1. 查询论文是否存在
        2. 通过topic.tutor_id验证导师权限
        3. 验证状态流转规则（1→2/3/4，不允许重复通过）
        4. 更新论文状态
        5. 记录操作日志（含旧/新状态、评审意见）
        
        Args:
            db: 数据库会话
            paper_id: 论文ID
            tutor_id: 导师ID
            status: 新状态（2=评审中, 3=待修改, 4=通过）
            review_comment: 评审意见
            ip_address: 操作IP地址
            
        Returns:
            更新后的论文对象
            
        Raises:
            BusinessException: 各种业务异常
        """
        from app.models.operation_log import OperationLog
        import json
        
        # ========== 步骤1：查询论文 ==========
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        
        if not paper:
            raise BusinessException(message="论文不存在", code=404)
        
        # ========== 步骤2：验证导师权限 ==========
        topic = db.query(Topic).filter(Topic.id == paper.topic_id).first()
        
        if not topic:
            raise BusinessException(message="关联选题不存在", code=404)
        
        if topic.tutor_id != tutor_id:
            raise BusinessException(
                message="无权限评审此论文，只能评审自己指导的学生论文",
                code=403
            )
        
        # ========== 步骤3：验证状态流转规则 ==========
        old_status = paper.status
        old_status_name = PaperStatus.get_name(old_status)
        new_status_name = PaperStatus.get_name(status)
        
        # 规则1：只能评审已提交的论文
        if old_status == PaperStatus.EDITING:  # 0
            raise BusinessException(
                message="论文尚未提交，无法评审",
                code=400
            )
        
        # 规则2：不允许重复评审已通过的论文
        if old_status == PaperStatus.APPROVED:  # 4
            raise BusinessException(
                message="论文已通过评审，不能重复评审",
                code=400
            )
        
        # 规则3：已归档论文不可评审
        if old_status == PaperStatus.ARCHIVED:  # 5
            raise BusinessException(
                message="论文已归档，无法评审",
                code=400
            )
        
        # ========== 步骤4：更新论文状态 ==========
        paper.status = status
        
        # ========== 步骤4.5：保存评审意见到最新版本 ==========
        from datetime import datetime
        latest_version = db.query(PaperVersion).filter(
            PaperVersion.paper_id == paper_id
        ).order_by(PaperVersion.version_no.desc()).first()
        
        if latest_version:
            latest_version.review_comment = review_comment
            latest_version.reviewed_by = tutor_id
            latest_version.reviewed_at = datetime.now()
        
        db.commit()
        db.refresh(paper)
        
        # ========== 步骤5：记录操作日志 ==========
        operation_detail = {
            "old_status": old_status,
            "old_status_name": old_status_name,
            "new_status": status,
            "new_status_name": new_status_name,
            "review_comment": review_comment,
            "paper_id": paper_id,
            "paper_title": paper.title,
            "student_id": paper.student_id
        }
        
        operation_log = OperationLog(
            actor_id=tutor_id,
            action="review_paper",
            target_table="paper",
            target_id=paper_id,
            detail=json.dumps(operation_detail, ensure_ascii=False),
            ip=ip_address
        )
        
        db.add(operation_log)
        db.commit()
        
        return paper

    @staticmethod
    def list_student_papers(
        db: Session,
        tutor_id: int,
        query: TutorPaperListQuery
    ) -> PaperListResponse:
        """
        导师端：查询指导学生的论文列表
        
        筛选规则：
        1. 通过topic.tutor_id筛选导师指导的论文
        2. 可选状态、学年、学期筛选
        3. 可选学生姓名模糊搜索
        4. 按提交时间倒序
        
        Args:
            db: 数据库会话
            tutor_id: 导师ID
            query: 查询参数
            
        Returns:
            分页后的论文列表
        """
        # ========== 构建基础查询 ==========
        # JOIN topic 筛选 tutor_id
        stmt = select(Paper).join(
            Topic, Paper.topic_id == Topic.id
        ).filter(
            Topic.tutor_id == tutor_id
        )
        
        # ========== 状态筛选 ==========
        if query.status is not None:
            if not PaperStatus.is_valid(query.status):
                raise BusinessException(message="状态值无效", code=400)
            stmt = stmt.filter(Paper.status == query.status)
        
        # ========== 学年筛选 ==========
        if query.academic_year:
            stmt = stmt.filter(Paper.academic_year == query.academic_year)
        
        # ========== 学期筛选 ==========
        if query.term:
            stmt = stmt.filter(Paper.term == query.term)
        
        # ========== 学生姓名模糊搜索 ==========
        if query.student_name:
            stmt = stmt.join(
                User, Paper.student_id == User.id
            ).filter(
                User.real_name.like(f"%{query.student_name}%")
            )
        
        # ========== 统计总数 ==========
        total = db.query(func.count()).select_from(stmt.subquery()).scalar()
        
        # ========== 分页查询 ==========
        offset = (query.page - 1) * query.page_size
        # MySQL不支持NULLS FIRST，使用CASE实现相同效果
        # submitted_at为NULL的排在前面（DESC时，1在前，0在后）
        stmt = stmt.order_by(
            case((Paper.submitted_at.is_(None), 1), else_=0).desc(),
            Paper.submitted_at.desc(),
            Paper.created_at.desc()
        ).offset(offset).limit(query.page_size)
        
        papers = db.execute(stmt).scalars().all()
        
        # ========== 转换响应 ==========
        items = [PaperService._to_list_item_response(db, p) for p in papers]
        
        return PaperListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def get_paper_detail_for_tutor(
        db: Session,
        paper_id: int,
        tutor_id: int
    ) -> PaperResponse:
        """
        导师端：获取论文详情（含所有版本）
        
        验证流程：
        1. 查询论文是否存在
        2. 通过topic.tutor_id验证导师权限
        3. 返回完整论文详情
        
        Args:
            db: 数据库会话
            paper_id: 论文ID
            tutor_id: 导师ID
            
        Returns:
            论文详情
            
        Raises:
            BusinessException: 论文不存在或无权限
        """
        # ========== 查询论文 ==========
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        
        if not paper:
            raise BusinessException(message="论文不存在", code=404)
        
        # ========== 验证导师权限 ==========
        topic = db.query(Topic).filter(Topic.id == paper.topic_id).first()
        
        if not topic:
            raise BusinessException(message="关联选题不存在", code=404)
        
        if topic.tutor_id != tutor_id:
            raise BusinessException(
                message="无权限查看此论文，只能查看自己指导的学生论文",
                code=403
            )
        
        # ========== 转换响应 ==========
        return PaperService._to_paper_response(db, paper)

