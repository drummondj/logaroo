from abc import ABC
from io import StringIO


class Message(ABC):
    """
    A class to represent a log message.

    Attributes:
        format (str): The log message format.
        code (str): The code associated with the log message.
        description (str): A description of the log message.
        level (str): The log level (e.g., INFO, WARNING, ERROR).
        verbosity (int): The verbosity level of the log message.
    """

    def __init__(
        self,
        format: str,
        code: str,
        description: str,
        level: str,
        verbosity: int = 0,
    ) -> None:
        """
        Initializes the Message instance.

        Args:
            format (str): The log message format.
            code (str): The code associated with the log message.
            description (str): A description of the log message.
            level (str): The log level (e.g., INFO, WARNING, ERROR).
            verbosity (int, optional): The verbosity level of the log message. Defaults to 0.
        """
        self.format = format
        self.code = code
        self.description = description
        self.level = level
        self.verbosity = verbosity

    def log(self, *args, **kwargs) -> None:
        """
        Logs the message with the given arguments.

        Args:
            *args: Positional arguments to format the message.
            **kwargs: Keyword arguments to format the message.
        """
        message = self.format.format(*args, **kwargs)
        output = f"{self.level}: {message} ({self.code})"
        print(output)

        file_handle = kwargs.get("file_handle")
        if file_handle:
            file_handle.write(output + "\n")
            file_handle.flush()
