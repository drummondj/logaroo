from io import StringIO
from typing import Any
from logaroo.level import Level


class Message:
    """
    A class to represent a log message.

    Attributes:
        format (str): The log message format.
        code (str): The code associated with the log message.
        description (str): A description of the log message.
        level (Level): The log level (e.g., INFO, WARNING, ERROR).
        verbosity (int): The verbosity level of the log message.
    """

    def __init__(
        self,
        format: str,
        code: str,
        description: str,
        level: Level,
        verbosity: int = 0,
    ) -> None:
        """
        Initializes the Message instance.

        Args:
            format (str): The log message format.
            code (str): The code associated with the log message.
            description (str): A description of the log message.
            level (Level): The log level (e.g., INFO, WARNING, ERROR).
            verbosity (int, optional): The verbosity level of the log message. Defaults to 0.
        """
        self.format = format
        self.code = code
        self.description = description
        self.level = level
        self.verbosity = verbosity

    def log(self, *args, **kwargs) -> str:  # type: ignore
        """
        Logs the message with the given arguments.

        Args:
            *args: Positional arguments to format the message.
            **kwargs: Keyword arguments to format the message.

        Returns:
            str: The formatted log message.
        """
        message = self.format.format(*args, **kwargs)  # type: ignore

        output = f"{self.level}: {message} ({self.code})"

        max_messages_reached = bool(kwargs.get("max_messages_reached", False))  # type: ignore
        max_messages: int = int(kwargs.get("max_messages", 0))  # type: ignore

        max_messages_previously_met_for_code: bool = bool(
            kwargs.get("max_messages_previously_met_for_code", False)  # type: ignore
        )

        if max_messages_previously_met_for_code:
            output_to_print = ""
        else:
            if max_messages_reached:
                output_to_print = f"WARNING: Maximum number of messages ({max_messages}) reached for code {self.code}."
            else:
                output_to_print = output

        timestamp: str | None = kwargs.get("timestamp")  # type: ignore

        if timestamp:
            output = f"{timestamp} - {output}"
            output_to_print = f"{timestamp} - {output_to_print}"

        if output_to_print != "":
            stdout: bool = bool(kwargs.get("stdout", True))  # type: ignore
            if stdout:
                print(output_to_print)

            file_handle: StringIO = kwargs.get("file_handle")  # type: ignore
            if file_handle:
                file_handle.write(output_to_print + "\n")
                file_handle.flush()

        return output

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the Message instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Message instance.
        """
        return {
            "format": self.format,
            "code": self.code,
            "description": self.description,
            "level": self.level.name,
            "verbosity": self.verbosity,
        }
