class FinanceError(Exception):
    """Base class for all custom finance exceptions."""
    pass


class ValidationError(FinanceError):
    """Used when user input is invalid."""
    pass


class NotFoundError(FinanceError):
    """Used when an object with a given ID is not found."""
    pass


class StorageError(FinanceError):
    """Used for file / CSV related errors."""
    pass
