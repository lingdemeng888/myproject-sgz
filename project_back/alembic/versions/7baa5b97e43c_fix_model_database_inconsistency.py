"""修复数据库模型不一致问题

修复内容:
1. topic_application表: 将remark字段拆分为application_reason和decision_comment
2. topic表: 确保academic_year和term字段存在(已在数据库中存在)
3. paper_attachment表: 确保使用paper_version_id而非paper_id(已在数据库中正确)

Revision ID: 7baa5b97e43c
Revises: 76fb9b2d9535
Create Date: 2025-11-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '7baa5b97e43c'
down_revision = '76fb9b2d9535'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级数据库"""
    # 1. 修改 topic_application 表
    # 检查是否存在 remark 字段，如果存在则进行迁移
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('topic_application')]
    
    if 'remark' in columns:
        # 如果存在旧的 remark 字段，添加新字段并迁移数据
        op.add_column('topic_application', 
            sa.Column('application_reason', sa.Text(), nullable=True, comment='申请理由'))
        op.add_column('topic_application', 
            sa.Column('decision_comment', sa.Text(), nullable=True, comment='审批意见'))
        
        # 迁移数据：将 remark 的值复制到 application_reason（待审批状态）或 decision_comment（已审批状态）
        # 注意：这是简化的迁移策略，实际可能需要根据业务逻辑调整
        connection.execute(sa.text("""
            UPDATE topic_application 
            SET application_reason = remark 
            WHERE status = 0 AND remark IS NOT NULL
        """))
        
        connection.execute(sa.text("""
            UPDATE topic_application 
            SET decision_comment = remark 
            WHERE status IN (1, 2) AND remark IS NOT NULL
        """))
        
        # 删除旧的 remark 字段
        op.drop_column('topic_application', 'remark')
    
    elif 'application_reason' not in columns:
        # 如果 remark 已被删除但新字段不存在，直接添加新字段
        op.add_column('topic_application', 
            sa.Column('application_reason', sa.Text(), nullable=True, comment='申请理由'))
        op.add_column('topic_application', 
            sa.Column('decision_comment', sa.Text(), nullable=True, comment='审批意见'))


def downgrade() -> None:
    """回滚数据库"""
    # 回滚时将两个字段合并回 remark 字段
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('topic_application')]
    
    if 'application_reason' in columns:
        # 添加 remark 字段
        op.add_column('topic_application',
            sa.Column('remark', mysql.VARCHAR(length=255), nullable=True, comment='申请备注/拒绝原因'))
        
        # 迁移数据：优先使用 decision_comment，其次使用 application_reason
        connection.execute(sa.text("""
            UPDATE topic_application 
            SET remark = COALESCE(decision_comment, application_reason)
            WHERE decision_comment IS NOT NULL OR application_reason IS NOT NULL
        """))
        
        # 删除新字段
        op.drop_column('topic_application', 'decision_comment')
        op.drop_column('topic_application', 'application_reason')
