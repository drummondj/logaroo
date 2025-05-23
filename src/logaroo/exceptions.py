class LogarooException(Exception):
    """Base class for all Logaroo exceptions."""

    pass


class LogarooMissingCodeException(LogarooException):
    """Exception raised when a code is missing."""

    def __init__(self, code: str) -> None:
        self.code = code
        self.message = f"logging code '{self.code}' is missing."
        super().__init__(self.message)


class LogarooDuplicateCodeException(LogarooException):
    """Exception raised when a duplicate code is found."""

    def __init__(self, code: str) -> None:
        self.code = code
        self.message = f"logging code '{self.code}' is duplicated."
        super().__init__(self.message)
