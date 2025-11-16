from .base import Base
from .department import Department
from .major import Major
from .user import User
from .user_major import UserMajor
from .role import Role
from .permission import Permission
from .user_role import UserRole
from .role_permission import RolePermission
from .topic import Topic
from .topic_application import TopicApplication
from .paper import Paper
from .paper_version import PaperVersion
from .paper_attachment import PaperAttachment
from .operation_log import OperationLog

__all__ = [
    "Base",
    "Department",
    "Major",
    "User",
    "UserMajor",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "Topic",
    "TopicApplication",
    "Paper",
    "PaperVersion",
    "PaperAttachment",
    "OperationLog",
]
