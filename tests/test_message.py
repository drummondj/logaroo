from io import StringIO
import unittest
from unittest.mock import patch

from src.logaroo import Message


class TestMessage(unittest.TestCase):
    def setUp(self):
        self.message = Message(
            format="Test message: {}",
            code="TEST-001",
            description="This is a test message.",
            level="INFO",
            verbosity=1,
        )

    def test_initialization(self):
        self.assertEqual(self.message.format, "Test message: {}")
        self.assertEqual(self.message.code, "TEST-001")
        self.assertEqual(self.message.description, "This is a test message.")
        self.assertEqual(self.message.level, "INFO")
        self.assertEqual(self.message.verbosity, 1)

    def test_log(self):
        # Test that stdout contains the expected message
        with patch("sys.stdout", new_callable=StringIO) as f:
            self.message.log("Hello, World!")
            output = f.getvalue().strip()
        self.assertEqual(output, "INFO: Test message: Hello, World! (TEST-001)")
