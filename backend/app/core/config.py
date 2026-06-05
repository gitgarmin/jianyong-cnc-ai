from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "简用 数控AI大师"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./jianyong_cnc.db"  # 开发期 SQLite，迁移条件见 PRD 7 章
    # DATABASE_URL: str = "mysql+pymysql://root:jianyong@localhost:3306/jianyong_cnc"  # 生产 MySQL

    # AI Provider
    AI_PROVIDER: str = "deepseek"  # deepseek | local | fallback
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_VISION_MODEL: str = "deepseek-vision"

    # 安全
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # 图纸上传
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./uploads"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
