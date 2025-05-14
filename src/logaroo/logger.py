from datetime import datetime
from logaroo import LogarooMissingCodeException, Level, Message
from logaroo.exceptions import LogarooDuplicateCodeException

ORDERED_LEVELS = [
    Level.DEBUG,
    Level.INFO,
    Level.WARNING,
    Level.ERROR,
    Level.CRITICAL,
]


class Logger:
    """
    A class to represent a logger.

    Attributes:
        name (str): The name of the logger.
        messages (list): A list of log messages associated with the logger.
        level (Level): The log level (e.g., INFO, WARNING, ERROR). Defaults to "INFO".
        verbosity (int): The verbosity level of the logger. Defaults to 0.
        filename (str | None): The name of the file to log messages to. Defaults to None.
        stdout (bool): Whether to log to stdout. Defaults to True.
        with_timestamp (bool): Whether to include a timestamp in the log messages. Defaults to False.
        max_messages (int): The maximum number of messages to log per code. Defaults to 100.
    """

    def __init__(
        self,
        name: str,
        level: Level = Level.INFO,
        verbosity: int = 0,
        filename: str | None = None,
        stdout: bool = True,
        with_timestamp: bool = False,
        max_messages: int = 100,
    ) -> None:
        """
        Initializes the Logger instance.

        Args:
            name (str): The name of the logger.
            level (str): The log level (e.g., INFO, WARNING, ERROR). Defaults to "INFO".
            verbosity (int, optional): The verbosity level of the logger. Defaults to 0.
            filename (str | None, optional): The name of the file to log messages to. Defaults to None.
            stdout (bool, optional): Whether to log to stdout. Defaults to True.
            with_timestamp (bool, optional): Whether to include a timestamp in the log messages. Defaults to False.
            max_messages (int, optional): The maximum number of messages to log per code. Defaults to 100.
        """
        self.name = name
        self.level = level
        self.verbosity = verbosity
        self.filename = filename
        self.stdout = stdout
        self.with_timestamp = with_timestamp
        self.max_messages = max_messages
        self.max_messages_previously_met_for_code = []
        self.messages = []

        if self.filename:
            self.file_handle = open(self.filename, "w")
        else:
            self.file_handle = None

        self.entries = []

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

    def _get_entry_count_for_code(self, code: str) -> int:
        """
        Retrieves the count of log entries for a specific code.

        Args:
            code (str): The code associated with the log message.

        Returns:
            int: The count of log entries for the specified code.
        """
        return len([entry for entry in self.entries if entry.message.code == code])

    def log(self, code: str, *args, **kwargs) -> None:
        """
        Logs a message with the given code and arguments.


        Args:
            code (str): The code associated with the log message.
            *args: Positional arguments to format the message.
            **kwargs: Keyword arguments to format the message.
        """
        message = self._get_message(code)

        context = kwargs.copy()

        if message:
            if self.file_handle:
                context["file_handle"] = self.file_handle

            context["stdout"] = self.stdout

            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
            if self.with_timestamp:
                context["timestamp"] = timestamp

            context["max_messages"] = self.max_messages
            context["max_messages_reached"] = False
            context["max_messages_previously_met_for_code"] = False

            entry_count = self._get_entry_count_for_code(code)
            if entry_count >= self.max_messages or self.max_messages == -1:
                context["max_messages_reached"] = True
                context["max_messages_previously_met_for_code"] = (
                    code in self.max_messages_previously_met_for_code
                )
                self.max_messages_previously_met_for_code.append(code)

            output: str = message.log(*args, **context)
            self.entries.append(Entry(output, message, timestamp))

    def add_message(
        self,
        code: str,
        description: str,
        level: Level,
        verbosity: int = 0,
        format: str = "{}",
    ) -> None:
        """
        Adds a new message to the logger.

        Args:
            message (Message): The Message object to add.
        """
        self._add_message_object(Message(format, code, description, level, verbosity))

    def _add_message_object(self, message: Message) -> None:
        """
        Adds a new message to the logger.

        Args:
            message (Message): The Message object to add.
        """
        if message.code in [m.code for m in self.messages]:
            raise LogarooDuplicateCodeException(message.code)
        self.messages.append(message)

    def add_messages(
        self,
        messages: list[Message],
    ) -> None:
        """
        Adds a list of messages to the logger.

        Args:
            messages (list[Message]): A list of Message objects to add.
        """
        for message in messages:
            self._add_message_object(message)

    def __del__(self):
        """
        Cleans up the logger instance.
        Closes the file handle if it was opened.
        """
        if self.file_handle:
            self.file_handle.close()

    def get_summary(self) -> str:
        """
        Returns a summary of the logged message entries.

        Returns:
            str: A summary of the logged message entries.
        """
        summary = "Message summary:\n"
        for level in ORDERED_LEVELS:
            count = len(
                [entry for entry in self.entries if entry.message.level == level]
            )
            summary += f"  {level.name} = {count}\n"

        summary += "\n"
        summary += "Message codes:\n"
        codes: dict[str, list[Message]] = {}
        for entry in self.entries:
            code = entry.message.code
            if code not in codes:
                codes[code] = []
            codes[code].append(entry.message)

        for code, messages in codes.items():
            count = len(messages)
            first_message: Message = messages[0]
            summary += f"  {code}: {first_message.format} = {count}\n"

        return summary.strip()


class Entry:
    """
    Represents a log entry with it output, original message object and a timestamp.

    Attributes:
        output (str): The formatted log message.
        message (Message): The original message object.
        timestamp (str): The timestamp when the log entry was created.
    """

    def __init__(self, output: str, message: Message, timestamp: str):
        self.output = output
        self.message = message
        self.timestamp = timestamp
