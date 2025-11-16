# Alembic 数据库迁移工具

此目录包含数据库迁移脚本，由 Alembic 管理。

## 常用命令

```powershell
# 生成新的迁移脚本（自动检测模型变化）
alembic revision --autogenerate -m "描述信息"

# 升级到最新版本
alembic upgrade head

# 回滚一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history --verbose
```

## 目录结构

```
alembic/
├── versions/        # 迁移脚本存放目录
├── env.py          # 环境配置
└── script.py.mako  # 迁移脚本模板
```

## 注意事项

1. 每次修改模型后，需执行 `alembic revision --autogenerate` 生成迁移脚本
2. 生成的迁移脚本需要人工检查确认后再执行
3. 生产环境执行迁移前务必备份数据库
4. 不要手动修改已应用的迁移脚本
