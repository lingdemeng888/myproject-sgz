/**
 * 常量定义中心
 */

// ==================== API配置 ====================
// 后端API基础地址 (开发环境)
const API_BASE_URL = 'http://localhost:8000/api/v1';

// ==================== 角色定义 ====================
const ROLE = {
  STUDENT: 'STUDENT',   // 学生
  TUTOR: 'TUTOR',       // 导师
  ADMIN: 'ADMIN'        // 管理员
};

const ROLE_TEXT = {
  'STUDENT': '学生',
  'TUTOR': '导师',
  'ADMIN': '管理员'
};

// 角色首页路由映射
const ROLE_HOME_MAP = {
  'STUDENT': '/pages/student/home/index',
  'TUTOR': '/pages/tutor/home/index',
  'ADMIN': '/pages/admin/home/index'
};

// ==================== 选题状态 ====================
const TOPIC_STATUS = {
  DRAFT: 0,       // 草稿
  PUBLISHED: 1,   // 已发布
  LOCKED: 2,      // 已锁定
  ARCHIVED: 3     // 已归档
};

const TOPIC_STATUS_TEXT = {
  0: '草稿',
  1: '已发布',
  2: '已锁定',
  3: '已归档'
};

const TOPIC_STATUS_COLOR = {
  0: '#999999',
  1: '#52c41a',
  2: '#fa8c16',
  3: '#d9d9d9'
};

// ==================== 申请状态 ====================
const APPLICATION_STATUS = {
  PENDING: 0,    // 待审批
  APPROVED: 1,   // 已通过
  REJECTED: 2,   // 已拒绝
  CANCELLED: 3   // 已取消
};

const APPLICATION_STATUS_TEXT = {
  0: '待审批',
  1: '已通过',
  2: '已拒绝',
  3: '已取消'
};

const APPLICATION_STATUS_COLOR = {
  0: '#1890ff',
  1: '#52c41a',
  2: '#f5222d',
  3: '#999999'
};

// ==================== 论文状态 ====================
const PAPER_STATUS = {
  EDITING: 0,     // 编辑中
  SUBMITTED: 1,   // 已提交
  REVIEWING: 2,   // 评审中
  REVISING: 3,    // 待修改
  APPROVED: 4,    // 已通过
  ARCHIVED: 5     // 已归档
};

const PAPER_STATUS_TEXT = {
  0: '编辑中',
  1: '已提交',
  2: '评审中',
  3: '待修改',
  4: '已通过',
  5: '已归档'
};

const PAPER_STATUS_COLOR = {
  0: '#999999',
  1: '#1890ff',
  2: '#fa8c16',
  3: '#f5222d',
  4: '#52c41a',
  5: '#d9d9d9'
};

// ==================== 用户状态 ====================
const USER_STATUS = {
  DISABLED: 0,  // 禁用
  ENABLED: 1    // 启用
};

const USER_STATUS_TEXT = {
  0: '禁用',
  1: '正常'
};

// ==================== 存储键名 ====================
const STORAGE_KEY = {
  TOKEN: 'token',              // JWT Token
  USER_INFO: 'userInfo',       // 用户信息
  USER_ROLE: 'userRole'        // 用户角色(主要角色)
};

// ==================== 文件上传配置 ====================
const UPLOAD_CONFIG = {
  MAX_SIZE: 50 * 1024 * 1024,  // 最大50MB
  ALLOWED_TYPES: ['.pdf', '.doc', '.docx', '.zip', '.rar'],
  ALLOWED_IMAGE_TYPES: ['.jpg', '.jpeg', '.png', '.gif']
};

// ==================== 导出 ====================
module.exports = {
  API_BASE_URL,
  ROLE,
  ROLE_TEXT,
  ROLE_HOME_MAP,
  TOPIC_STATUS,
  TOPIC_STATUS_TEXT,
  TOPIC_STATUS_COLOR,
  APPLICATION_STATUS,
  APPLICATION_STATUS_TEXT,
  APPLICATION_STATUS_COLOR,
  PAPER_STATUS,
  PAPER_STATUS_TEXT,
  PAPER_STATUS_COLOR,
  USER_STATUS,
  USER_STATUS_TEXT,
  STORAGE_KEY,
  UPLOAD_CONFIG
};
