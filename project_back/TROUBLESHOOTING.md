# 常见问题解决方案

## 依赖安装问题

### 问题1: pydantic-core 需要 Rust 编译环境

**错误信息**: `Cargo, the Rust package manager, is not installed`

**解决方案**: 
已更新 `requirements.txt` 使用最新版本（提供预编译wheel包），重新安装即可：

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 问题2: Python 环境未找到

**错误信息**: `无法将"python"项识别为 cmdlet`

**解决方案**:
使用完整路径创建虚拟环境：

```powershell
# 使用项目配置的Python路径
C:/Users/徐恩睿/AppData/Local/Programs/Python/Python314/python.exe -m venv .venv
```

### 问题3: 虚拟环境激活失败

**解决方案**:
直接使用虚拟环境中的Python执行命令，无需激活：

```powershell
# 安装依赖
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 运行服务
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

或使用提供的启动脚本：
```powershell
.\start_dev.ps1
```

## 数据库连接问题

### 问题: 无法连接到MySQL数据库

**解决方案**:

1. 确认MySQL服务已启动
2. 检查 `.env` 文件中的 `DATABASE_URL` 配置
3. 确认数据库 `thesis_mgmt` 已创建

```sql
CREATE DATABASE IF NOT EXISTS thesis_mgmt DEFAULT CHARACTER SET utf8mb4;
```

## Alembic 迁移问题

### 问题: 执行迁移时报错

**解决方案**:

1. 确认 `.env` 文件中的数据库配置正确
2. 确认数据库已创建
3. 检查模型导入是否正确

```powershell
# 查看当前迁移版本
.venv\Scripts\python.exe -m alembic current

# 升级到最新版本
.venv\Scripts\python.exe -m alembic upgrade head
```

## 网络问题

### 问题: pip 下载超时

**解决方案**:
使用国内镜像源：

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 开发建议

1. **首次运行前**
   - 复制 `.env.example` 到 `.env`
   - 修改数据库连接配置
   - 确保MySQL服务运行中

2. **依赖更新后**
   - 重新安装依赖：`.venv\Scripts\python.exe -m pip install -r requirements.txt`
   - 清理缓存：`.venv\Scripts\python.exe -m pip cache purge`

3. **遇到问题时**
   - 检查终端输出的错误信息
   - 查看日志文件
   - 使用 `--reload` 参数自动重载代码
