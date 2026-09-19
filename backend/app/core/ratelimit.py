"""双层登录限流：账号为主、IP 为辅，计数持久化到数据库（跨进程/多实例共享）。

- 账号层：保护目标账号本身，防「换 IP 绕过」的爆破；admin 采用更严格阈值与更长锁定。
- IP 层：拦截来自单一来源的暴力扫描。
- 计数存库而非进程内存：gunicorn 多 worker / 多实例部署时计数共享、不失效。
  该表读多写少且量小，SQLite 单 worker 或换 MySQL 后多 worker 均适用。

为避免「恶意锁定 DoS」，锁定时间封顶，且登录成功即清除计数。
"""
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LoginAttempt


class LoginRateLimiter:
    def __init__(
        self,
        *,
        ip_max_fails: int = 5,
        user_max_fails: int = 5,
        admin_max_fails: int = 3,
        lock_seconds: int = 15 * 60,
        admin_lock_seconds: int = 30 * 60,
        window_seconds: int = 3600,
    ):
        self.ip_max_fails = ip_max_fails
        self.user_max_fails = user_max_fails
        self.admin_max_fails = admin_max_fails
        self.lock_seconds = lock_seconds
        self.admin_lock_seconds = admin_lock_seconds
        self.window_seconds = window_seconds

    def _params_for(self, key_type: str, key_value: str):
        """按维度返回 (阈值, 锁定秒数)。admin 账号单独走严格策略。"""
        if key_type == "user" and key_value == "admin":
            return self.admin_max_fails, self.admin_lock_seconds
        if key_type == "user":
            return self.user_max_fails, self.lock_seconds
        return self.ip_max_fails, self.lock_seconds

    def remaining_lock(self, db: Session, key_type: str, key_value: str) -> int:
        """若当前处于锁定期，返回剩余秒数；否则返回 0（并清理已过期锁定）。"""
        row = self._get(db, key_type, key_value)
        now = time.time()
        if row and row.locked_until:
            left = int(row.locked_until - now)
            if left > 0:
                return left + 1
            row.locked_until = None
            db.commit()
        return 0

    def record_failure(self, db: Session, key_type: str, key_value: str) -> None:
        max_fails, lock_seconds = self._params_for(key_type, key_value)
        now = int(time.time())
        row = self._get(db, key_type, key_value)
        if not row:
            row = LoginAttempt(
                key_type=key_type, key_value=key_value, fail_count=0,
                last_fail_at=now, locked_until=None,
            )
            db.add(row)
            db.flush()
        if now - row.last_fail_at > self.window_seconds:
            row.fail_count = 0
        row.fail_count += 1
        row.last_fail_at = now
        if row.fail_count >= max_fails:
            row.locked_until = now + lock_seconds
            row.fail_count = 0  # 解封后从新窗口重新计数
        db.commit()

    def reset(self, db: Session, key_type: str, key_value: str) -> None:
        row = self._get(db, key_type, key_value)
        if row:
            db.delete(row)
            db.commit()

    def _get(self, db: Session, key_type: str, key_value: str):
        return db.execute(
            select(LoginAttempt).where(
                LoginAttempt.key_type == key_type,
                LoginAttempt.key_value == key_value,
            )
        ).scalar_one_or_none()


def client_ip(request) -> str:
    """取真实客户端 IP。当前直接用 TCP 对端地址（不可被伪造）；
    若经受控反代且想取背后来访 IP，可改为解析 X-Forwarded-For。"""
    if request.client:
        return request.client.host
    return "unknown"