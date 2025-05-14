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

    def log(self, *args, **kwargs) -> str:
        """
        Logs the message with the given arguments.

        Args:
            *args: Positional arguments to format the message.
            **kwargs: Keyword arguments to format the message.

        Returns:
            str: The formatted log message.
        """
        message = self.format.format(*args, **kwargs)

        output = f"{self.level}: {message} ({self.code})"

        max_messages_reached: bool = kwargs.get("max_messages_reached", False)
        max_messages: int = kwargs.get("max_messages", 0)

        max_messages_previously_met_for_code = kwargs.get(
            "max_messages_previously_met_for_code", False
        )
        if max_messages_previously_met_for_code:
            output_to_print = ""
        else:
            if max_messages_reached:
                output_to_print = f"WARNING: Maximum number of messages ({max_messages}) reached for code {self.code}."
            else:
                output_to_print = output

        timestamp: str | None = kwargs.get("timestamp")
        if timestamp:
            output = f"{timestamp} - {output}"
            output_to_print = f"{timestamp} - {output_to_print}"

        if output_to_print != "":
            stdout = kwargs.get("stdout", True)
            if stdout:
                print(output_to_print)

            file_handle = kwargs.get("file_handle")
            if file_handle:
                file_handle.write(output_to_print + "\n")
                file_handle.flush()

        return output
