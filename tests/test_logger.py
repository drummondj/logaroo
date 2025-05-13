from io import StringIO
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.logaroo import Logger, Message


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.messages = [
            Message(
                format="Test message: {}",
                code="TEST-001",
                description="This is a test message.",
                level="INFO",
                verbosity=1,
            )
        ]

        self.messages.append(
            Message(
                format="Test message: {}",
                code="TEST-002",
                description="This is another test message with level=ERROR.",
                level="ERROR",
                verbosity=1,
            )
        )

        self.messages.append(
            Message(
                format="Test message: {}",
                code="TEST-003",
                description="This is another test message, with verbosity=2.",
                level="ERROR",
                verbosity=2,
            )
        )

        self.messages.append(
            Message(
                format="Test message: {}",
                code="TEST-004",
                description="This is another test message, with level=DEBUG.",
                level="DEBUG",
                verbosity=1,
            )
        )

        self.logger = Logger(
            name="TestLogger",
            messages=self.messages,
            level="INFO",
            verbosity=1,
        )

    def test_initialization(self):
        self.assertEqual(self.logger.name, "TestLogger")
        self.assertEqual(self.logger.level, "INFO")
        self.assertEqual(self.logger.verbosity, 1)
        self.assertEqual(len(self.logger.messages), 4)
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
                messages=self.messages,
                level="INFO",
                verbosity=1,
                filename=filename,
            )
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
