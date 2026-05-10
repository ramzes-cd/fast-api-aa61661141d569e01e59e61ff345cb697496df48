"""
Исключения на уровне инфраструктуры
"""


class BaseDatabaseException(Exception):
    """Базовое исключение"""
    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail
        super().__init__(detail)


class UserByNicknameAlreadyExistsException(BaseDatabaseException):
    """Пользователь с таким ником уже создан"""
    pass


class UserByEmailAlreadyExistsException(BaseDatabaseException):
    """Пользователь с таким email уже существует"""
    pass


class UserNotFoundException(BaseDatabaseException):
    """Пользователь не найден"""
    pass


# Ошибки категорий
class CategoryNotFoundException(BaseDatabaseException):
    """Категория не найдена"""
    pass


class CategoryAlreadyExistsException(BaseDatabaseException):
    """Категория с таким slug уже существует"""
    pass


# Ошибки локаций
class LocationNotFoundException(BaseDatabaseException):
    """Локация не найдена"""
    pass


class LocationAlreadyExistsException(BaseDatabaseException):
    """Локация с таким именем уже существует"""
    pass


# Ошибки постов
class PostNotFoundException(BaseDatabaseException):
    """Пост не найден"""
    pass


# Ошибки комментариев
class CommentNotFoundException(BaseDatabaseException):
    """Комментарий не найден"""
    pass


class CredentialException(BaseDatabaseException):
    """Ошибка прав доступа (не тот пользователь пытается изменить)"""
    pass
