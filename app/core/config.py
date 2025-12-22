import os

class Settings:
    PROJECT_NAME: str = "Цифровая платформа холдинга"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./digital_platform.db"
    
    # Security
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

