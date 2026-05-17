import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def configure_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)

    get_logger(__name__).info("Logging configured, file=%s", settings.LOG_FILE)


class UserActionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()
        user = self._extract_user_from_token(request)
        response = await call_next(request)
        latency_ms = (time.perf_counter() - started_at) * 1000

        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        get_logger("user_actions").log(
            log_level,
            "user=%s ip=%s method=%s path=%s status=%s latency_ms=%.2f",
            user,
            request.client.host if request.client else "unknown",
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
        )
        return response

    @staticmethod
    def _extract_user_from_token(request: Request) -> str:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return "anonymous"

        token = authorization.split(" ", maxsplit=1)[1]
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_AUTH_KEY.get_secret_value(),
                algorithms=[settings.AUTH_ALGORITHM],
            )
            return payload.get("sub", "anonymous")
        except JWTError:
            return "anonymous"
