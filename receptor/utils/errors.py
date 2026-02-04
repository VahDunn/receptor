class ServiceError(Exception):
    """Базовая ошибка сервиса."""


class EntityNotFoundError(ServiceError):
    """Объект не найден."""


class ValidationError(ServiceError):
    """Некорректные данные."""


class ConflictError(ServiceError):
    """Конфликт данных."""

class AiResponseParseError(ValueError):
    """LLM вернул невалидный/неожиданный формат."""
