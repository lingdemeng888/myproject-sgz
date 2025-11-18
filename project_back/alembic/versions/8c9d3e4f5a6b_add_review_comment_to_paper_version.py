"""添加论文版本评审意见字段

为paper_version表添加review_comment和reviewed_by字段，用于存储导师评审意见

Revision ID: 8c9d3e4f5a6b
Revises: 7baa5b97e43c
Create Date: 2025-11-18
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = '8c9d3e4f5a6b'
down_revision = '7baa5b97e43c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级数据库"""
    # 检查字段是否已存在
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('paper_version')]
    
    # 为 paper_version 表添加评审意见相关字段（如果不存在）
    if 'review_comment' not in columns:
        op.add_column('paper_version', 
            sa.Column('review_comment', sa.Text(), nullable=True, comment='导师评审意见'))
    
    if 'reviewed_by' not in columns:
        op.add_column('paper_version',
            sa.Column('reviewed_by', mysql.BIGINT(unsigned=True), nullable=True, comment='评审导师ID'))
    
    if 'reviewed_at' not in columns:
        op.add_column('paper_version',
            sa.Column('reviewed_at', sa.DateTime(timezone=False), nullable=True, comment='评审时间'))
    
    # 检查外键是否已存在
    foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('paper_version')]
    if 'fk_version_reviewer' not in foreign_keys and 'reviewed_by' in columns:
        # 添加外键约束
        op.create_foreign_key(
            'fk_version_reviewer',
            'paper_version', 'user',
            ['reviewed_by'], ['id'],
            onupdate='RESTRICT', ondelete='SET NULL'
        )


def downgrade() -> None:
    """回滚数据库"""
    # 删除外键约束
    op.drop_constraint('fk_version_reviewer', 'paper_version', type_='foreignkey')
    
    # 删除字段
    op.drop_column('paper_version', 'reviewed_at')
    op.drop_column('paper_version', 'reviewed_by')
    op.drop_column('paper_version', 'review_comment')
