-- =============================================================
-- 毕业论文选题管理系统 数据库结构 (MySQL 8+)
-- 说明：
--  * 字符集统一使用 utf8mb4
--  * 存储引擎 InnoDB
--  * 时间精度到毫秒 DATETIME(3)
--  * 可根据需要决定是否保留真实外键约束；生产环境若考虑性能和分库，可去掉 FK 自行保证数据一致性
--  * 状态字段均使用 TINYINT + 注释说明
-- =============================================================

SET NAMES utf8mb4;
SET time_zone = '+08:00';

 --可选：创建数据库（如已有可跳过）
CREATE DATABASE IF NOT EXISTS thesis_mgmt DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE thesis_mgmt;

-- =====================
-- 1. 系部 department
-- =====================
DROP TABLE IF EXISTS department;
CREATE TABLE department (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  dept_code VARCHAR(32) NOT NULL UNIQUE COMMENT '系部编码',
  name VARCHAR(128) NOT NULL COMMENT '系部名称',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1=启用,0=停用',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系部';

-- =====================
-- 2. 专业 major
-- =====================
DROP TABLE IF EXISTS major;
CREATE TABLE major (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  department_id BIGINT UNSIGNED NOT NULL COMMENT '所属系部ID',
  major_code VARCHAR(32) NOT NULL UNIQUE COMMENT '专业编码',
  name VARCHAR(128) NOT NULL COMMENT '专业名称',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1=启用,0=停用',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  CONSTRAINT fk_major_department FOREIGN KEY (department_id) REFERENCES department(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业';

-- =====================
-- 3. 用户 user
-- =====================
DROP TABLE IF EXISTS user;
CREATE TABLE user (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  username VARCHAR(64) NOT NULL UNIQUE COMMENT '登录用户名',
  real_name VARCHAR(64) NOT NULL COMMENT '真实姓名',
  student_no VARCHAR(64) NULL COMMENT '学号(学生)',
  teacher_no VARCHAR(64) NULL COMMENT '工号(导师)',
  phone VARCHAR(32) NULL COMMENT '手机号',
  email VARCHAR(128) NULL COMMENT '邮箱',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
  password_salt VARCHAR(64) NOT NULL COMMENT '密码盐',
  department_id BIGINT UNSIGNED NULL COMMENT '所属系部（管理员可为空）',
  primary_major_id BIGINT UNSIGNED NULL COMMENT '主专业ID',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1=正常,0=锁定',
  last_login_at DATETIME(3) NULL COMMENT '最后登录时间',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  deleted_at DATETIME(3) NULL COMMENT '软删除时间',
  UNIQUE KEY uq_user_student_no (student_no),
  UNIQUE KEY uq_user_teacher_no (teacher_no),
  UNIQUE KEY uq_user_phone (phone),
  UNIQUE KEY uq_user_email (email),
  KEY idx_user_dept (department_id),
  KEY idx_user_major (primary_major_id),
  CONSTRAINT fk_user_dept FOREIGN KEY (department_id) REFERENCES department(id)
    ON UPDATE RESTRICT ON DELETE SET NULL,
  CONSTRAINT fk_user_primary_major FOREIGN KEY (primary_major_id) REFERENCES major(id)
    ON UPDATE RESTRICT ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户';

-- =====================
-- 4. 用户-专业 多对多 user_major
-- =====================
DROP TABLE IF EXISTS user_major;
CREATE TABLE user_major (
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  major_id BIGINT UNSIGNED NOT NULL COMMENT '专业ID',
  PRIMARY KEY (user_id, major_id),
  CONSTRAINT fk_um_user FOREIGN KEY (user_id) REFERENCES user(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_um_major FOREIGN KEY (major_id) REFERENCES major(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户与专业映射';

-- =====================
-- 5. 角色 role
-- =====================
DROP TABLE IF EXISTS role;
CREATE TABLE role (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  role_key VARCHAR(32) NOT NULL UNIQUE COMMENT '系统标识: ADMIN/TUTOR/STUDENT',
  name VARCHAR(64) NOT NULL COMMENT '角色名称',
  description VARCHAR(255) NULL COMMENT '描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色';

-- =====================
-- 6. 权限 permission
-- =====================
DROP TABLE IF EXISTS permission;
CREATE TABLE permission (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  perm_key VARCHAR(64) NOT NULL UNIQUE COMMENT '权限标识: topic.read 等',
  name VARCHAR(64) NOT NULL COMMENT '权限名称',
  category VARCHAR(32) NOT NULL COMMENT '分类: topic/paper/user',
  description VARCHAR(255) NULL COMMENT '描述'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限';

-- =====================
-- 7. 用户-角色 user_role
-- =====================
DROP TABLE IF EXISTS user_role;
CREATE TABLE user_role (
  user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  role_id BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
  PRIMARY KEY (user_id, role_id),
  CONSTRAINT fk_ur_user FOREIGN KEY (user_id) REFERENCES user(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ur_role FOREIGN KEY (role_id) REFERENCES role(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户-角色关联';

-- =====================
-- 8. 角色-权限 role_permission
-- =====================
DROP TABLE IF EXISTS role_permission;
CREATE TABLE role_permission (
  role_id BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
  permission_id BIGINT UNSIGNED NOT NULL COMMENT '权限ID',
  PRIMARY KEY (role_id, permission_id),
  CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES role(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_rp_perm FOREIGN KEY (permission_id) REFERENCES permission(id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色-权限关联';

-- =====================
-- 9. 选题 topic
-- =====================
DROP TABLE IF EXISTS topic;
CREATE TABLE topic (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  title VARCHAR(255) NOT NULL COMMENT '题目标题',
  description MEDIUMTEXT NULL COMMENT '题目描述',
  major_id BIGINT UNSIGNED NOT NULL COMMENT '所属专业',
  tutor_id BIGINT UNSIGNED NOT NULL COMMENT '导师用户ID',
  max_students INT NOT NULL DEFAULT 1 COMMENT '最大可选学生数',
  current_students INT NOT NULL DEFAULT 0 COMMENT '当前已确认学生数',
  status TINYINT NOT NULL DEFAULT 0 COMMENT '0=草稿,1=发布,2=锁定,3=归档',
  academic_year VARCHAR(16) NOT NULL COMMENT '学年: 2024-2025',
  term TINYINT NOT NULL DEFAULT 1 COMMENT '学期:1=上,2=下',
  published_at DATETIME(3) NULL COMMENT '发布时间',
  locked_at DATETIME(3) NULL COMMENT '锁定时间',
  archived_at DATETIME(3) NULL COMMENT '归档时间',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  KEY idx_topic_major_status (major_id, status),
  KEY idx_topic_tutor (tutor_id),
  KEY idx_topic_year_term (academic_year, term),
  CONSTRAINT fk_topic_major FOREIGN KEY (major_id) REFERENCES major(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_topic_tutor FOREIGN KEY (tutor_id) REFERENCES user(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选题';

-- =====================
-- 10. 选题申请 topic_application
-- =====================
DROP TABLE IF EXISTS topic_application;
CREATE TABLE topic_application (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  topic_id BIGINT UNSIGNED NOT NULL COMMENT '选题ID',
  student_id BIGINT UNSIGNED NOT NULL COMMENT '学生用户ID',
  status TINYINT NOT NULL DEFAULT 0 COMMENT '0=待审批,1=通过,2=拒绝,3=取消',
  application_reason TEXT NULL COMMENT '申请理由',
  decision_by BIGINT UNSIGNED NULL COMMENT '审批人(导师)',
  decision_at DATETIME(3) NULL COMMENT '审批时间',
  decision_comment TEXT NULL COMMENT '审批意见',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_app_topic_student (topic_id, student_id),
  KEY idx_app_topic_status (topic_id, status),
  KEY idx_app_student_status (student_id, status),
  CONSTRAINT fk_app_topic FOREIGN KEY (topic_id) REFERENCES topic(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_app_student FOREIGN KEY (student_id) REFERENCES user(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_app_decider FOREIGN KEY (decision_by) REFERENCES user(id)
    ON UPDATE RESTRICT ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选题申请';

-- =====================
-- 11. 论文 paper
-- =====================
DROP TABLE IF EXISTS paper;
CREATE TABLE paper (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  topic_id BIGINT UNSIGNED NOT NULL COMMENT '关联选题ID',
  student_id BIGINT UNSIGNED NOT NULL COMMENT '学生用户ID',
  title VARCHAR(255) NOT NULL COMMENT '论文标题',
  abstract TEXT NULL COMMENT '摘要',
  keywords VARCHAR(255) NULL COMMENT '关键词',
  status TINYINT NOT NULL DEFAULT 0 COMMENT '0=编辑中,1=已提交,2=评审中,3=待修改,4=通过,5=归档',
  academic_year VARCHAR(16) NOT NULL COMMENT '学年',
  term TINYINT NOT NULL DEFAULT 1 COMMENT '学期',
  submitted_at DATETIME(3) NULL COMMENT '首次提交时间',
  archived_at DATETIME(3) NULL COMMENT '归档时间',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  UNIQUE KEY uq_paper_student_term (student_id, academic_year, term),
  KEY idx_paper_topic (topic_id),
  KEY idx_paper_status (status),
  CONSTRAINT fk_paper_topic FOREIGN KEY (topic_id) REFERENCES topic(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_paper_student FOREIGN KEY (student_id) REFERENCES user(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文';

-- =====================
-- 12. 论文版本 paper_version
-- =====================
DROP TABLE IF EXISTS paper_version;
CREATE TABLE paper_version (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  paper_id BIGINT UNSIGNED NOT NULL COMMENT '论文ID',
  version_no INT NOT NULL COMMENT '版本序号(1开始递增)',
  content_text MEDIUMTEXT NULL COMMENT '正文内容(可选)',
  content_format TINYINT NOT NULL DEFAULT 0 COMMENT '0=无,1=markdown,2=html,3=text',
  is_final TINYINT NOT NULL DEFAULT 0 COMMENT '是否标记为最终版本',
  submitted_by BIGINT UNSIGNED NOT NULL COMMENT '提交人ID',
  submitted_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '提交时间',
  notes VARCHAR(255) NULL COMMENT '备注',
  UNIQUE KEY uq_paper_version_no (paper_id, version_no),
  KEY idx_version_paper (paper_id),
  CONSTRAINT fk_version_paper FOREIGN KEY (paper_id) REFERENCES paper(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_version_submitter FOREIGN KEY (submitted_by) REFERENCES user(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文版本';

-- =====================
-- 13. 版本附件 paper_attachment
-- =====================
DROP TABLE IF EXISTS paper_attachment;
CREATE TABLE paper_attachment (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  paper_version_id BIGINT UNSIGNED NOT NULL COMMENT '论文版本ID',
  file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
  mime_type VARCHAR(128) NOT NULL COMMENT 'MIME类型',
  file_size BIGINT UNSIGNED NOT NULL COMMENT '文件大小字节',
  storage_url VARCHAR(1024) NOT NULL COMMENT '存储地址/URL',
  file_hash VARCHAR(128) NULL COMMENT '文件哈希(SHA256)',
  uploaded_by BIGINT UNSIGNED NOT NULL COMMENT '上传人ID',
  uploaded_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '上传时间',
  KEY idx_att_version (paper_version_id),
  CONSTRAINT fk_att_version FOREIGN KEY (paper_version_id) REFERENCES paper_version(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_att_uploader FOREIGN KEY (uploaded_by) REFERENCES user(id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文版本附件';

-- =====================
-- 14. 操作日志 operation_log （可选）
-- =====================
DROP TABLE IF EXISTS operation_log;
CREATE TABLE operation_log (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  actor_id BIGINT UNSIGNED NULL COMMENT '操作人ID',
  action VARCHAR(64) NOT NULL COMMENT '动作标识',
  target_table VARCHAR(64) NULL COMMENT '目标表名',
  target_id BIGINT UNSIGNED NULL COMMENT '目标记录ID',
  detail JSON NULL COMMENT '详情(JSON)',
  ip VARCHAR(64) NULL COMMENT '来源IP',
  created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  KEY idx_log_actor (actor_id, created_at),
  KEY idx_log_created_at (created_at),
  KEY idx_log_user_id (actor_id),
  KEY idx_log_action (action),
  KEY idx_log_resource_type (target_table),
  CONSTRAINT fk_log_actor FOREIGN KEY (actor_id) REFERENCES user(id)
    ON UPDATE SET NULL ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志';

-- =====================
-- 15. 基础数据初始化（可根据需要调整）
-- =====================
INSERT INTO role (role_key, name, description) VALUES
 ('ADMIN','管理员','系统管理员'),
 ('TUTOR','导师','指导教师'),
 ('STUDENT','学生','学生用户');

-- 示例权限（可扩展）
INSERT INTO permission (perm_key, name, category, description) VALUES
 ('topic.create','创建选题','topic','导师创建选题'),
 ('topic.read','查看选题','topic','查询选题列表'),
 ('topic.apply','申请选题','topic','学生申请选题'),
 ('paper.submit','提交论文','paper','提交论文/版本'),
 ('paper.review','评审论文','paper','导师评审论文');

-- 角色权限映射（示例）
INSERT INTO role_permission (role_id, permission_id)
  SELECT r.id, p.id FROM role r JOIN permission p
   ON ( (r.role_key='TUTOR' AND p.perm_key IN ('topic.create','topic.read','paper.review'))
     OR (r.role_key='STUDENT' AND p.perm_key IN ('topic.read','topic.apply','paper.submit'))
     OR (r.role_key='ADMIN') );

-- 系部/专业示例
INSERT INTO department (dept_code, name) VALUES ('INFO','信息工程系');
INSERT INTO major (department_id, major_code, name) VALUES (1,'NET','计算机网络技术');

-- 管理员示例用户（密码需在应用层加密后再入库，这里仅演示）
INSERT INTO user (username, real_name, password_hash, password_salt, status)
VALUES ('admin','系统管理员','{PLEASE_REPLACE}','{SALT}',1);

INSERT INTO user_role (user_id, role_id)
  SELECT u.id, r.id FROM user u, role r WHERE u.username='admin' AND r.role_key='ADMIN';

-- 结束
