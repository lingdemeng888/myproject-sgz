"""
状态常量定义
集中管理所有状态枚举值，避免魔法数字
"""


class TopicStatus:
    """选题状态枚举（TINYINT数字类型）"""
    DRAFT = 0      # 草稿
    PUBLISHED = 1  # 发布
    LOCKED = 2     # 锁定
    ARCHIVED = 3   # 归档

    # 映射字典（用于日志/调试）
    NAMES = {
        0: "草稿",
        1: "发布",
        2: "锁定",
        3: "归档"
    }

    # 允许的状态值集合
    VALID_VALUES = {DRAFT, PUBLISHED, LOCKED, ARCHIVED}

    @classmethod
    def is_valid(cls, status: int) -> bool:
        """验证状态值是否合法"""
        return status in cls.VALID_VALUES

    @classmethod
    def get_name(cls, status: int) -> str:
        """获取状态名称"""
        return cls.NAMES.get(status, "未知")


class ApplicationStatus:
    """申请状态枚举（TINYINT数字类型）"""
    PENDING = 0    # 待审批
    APPROVED = 1   # 通过
    REJECTED = 2   # 拒绝
    WITHDRAWN = 3  # 取消（学生主动撤回）

    # 映射字典
    NAMES = {
        0: "待审批",
        1: "通过",
        2: "拒绝",
        3: "取消"
    }

    # 允许的状态值集合
    VALID_VALUES = {PENDING, APPROVED, REJECTED, WITHDRAWN}

    # 活跃状态（占用名额的状态）
    ACTIVE_STATUSES = {PENDING, APPROVED}  # 用于学生申请数量限制

    @classmethod
    def is_valid(cls, status: int) -> bool:
        """验证状态值是否合法"""
        return status in cls.VALID_VALUES

    @classmethod
    def get_name(cls, status: int) -> str:
        """获取状态名称"""
        return cls.NAMES.get(status, "未知")

    @classmethod
    def is_active(cls, status: int) -> bool:
        """判断是否为活跃状态（占用名额）"""
        return status in cls.ACTIVE_STATUSES


class PaperStatus:
    """论文状态枚举（TINYINT数字类型）"""
    EDITING = 0      # 编辑中（草稿）
    SUBMITTED = 1    # 已提交
    REVIEWING = 2    # 评审中
    REVISING = 3     # 待修改
    APPROVED = 4     # 通过
    ARCHIVED = 5     # 归档

    # 映射字典
    NAMES = {
        0: "编辑中",
        1: "已提交",
        2: "评审中",
        3: "待修改",
        4: "通过",
        5: "归档"
    }

    # 允许的状态值集合
    VALID_VALUES = {EDITING, SUBMITTED, REVIEWING, REVISING, APPROVED, ARCHIVED}

    @classmethod
    def is_valid(cls, status: int) -> bool:
        """验证状态值是否合法"""
        return status in cls.VALID_VALUES

    @classmethod
    def get_name(cls, status: int) -> str:
        """获取状态名称"""
        return cls.NAMES.get(status, "未知")


class UserStatus:
    """用户状态枚举（TINYINT数字类型）"""
    DISABLED = 0  # 禁用
    ENABLED = 1   # 启用

    # 映射字典
    NAMES = {
        0: "禁用",
        1: "启用"
    }

    # 允许的状态值集合
    VALID_VALUES = {DISABLED, ENABLED}

    @classmethod
    def is_valid(cls, status: int) -> bool:
        """验证状态值是否合法"""
        return status in cls.VALID_VALUES

    @classmethod
    def get_name(cls, status: int) -> str:
        """获取状态名称"""
        return cls.NAMES.get(status, "未知")
