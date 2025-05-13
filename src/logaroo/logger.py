from logaroo.exceptions import LogarooMissingCodeException
from src.logaroo.message import Message

ORDERED_LEVELS = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


class Logger:
    """
    A class to represent a logger.

    Attributes:
        name (str): The name of the logger.
        level (str): The log level (e.g., INFO, WARNING, ERROR).
        verbosity (int): The verbosity level of the logger.
        messages (list): A list of log messages associated with the logger.
    """

    def __init__(
        self,
        name: str,
        messages: list[Message] = [],
        level: str = "INFO",
        verbosity: int = 0,
        filename: str | None = None,
    ) -> None:
        """
        Initializes the Logger instance.

        Args:
            name (str): The name of the logger.
            level (str): The log level (e.g., INFO, WARNING, ERROR). Defaults to "INFO".
            verbosity (int, optional): The verbosity level of the logger. Defaults to 0.
        """
        self.name = name
        self.messages = messages
        self.level = level
        self.verbosity = verbosity
        self.filename = filename

        if self.filename:
            self.file_handle = open(self.filename, "w")
        else:
            self.file_handle = None

        # loggers[name] = self

    def _get_message(self, code: str) -> Message | None:
        """
        Retrieves a message by its code, level, and verbosity.
        If level is above the logger's level, the message is not logged.
        If verbosity is above the logger's verbosity, the message is not logged.

        Args:
            code (str): The code associated with the log message.

        Returns:
            Message | None: The corresponding Message object or None if not found.
        """

        if code not in [message.code for message in self.messages]:
            raise LogarooMissingCodeException(code)

        for message in self.messages:
            if message.code == code:
                if ORDERED_LEVELS.index(message.level) >= ORDERED_LEVELS.index(
                    self.level
                ):
                    if message.verbosity <= self.verbosity:
                        return message
        return

    def log(self, code: str, *args, **kwargs) -> None:
        """
        Logs a message with the given code and arguments.


        Args:
            code (str): The code associated with the log message.
            *args: Positional arguments to format the message.
            **kwargs: Keyword arguments to format the message.
        """
        message = self._get_message(code)

        if self.file_handle:
            kwargs["file_handle"] = self.file_handle

        if message:
            message.log(*args, **kwargs)

    def add_message(
        self,
        code: str,
        description: str,
        level: str,
        verbosity: int = 0,
        format: str = "{}",
    ) -> None:
        """
        Adds a new message to the logger.

        Args:
            message (Message): The Message object to add.
        """
        self.messages.append(Message(format, code, description, level, verbosity))

    def __del__(self):
        """
        Cleans up the logger instance.
        Closes the file handle if it was opened.
        """
        if self.file_handle:
            self.file_handle.close()


# loggers: dict[str, Logger] = {}
