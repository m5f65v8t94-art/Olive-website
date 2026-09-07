from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Olive — Youth Mental-Wellbeing Support"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./wellbeing_app.db"
    AI_PROVIDER: str = "local_engine"  # options: 'local_engine', 'ollama', 'custom_llm'
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"
    MAX_HISTORY_MESSAGES_CONTEXT: int = 10
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
