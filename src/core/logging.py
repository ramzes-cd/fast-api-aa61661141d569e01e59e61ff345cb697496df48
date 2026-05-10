import logging
import time

from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


class UserActionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started_at = time.perf_counter()
        user = self._extract_user_from_token(request)
        response = await call_next(request)
        latency_ms = (time.perf_counter() - started_at) * 1000

        logging.getLogger("user_actions").info(
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
