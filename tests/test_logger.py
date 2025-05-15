# type: ignore
import filecmp
from io import StringIO
import os
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from logaroo import Logger, Level, LogarooMissingCodeException
from logaroo.exceptions import LogarooDuplicateCodeException


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.logger: Logger = Logger(
            name="TestLogger",
            verbosity=1,
        )

        self.logger.add_message(
            format="Test message: {}",
            code="TEST-001",
            description="This is a test message.",
            level=Level.INFO,
            verbosity=1,
        )

        self.logger.add_message(
            format="Test message: {}",
            code="TEST-002",
            description="This is another test message with level=ERROR.",
            level=Level.ERROR,
            verbosity=1,
        )

        self.logger.add_message(
            format="Test message: {}",
            code="TEST-003",
            description="This is another test message, with verbosity=2.",
            level=Level.ERROR,
            verbosity=2,
        )

        self.logger.add_message(
            format="Test message: {}",
            code="TEST-004",
            description="This is another test message, with level=DEBUG.",
            level=Level.DEBUG,
            verbosity=1,
        )

        self.logger.add_message(
            format="Syntax error on line {}:{}",
            code="TEST-005",
            description="Un-named argument format.",
            level=Level.ERROR,
            verbosity=1,
        )

        self.logger.add_message(
            format="value {value1} is larger than {value2}",
            code="TEST-006",
            description="Testing format with named arguments and specific types.",
            level=Level.CRITICAL,
            verbosity=1,
        )

    def test_initialization(self):
        self.assertEqual(self.logger.name, "TestLogger")
        self.assertEqual(self.logger.level, Level.INFO)
        self.assertEqual(self.logger.verbosity, 1)
        self.assertEqual(len(self.logger.messages), 6)
        self.assertEqual(self.logger.filename, None)

    def test_log(self):
        # Test that stdout contains the expected message
        with patch("sys.stdout", new_callable=StringIO) as f:
            self.logger.log("TEST-001", "Hello, World!")
            output = f.getvalue().strip()
        self.assertEqual(output, "INFO: Test message: Hello, World! (TEST-001)")

    def test_wrong_level(self):
        # Test that the message is not logged if the level is above the logger's level
        with patch("sys.stdout", new_callable=StringIO) as f:
            self.logger.log("TEST-004", "Hello, World!")
            output = f.getvalue().strip()
        self.assertEqual(output, "")

    def test_wrong_verbosity(self):
        # Test that the message is not logged if the verbosity is above the logger's verbosity
        with patch("sys.stdout", new_callable=StringIO) as f:
            self.logger.log("TEST-003", "Hello, World!")
            output = f.getvalue().strip()
        self.assertEqual(output, "")

    def test_log_to_file(self):
        # Create a temporary directory
        with TemporaryDirectory() as tempdir:
            filename = f"{tempdir}/test.log"
            logger = Logger(
                name="TestLogger",
                verbosity=1,
                filename=filename,
            )
            logger.add_messages(self.logger.messages)
            with patch("sys.stdout", new_callable=StringIO) as f:
                logger.log("TEST-001", "Hello, World!")
                logger.log("TEST-002", "Hello, World!")
            logger.__del__()  # Close the file handle

            # Check the contents of the log file
            with open(filename, "r") as f:
                output = f.readlines()
            self.assertEqual(
                output[0], "INFO: Test message: Hello, World! (TEST-001)\n"
            )
            self.assertEqual(
                output[1],
                "ERROR: Test message: Hello, World! (TEST-002)\n",
            )

    def test_log_syntax_error(self):
        # Test that a syntax error in the message format raises an exception
        with patch("sys.stdout", new_callable=StringIO) as f:
            self.logger.log("TEST-005", "/this/is/a/test", 42)
            output = f.getvalue().strip()
        self.assertEqual(
            output, "ERROR: Syntax error on line /this/is/a/test:42 (TEST-005)"
        )

    def test_log_with_named_arguments(self):
        # Test that the message is logged with named arguments
        with patch("sys.stdout", new_callable=StringIO) as f:
            self.logger.log("TEST-006", value1=42, value2=24)
            output = f.getvalue().strip()
        self.assertEqual(
            output,
            "CRITICAL: value 42 is larger than 24 (TEST-006)",
        )

    def test_missing_code_exception(self):
        # Test that a missing code raises an exception
        with self.assertRaises(LogarooMissingCodeException):
            self.logger.log("TEST-999")

    def test_file_only(self):
        # Test that the logger only logs to a file
        with TemporaryDirectory() as tempdir:
            filename = f"{tempdir}/test.log"
            logger = Logger(
                name="TestLogger",
                verbosity=1,
                filename=filename,
                stdout=False,
            )
            logger.add_messages(self.logger.messages)
            with patch("sys.stdout", new_callable=StringIO) as f:
                logger.log("TEST-001", "Hello, World!")
                output = f.getvalue().strip()
            self.assertEqual(output, "")
            logger.__del__()

            # Check the contents of the log file
            with open(filename, "r") as f:
                output = f.readlines()
            self.assertEqual(
                output[0], "INFO: Test message: Hello, World! (TEST-001)\n"
            )

    def test_log_with_timestamp(self):
        # Test that the logger includes a timestamp in the log messages
        logger = Logger(
            name="TestLogger",
            verbosity=1,
            with_timestamp=True,
        )
        logger.add_messages(self.logger.messages)
        with patch("sys.stdout", new_callable=StringIO) as f:
            logger.log("TEST-001", "Hello, World!")
            output = f.getvalue().strip()

        # Get timestamp of last entry
        timestamp = logger.entries[-1].timestamp
        self.assertEqual(
            output,
            f"{timestamp} - INFO: Test message: Hello, World! (TEST-001)",
        )

    def test_max_messages(self):
        # Test that the logger limits the number of messages logged per code
        logger = Logger(
            name="TestLogger",
            verbosity=1,
            max_messages=2,
        )
        logger.add_messages(self.logger.messages)
        with patch("sys.stdout", new_callable=StringIO) as f:
            for i in range(5):
                logger.log("TEST-001", f"Hello, World! {i}")
            output = f.getvalue()

        # Check that only the first 2 messages are logged, along with a warning about truncated messages
        self.assertEqual(
            output,
            "INFO: Test message: Hello, World! 0 (TEST-001)\n"
            + "INFO: Test message: Hello, World! 1 (TEST-001)\n"
            + "WARNING: Maximum number of messages (2) reached for code TEST-001.\n",
        )

    def test_duplicate_code_exception(self):
        # Test that a duplicate code raises an exception
        with self.assertRaises(LogarooDuplicateCodeException):
            self.logger.add_message(
                format="Duplicate message: {}",
                code="TEST-001",
                description="This is a duplicate message.",
                level=Level.INFO,
                verbosity=1,
            )

    def test_get_summary(self):
        # Test that the logger returns a summary of the logged message entries
        with patch("sys.stdout", new_callable=StringIO) as f:
            self.logger.level = Level.DEBUG
            self.logger.verbosity = 999
            self.logger.log("TEST-001", "Hello, World!")
            self.logger.log("TEST-001", "Hello, World!")
            self.logger.log("TEST-002", "Hello, World!")
            self.logger.log("TEST-003", "Hello, World!")
            self.logger.log("TEST-004", "Hello, World!")
            self.logger.log("TEST-005", 2, 1)
            self.assertEqual(
                len(self.logger.entries),
                6,
            )
        summary = self.logger.get_summary()

        expected_output = (
            "Message summary:\n"
            "  DEBUG = 1\n"
            "  INFO = 2\n"
            "  WARNING = 0\n"
            "  ERROR = 3\n"
            "  CRITICAL = 0\n"
            "\n"
            "Message codes:\n"
            "  TEST-001: Test message: {} = 2\n"
            "  TEST-002: Test message: {} = 1\n"
            "  TEST-003: Test message: {} = 1\n"
            "  TEST-004: Test message: {} = 1\n"
            "  TEST-005: Syntax error on line {}:{} = 1"
        )
        self.assertEqual(summary, expected_output)

    def test_to_json(self):
        # Test that the logger can be converted to JSON
        fn = "tmp.json"
        with open(fn, "w") as temp_file:
            json_output = self.logger.to_json()
            temp_file.write(json_output)

        self.assertTrue(filecmp.cmp(fn, "tests/test.json"))
        os.remove(fn)
