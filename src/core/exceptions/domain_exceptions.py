"""
Исключения для доменного слоя cодержащие в себе данные
"""


class BaseDomainException(Exception):
    """Базовое доменное исключение"""
    def __init__(self, detail: str) -> None:
        self._detail = detail
        super().__init__(detail)

    def get_detail(self) -> str:
        """Получить детальное описание ошибки для пользователя"""
        return self._detail


# Пользователи
class UserNotFoundByNicknameException(BaseDomainException):
    """Пользователь не найден - ОБОГАЩАЕМ данными"""
    _template = "Пользователь с никнеймом '{nickname}' не найден."

    def __init__(self, nickname: str) -> None:
        # Вставляем конкретный никнейм в сообщение
        detail = self._template.format(nickname=nickname)
        super().__init__(detail)


class UserNicknameIsNotUniqueException(BaseDomainException):
    """Никнейм уже занят"""
    _template = "Пользователь с никнеймом '{nickname}' уже существует."

    def __init__(self, nickname: str) -> None:
        detail = self._template.format(nickname=nickname)
        super().__init__(detail)


class UserEmailIsNotUniqueException(BaseDomainException):
    """Email уже используется"""
    _template = "Пользователь с email '{email}' уже существует."

    def __init__(self, email: str) -> None:
        detail = self._template.format(email=email)
        super().__init__(detail)


class WrongUserPasswordException(BaseDomainException):
    """Неверный пароль"""
    def __init__(self) -> None:
        super().__init__("Неверный пароль")


# Категории
class CategoryNotFoundBySlugException(BaseDomainException):
    """Категория не найдена"""
    _template = "Категория с slug '{slug}' не найдена."

    def __init__(self, slug: str) -> None:
        detail = self._template.format(slug=slug)
        super().__init__(detail)


class CategoryIsNotUniqueException(BaseDomainException):
    """Категория уже существует"""
    _template = "Категория с slug '{slug}' уже существует."

    def __init__(self, slug: str) -> None:
        detail = self._template.format(slug=slug)
        super().__init__(detail)


# Локации
class LocationNotFoundByNameException(BaseDomainException):
    """Локация не найдена"""
    _template = "Локация с названием '{name}' не найдена."

    def __init__(self, name: str) -> None:
        detail = self._template.format(name=name)
        super().__init__(detail)


class LocationIsNotUniqueException(BaseDomainException):
    """Локация уже существует"""
    _template = "Локация с названием '{name}' уже существует."

    def __init__(self, name: str) -> None:
        detail = self._template.format(name=name)
        super().__init__(detail)


# Посты
class PostNotFoundByIDException(BaseDomainException):
    """Пост не найден"""
    _template = "Пост с ID '{id}' не найден."

    def __init__(self, post_id: int) -> None:
        detail = self._template.format(id=post_id)
        super().__init__(detail)


class PostDontCreateException(BaseDomainException):
    """Пост нельзя создать"""
    _template = "Пост не может быть создан: {cause}"

    def __init__(self, cause: str) -> None:
        detail = self._template.format(cause=cause)
        super().__init__(detail)


class PostDontChangeException(BaseDomainException):
    """Пост нельзя изменить"""
    _template = "Пост не может быть изменен: {cause}"

    def __init__(self, cause: str) -> None:
        detail = self._template.format(cause=cause)
        super().__init__(detail)


class PostDontDestroyException(BaseDomainException):
    """Пост нельзя удалить"""
    _template = "Пост не может быть удален: {cause}"

    def __init__(self, cause: str) -> None:
        detail = self._template.format(cause=cause)
        super().__init__(detail)


# Комментарии
class CommentNotFoundByIDException(BaseDomainException):
    """Комментарий не найден"""
    _template = "Комментарий с ID '{id}' не найден."

    def __init__(self, comment_id: int) -> None:
        detail = self._template.format(id=comment_id)
        super().__init__(detail)


class CommentDontCreateException(BaseDomainException):
    """Комментарий нельзя создать"""
    _template = "Комментарий не может быть создан: {cause}"

    def __init__(self, cause: str) -> None:
        detail = self._template.format(cause=cause)
        super().__init__(detail)


class CommentDontChangeException(BaseDomainException):
    """Комментарий нельзя изменить"""
    _template = "Комментарий не может быть изменен: {cause}"

    def __init__(self, cause: str) -> None:
        detail = self._template.format(cause=cause)
        super().__init__(detail)


class CommentDontDestroyException(BaseDomainException):
    """Комментарий нельзя удалить"""
    _template = "Комментарий не может быть удален: {cause}"

    def __init__(self, cause: str) -> None:
        detail = self._template.format(cause=cause)
        super().__init__(detail)
