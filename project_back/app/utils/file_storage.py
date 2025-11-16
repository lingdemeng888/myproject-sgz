"""
文件存储工具
实现文件上传、哈希计算、存储路径管理等功能
"""
import os
import hashlib
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
from typing import Dict, Tuple

from app.core.config import get_settings
from app.core.exceptions import BusinessException


class FileStorage:
    """文件存储管理类"""

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        验证文件是否符合要求
        
        验证项：
        1. 文件大小限制（max_upload_size）
        2. 文件扩展名限制（allowed_extensions）
        
        Args:
            file: 上传的文件对象
            
        Raises:
            BusinessException: 文件验证失败
        """
        settings = get_settings()
        
        # 验证文件名
        if not file.filename:
            raise BusinessException(
                message="文件名不能为空",
                code=400
            )
        
        # 验证文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        allowed_exts = [ext.strip() for ext in settings.allowed_extensions.split(',')]
        
        if file_ext not in allowed_exts:
            raise BusinessException(
                message=f"不支持的文件类型 {file_ext}，允许的类型：{', '.join(allowed_exts)}",
                code=400
            )
        
        # 验证文件大小（需要读取文件内容）
        # 注意：这里会读取整个文件到内存，对于大文件可能有性能问题
        # 生产环境建议使用流式读取或nginx限制
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到文件开头
        
        if file_size > settings.max_upload_size:
            max_mb = settings.max_upload_size / (1024 * 1024)
            raise BusinessException(
                message=f"文件大小超过限制（最大 {max_mb:.0f}MB）",
                code=400
            )
        
        if file_size == 0:
            raise BusinessException(
                message="文件不能为空",
                code=400
            )

    @staticmethod
    def get_file_hash(file: UploadFile) -> str:
        """
        计算文件的SHA256哈希值
        
        Args:
            file: 上传的文件对象
            
        Returns:
            文件的SHA256哈希值（小写十六进制字符串）
        """
        sha256_hash = hashlib.sha256()
        
        # 分块读取文件计算哈希（避免大文件占用内存）
        file.file.seek(0)
        for chunk in iter(lambda: file.file.read(8192), b""):
            sha256_hash.update(chunk)
        
        file.file.seek(0)  # 重置到文件开头
        
        return sha256_hash.hexdigest()

    @staticmethod
    def ensure_upload_dir(sub_path: str = "") -> Path:
        """
        确保上传目录存在，不存在则创建
        
        Args:
            sub_path: 子目录路径（如 "papers/2024/11"）
            
        Returns:
            完整的目录路径对象
        """
        settings = get_settings()
        
        # 构建完整路径
        if sub_path:
            full_path = Path(settings.upload_dir) / sub_path
        else:
            full_path = Path(settings.upload_dir)
        
        # 创建目录（递归创建，exist_ok=True表示已存在不报错）
        full_path.mkdir(parents=True, exist_ok=True)
        
        return full_path

    @staticmethod
    def save_attachment(file: UploadFile) -> Dict[str, any]:
        """
        保存附件文件到服务器
        
        存储策略：
        1. 目录结构：papers/年/月/
        2. 文件命名：SHA256哈希值 + 原始扩展名
        3. 返回相对路径（storage_url）和哈希值（file_hash）
        
        哈希去重：
        - 如果相同哈希的文件已存在，则复用该文件，不重复存储
        
        Args:
            file: 上传的文件对象
            
        Returns:
            包含文件信息的字典：
            {
                'file_name': '原始文件名.pdf',
                'storage_url': 'papers/2024/11/abc123...def.pdf',
                'file_hash': 'abc123...def',
                'file_size': 1234567,
                'mime_type': 'application/pdf'
            }
            
        Raises:
            BusinessException: 文件保存失败
        """
        # 步骤1：验证文件
        FileStorage.validate_file(file)
        
        # 步骤2：计算文件哈希
        file_hash = FileStorage.get_file_hash(file)
        
        # 步骤3：获取文件信息
        file_ext = Path(file.filename).suffix.lower()
        file_size = file.file.seek(0, 2)
        file.file.seek(0)
        
        # 步骤4：构建存储路径（按年/月分类）
        now = datetime.now()
        sub_path = f"papers/{now.year}/{now.month:02d}"
        upload_dir = FileStorage.ensure_upload_dir(sub_path)
        
        # 步骤5：构建文件名（哈希 + 扩展名）
        file_name_on_disk = f"{file_hash}{file_ext}"
        full_path = upload_dir / file_name_on_disk
        
        # 步骤6：构建相对路径（用于数据库存储）
        storage_url = f"{sub_path}/{file_name_on_disk}"
        
        # 步骤7：哈希去重 - 如果文件已存在，则不重复保存
        if full_path.exists():
            # 文件已存在，验证大小是否一致（简单校验）
            existing_size = full_path.stat().st_size
            if existing_size == file_size:
                # 复用现有文件
                return {
                    'file_name': file.filename,
                    'storage_url': storage_url,
                    'file_hash': file_hash,
                    'file_size': file_size,
                    'mime_type': file.content_type or 'application/octet-stream'
                }
            else:
                # 哈希冲突（极低概率），使用时间戳作为后缀
                timestamp = int(datetime.now().timestamp() * 1000)
                file_name_on_disk = f"{file_hash}_{timestamp}{file_ext}"
                full_path = upload_dir / file_name_on_disk
                storage_url = f"{sub_path}/{file_name_on_disk}"
        
        # 步骤8：保存文件到磁盘
        try:
            with open(full_path, "wb") as buffer:
                file.file.seek(0)
                buffer.write(file.file.read())
        except Exception as e:
            raise BusinessException(
                message=f"文件保存失败: {str(e)}",
                code=500
            )
        
        # 步骤9：返回文件信息
        return {
            'file_name': file.filename,
            'storage_url': storage_url,
            'file_hash': file_hash,
            'file_size': file_size,
            'mime_type': file.content_type or 'application/octet-stream'
        }

    @staticmethod
    def get_file_path(storage_url: str) -> Path:
        """
        根据存储URL获取文件的完整路径
        
        Args:
            storage_url: 存储URL（相对路径，如 "papers/2024/11/abc.pdf"）
            
        Returns:
            文件的完整路径对象
        """
        settings = get_settings()
        return Path(settings.upload_dir) / storage_url

    @staticmethod
    def delete_file(storage_url: str) -> bool:
        """
        删除文件（注意：哈希去重场景下，不应轻易删除物理文件）
        
        Args:
            storage_url: 存储URL（相对路径）
            
        Returns:
            是否删除成功
        """
        file_path = FileStorage.get_file_path(storage_url)
        
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        
        return False
