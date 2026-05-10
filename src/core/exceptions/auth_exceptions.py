from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self, detail: str = "Не удалось проверить данные авторизации.") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
