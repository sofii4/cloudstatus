from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Banco
    database_url: str
    
    # Redis
    redis_url: str
    
    # Segurança
    secret_key: str
    admin_username: str
    admin_password: str
    
    # Polling
    poll_interval: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()