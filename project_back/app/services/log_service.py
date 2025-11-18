"""
日志服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from typing import Optional
import json

from app.models.operation_log import OperationLog
from app.models.user import User
from app.schemas.log import LogListQuery, LogListResponse, OperationLogResponse


class LogService:
    """日志服务类"""

    @staticmethod
    def record_log(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        detail: Optional[dict] = None,
        ip_address: Optional[str] = None
    ) -> Optional[OperationLog]:
        """
        记录操作日志
        
        关键特性：
        1. detail自动转JSON（使用ensure_ascii=False保留中文）
        2. 失败不抛异常（仅打印日志）
        3. 与主业务解耦
        
        Args:
            db: 数据库会话
            user_id: 操作人ID
            action: 操作类型（CREATE/UPDATE/DELETE/APPROVE/REJECT等）
            resource_type: 资源类型（user/topic/paper/application等）
            resource_id: 资源ID
            detail: 详细信息（dict，自动转JSON）
            ip_address: 操作IP
            
        Returns:
            OperationLog对象（或None如果失败）
        """
        try:
            # 步骤1：转换detail为JSON字符串
            detail_json = None
            if detail:
                detail_json = json.dumps(detail, ensure_ascii=False)
            
            # 步骤2：创建日志记录
            log = OperationLog(
                actor_id=user_id,
                action=action,
                target_table=resource_type,
                target_id=resource_id,
                detail=detail_json,
                ip=ip_address
            )
            
            # 步骤3：提交到数据库
            db.add(log)
            db.commit()
            db.refresh(log)
            
            return log
            
        except Exception as e:
            # 步骤4：失败时回滚并打印错误
            db.rollback()
            print(f"[LogService] 记录日志失败: {str(e)}")
            return None

    @staticmethod
    def query_logs(
        db: Session,
        query: LogListQuery
    ) -> LogListResponse:
        """
        查询操作日志
        
        验证流程：
        1. 构建基础查询（LEFT JOIN user表）
        2. 应用用户ID筛选
        3. 应用操作类型筛选
        4. 应用资源类型筛选
        5. 应用时间范围筛选
        6. 应用关键词搜索（操作人姓名/用户名）
        7. 统计总数
        8. 分页查询并加载用户信息
        9. 转换为响应对象
        
        Args:
            db: 数据库会话
            query: 查询参数
            
        Returns:
            LogListResponse（含total, page, page_size, items）
        """
        # ========== 步骤1：构建基础查询 ==========
        stmt = select(OperationLog).outerjoin(
            User, OperationLog.actor_id == User.id
        )
        
        # ========== 步骤2：应用用户ID筛选 ==========
        if query.user_id:
            stmt = stmt.filter(OperationLog.actor_id == query.user_id)
        
        # ========== 步骤3：应用操作类型筛选 ==========
        if query.action:
            stmt = stmt.filter(OperationLog.action == query.action)
        
        # ========== 步骤4：应用资源类型筛选 ==========
        if query.resource_type:
            stmt = stmt.filter(OperationLog.target_table == query.resource_type)
        
        # ========== 步骤5：应用时间范围筛选 ==========
        if query.start_date:
            stmt = stmt.filter(OperationLog.created_at >= query.start_date)
        if query.end_date:
            stmt = stmt.filter(OperationLog.created_at <= query.end_date)
        
        # ========== 步骤6：应用关键词搜索 ==========
        if query.keyword:
            stmt = stmt.filter(
                or_(
                    User.username.like(f"%{query.keyword}%"),
                    User.real_name.like(f"%{query.keyword}%")
                )
            )
        
        # ========== 步骤7：统计总数 ==========
        total = db.query(func.count()).select_from(stmt.subquery()).scalar()
        
        # ========== 步骤8：分页查询 ==========
        offset = (query.page - 1) * query.page_size
        stmt = stmt.order_by(OperationLog.created_at.desc()).offset(offset).limit(query.page_size)
        
        logs = db.execute(stmt).scalars().all()
        
        # ========== 步骤9：转换响应 ==========
        items = [LogService._to_log_response(db, log) for log in logs]
        
        return LogListResponse(
            total=total,
            page=query.page,
            page_size=query.page_size,
            items=items
        )

    @staticmethod
    def _to_log_response(db: Session, log: OperationLog) -> OperationLogResponse:
        """转换为日志响应对象"""
        # 查询操作人信息
        username = None
        real_name = None
        if log.actor_id:
            user = db.query(User).filter(User.id == log.actor_id).first()
            if user:
                username = user.username
                real_name = user.real_name
        
        return OperationLogResponse(
            id=log.id,
            user_id=log.actor_id,
            username=username,
            real_name=real_name,
            action=log.action,
            resource_type=log.target_table,
            resource_id=log.target_id,
            detail=log.detail,
            ip_address=log.ip,
            created_at=log.created_at
        )
