
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = Field(default="Thesis Management API")
    env: str = Field(default="dev")
    debug: bool = Field(default=True)

    database_url: str = Field(alias="DATABASE_URL")

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60*24, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    cors_allow_origins: str = Field(default="*", alias="CORS_ALLOW_ORIGINS")

    # 文件上传配置
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")
    max_upload_size: int = Field(default=1073741824, alias="MAX_UPLOAD_SIZE")  # 1GB
    allowed_extensions: str = Field(default=".pdf,.doc,.docx,.zip,.rar", alias="ALLOWED_EXTENSIONS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
