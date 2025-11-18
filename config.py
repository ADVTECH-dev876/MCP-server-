import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Storage
    upload_dir: Path = Path("uploads")
    max_file_size: int = 10 * 1024 * 1024 * 1024  # 10 GB
    chunk_size: int = 10 * 1024 * 1024  # 10 MB chunks
    
    # File type restrictions
    allowed_extensions: dict = {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
        "videos": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
        "code": [".html", ".css", ".js", ".ts", ".jsx", ".tsx", ".py", ".json", ".xml", ".yaml", ".yml"],
        "documents": [".pdf", ".txt", ".md", ".doc", ".docx"],
        "binaries": [".zip", ".tar", ".gz", ".exe", ".dll", ".so"],
        "databases": [".sqlite", ".db", ".mdb", ".accdb", ".sql"]
    }
    
    max_sizes: dict = {
        "images": 500 * 1024 * 1024,    # 500 MB
        "videos": 2 * 1024 * 1024 * 1024,  # 2 GB
        "code": 100 * 1024 * 1024,      # 100 MB
        "documents": 100 * 1024 * 1024, # 100 MB
        "binaries": 5 * 1024 * 1024 * 1024, # 5 GB
        "databases": 10 * 1024 * 1024 * 1024 # 10 GB
    }
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./mcp_web_host.db")
    
    class Config:
        env_file = ".env"

settings = Settings()
