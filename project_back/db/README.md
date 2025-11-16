# 毕业论文选题管理系统 数据库说明

> 对应结构定义文件：`schema.sql`
> 数据库建议名：`thesis_mgmt`

## 目录
- [总体概述](#总体概述)
- [命名规范](#命名规范)
- [核心实体与关系概览](#核心实体与关系概览)
- [表说明](#表说明)
- [状态码约定](#状态码约定)
- [索引策略摘要](#索引策略摘要)
- [并发与一致性策略](#并发与一致性策略)
- [初始化与迁移建议](#初始化与迁移建议)
- [未来扩展建议](#未来扩展建议)

## 总体概述
系统支持院系(系部)→专业→选题→申请→论文→版本/附件 的全流程管理，采用 RBAC（角色-权限）实现访问控制，并为后续审计（operation_log）预留结构。

## 命名规范
| 类型 | 规范 |
|------|------|
| 表名 | 下划线小写，如 `topic_application` |
| 主键 | `id` (BIGINT UNSIGNED AUTO_INCREMENT) |
| 外键 | `{refer}_id` 如 `major_id` |
| 时间 | `*_at` DATETIME(3) 毫秒精度 |
| 状态字段 | TINYINT + 注释说明 |
| 软删除 | `deleted_at` 为 NULL 表示未删除 |

字符集统一 `utf8mb4`，存储引擎使用 InnoDB。

## 核心实体与关系概览
逻辑分层：
1. 组织结构：`department` → `major`
2. 用户与权限：`user` + `role` + `permission` + 中间表
3. 选题生命周期：`topic` → `topic_application`
4. 论文生命周期：`paper` → `paper_version` → `paper_attachment`
5. 审计：`operation_log`

ER 参考（详见 `erdiagram.md` 或 Mermaid 图）：
- 一个系部(department)有多个专业(major)
- 用户可绑定主专业，也可通过 `user_major` 绑定多个专业
- 多角色多权限：`user_role`、`role_permission`
- 选题与专业、导师绑定；学生通过申请进入选题；批准后产生论文
- 论文拥有多个版本与附件

## 表说明
### 1. department (系部)
存放系部基础信息，用于专业与用户的上层分类。

### 2. major (专业)
专业从属于系部；与选题、用户（学生/导师）关联。

### 3. user (用户)
统一用户表，包含学生、导师、管理员。通过 `user_role` 区分角色。可支持多专业（辅以 `user_major`）。

### 4. user_major (用户-专业映射)
允许导师跨专业指导、记录学生转专业历史。

### 5. role / 6. permission
RBAC 基础表。`permission.perm_key` 建议使用资源.动作 命名，如 `topic.create`。

### 7. user_role / 8. role_permission
多对多关联表，实现灵活授权；可在业务变更时增删菜单与权限。

### 9. topic (选题)
导师发布（草稿→发布），学生申请，通过后依据并发控制更新锁定。`max_students` 与 `current_students` 支持人数限制。达到上限时可切换为锁定状态。

### 10. topic_application (选题申请)
学生申请记录，保证 (topic_id, student_id) 唯一。审批通过时需事务检查人数限制。

### 11. paper (论文)
与选题、学生关联。可限制同一学生在一个学年/学期仅一篇（唯一索引实现）。

### 12. paper_version (论文版本)
记录版本序列及最终版本标记；正文可选存储（大文本可考虑迁移 OSS）。

### 13. paper_attachment (论文版本附件)
关联具体版本的 PDF/DOC 等文件元数据，存储真实路径/URL。

### 14. operation_log (操作日志)
可记录关键操作（审批、状态变更、删除等），便于审计与追踪。

## 状态码约定
| 表 | 字段 | 取值 | 含义 |
|----|------|------|------|
| topic | status | 0 | 草稿 |
|      |        | 1 | 已发布 |
|      |        | 2 | 已锁定（满员或关闭） |
|      |        | 3 | 已归档 |
| topic_application | status | 0 | 待审批 |
|                   |        | 1 | 通过 |
|                   |        | 2 | 拒绝 |
|                   |        | 3 | 取消（学生撤销） |
| paper | status | 0 | 编辑中 |
|       |        | 1 | 已提交 |
|       |        | 2 | 评审中（可选） |
|       |        | 3 | 待修改 |
|       |        | 4 | 通过 |
|       |        | 5 | 归档 |
| paper_version | content_format | 0 | 无/默认 |
|               |                | 1 | markdown |
|               |                | 2 | html |
|               |                | 3 | plain text |
| paper_version | is_final | 0 | 否 |
|               |         | 1 | 是 |
| user | status | 1 | 正常 |
|      |        | 0 | 锁定 |
| major/department | status | 1 | 启用 |
|                  |        | 0 | 停用 |

## 索引策略摘要
| 表 | 索引 | 用途 |
|----|------|------|
| user | uq_user_* | 登录/查询唯一性保证 |
| topic | idx_topic_major_status | 按专业/状态列出选题 |
| topic | idx_topic_year_term | 学年学期筛选 |
| topic_application | uq_app_topic_student | 防重复申请 |
| topic_application | idx_app_topic_status | 导师审批队列 |
| paper | uq_paper_student_term | 学生学期唯一论文约束 |
| paper_version | uq_paper_version_no | 控制版本序号唯一 |
| paper_attachment | idx_att_version | 取版本附件 |
| operation_log | idx_log_actor | 操作人追踪 |

## 并发与一致性策略
1. 选题申请审批：
   - 在批准时事务中执行：
     - `SELECT ... FROM topic WHERE id=? FOR UPDATE` 锁行
     - 统计已通过人数 `SELECT COUNT(*) FROM topic_application WHERE topic_id=? AND status=1`
     - 若 < max_students → 更新申请状态为通过并递增 `current_students`
     - 若 == max_students 则将 topic.status=2(锁定)
2. 版本号维护：
   - 查询当前最大 version_no，再 +1 插入；可加行级锁或采用数据库唯一约束冲突重试。
3. 软删除：
   - 对关键数据使用 deleted_at（目前示例仅 user 提供），避免误删。

## 初始化与迁移建议
1. 创建数据库并导入 `schema.sql`。
2. 替换管理员初始密码哈希及盐。
3. 根据业务补充权限集合与角色权限映射。
4. 使用迁移工具（推荐）：
   - Python/Flask: Alembic
   - 版本号统一：`V{时间戳}__{描述}.sql`
5. 数据变更流程：
   - 先修改本地 -> 评审 -> 生成迁移脚本 -> 测试环境验证 -> 生产执行。

## 未来扩展建议
| 方向 | 描述 |
|------|------|
| 评审流程 | 新增 `paper_review` 存多轮评审意见与评分 |
| 公共选题 | 在 `topic` 增加 scope 字段（MAJOR / DEPT / GLOBAL） |
| 通知提醒 | 增加 `notification` 表 + WebSocket/消息推送 |
| 数据权限 | 增加数据范围表（role_data_scope） 实现跨学院权限 |
| 审计增强 | 引入变更快照（history_* 表）保存旧值 |
| 搜索优化 | ElasticSearch / OpenSearch 建立全文索引（标题/摘要） |

## 附：快速执行示例
```sql
-- (如需) 创建数据库
CREATE DATABASE IF NOT EXISTS thesis_mgmt DEFAULT CHARACTER SET utf8mb4;
USE thesis_mgmt;
-- 导入 schema.sql 内容
SOURCE /path/to/schema.sql;
```

## 版本
- 初始版本：v1.0  (与 schema.sql 同步)

---
如果后续需要生成 SQLAlchemy 模型或迁移脚手架，可在此 README 继续追加对应章节。
