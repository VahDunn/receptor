class ServiceError(Exception):
    """Базовая ошибка сервиса."""


class EntityNotFoundError(ServiceError):
    """Объект не найден."""


class ValidationError(ServiceError):
    """Некорректные данные."""


class ConflictError(ServiceError):
    """Конфликт данных."""


class DatabaseError(ServiceError):
    """Ошибка базы данных."""


class InsufficientFundsError(ServiceError):
    """Недостаточно средств."""


class AiResponseParseError(ServiceError):
    """LLM вернул невалидный/неожиданный формат."""