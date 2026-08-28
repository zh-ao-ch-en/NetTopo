"""全局配置。数据源、JWT、跨域等均通过环境变量 / .env 覆盖。"""
import os

from dotenv import load_dotenv

load_dotenv()

# 数据库连接串。默认 SQLite 本地演示零依赖；换 MySQL 时改为：
#   mysql+pymysql://user:password@host:3306/dbname （并在 requirements.txt 加 pymysql）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lab.db")

# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", "lab-dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 小时

# 允许跨域的前端来源（逗号分隔）。开发时 Vite 默认 5173。
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]