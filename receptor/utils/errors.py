class ServiceError(Exception):
    """Базовая ошибка сервиса."""


class EntityNotFoundError(ServiceError):
    """Объект не найден."""


class ValidationError(ServiceError):
    """Некорректные данные."""


class ConflictError(ServiceError):
    """Конфликт данных."""


class DatabaseError(Exception):
    """Ошибка в базе данных"""


class AiResponseParseError(ValueError):
    """LLM вернул невалидный/неожиданный формат."""
