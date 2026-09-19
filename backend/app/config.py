"""全局配置。数据源、JWT、跨域等均通过环境变量 / .env 覆盖。"""
import os
import pathlib

from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).resolve().parent.parent / ".env")

# 数据库连接串。默认 SQLite 本地演示零依赖；换 MySQL 时改为：
#   mysql+pymysql://user:password@host:3306/dbname （并在 requirements.txt 加 pymysql）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lab.db")
# SQLite 相对路径基于 backend 目录解析为绝对路径，避免随启动位置（systemd/Docker 的 WorkingDirectory）漂移导致数据"丢失"。
if DATABASE_URL.startswith("sqlite:///"):
    p = pathlib.Path(DATABASE_URL[len("sqlite:///") :])
    if not p.is_absolute():
        DATABASE_URL = f"sqlite:///{(pathlib.Path(__file__).resolve().parent.parent / p).resolve().as_posix()}"

# JWT 配置。密钥必须由 .env 显式提供：未配置即启动失败，杜绝公开弱默认值兜底。
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable not set")
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

# 登录限流：账号为主、IP 为辅的双层防护，计数存于数据库（跨进程共享）。
# IP 层：拦截单来源暴力扫描；账号层：保护目标账号、防换 IP 爆破；admin 走更严格策略。
LOGIN_IP_MAX_FAILS = int(os.getenv("LOGIN_IP_MAX_FAILS", "5"))
LOGIN_USER_MAX_FAILS = int(os.getenv("LOGIN_USER_MAX_FAILS", "5"))
LOGIN_ADMIN_MAX_FAILS = int(os.getenv("LOGIN_ADMIN_MAX_FAILS", "3"))
LOGIN_LOCK_MINUTES = int(os.getenv("LOGIN_LOCK_MINUTES", "15"))
LOGIN_ADMIN_LOCK_MINUTES = int(os.getenv("LOGIN_ADMIN_LOCK_MINUTES", "30"))