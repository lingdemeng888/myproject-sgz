"""Alembic迁移脚本模板

每次使用 alembic revision 命令时会使用此模板
Pylint模板变量：rev, down_revision, branch_labels, depends_on
"""

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """升级数据库"""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """回滚数据库"""
    ${downgrades if downgrades else "pass"}
