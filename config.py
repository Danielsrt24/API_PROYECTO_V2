from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Sistema INDA API"
    DATABASE_URL: str = "mysql+pymysql://root:@localhost/inda_db"
    SECRET_KEY: str = "Cocolito"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    class Config:
        env_file = ".env"

settings = Settings()