# Logaroo

Yet another python package for logging. Why is this different?

The idea behind Logaroo is to provide a very simple way to generate documented log messages to users of your application or package.

Each message has a code that is documented, so a user knows what to do when that message occurs.

This is useful for complex applications that have many different types of messages, that need to be processed and documented individually.



Feature list (under development):

1. Documented message structure using codes
2. Log to stdout, a file or both
3. Control maximum message count per code
4. Add optional timestamps to messages
5. Generate a message summary containing counts per level and code

## Usage

### Basic examples

To use Logaroo, create a `logger` module in your Python package containing:

**my_logger.py**
```python
import logaroo

my_logger = logaroo.Logger(
    level="INFO",
    verbosity=1,
)

my_logger.add_message(
    level="ERROR",
    code="ERR-001",
    description="This is a basic error message with no special formatting",
)

my_logger.add_message(
    level="WARNING",
    code="VAL-001",
    format="Value {value1} is larger than {value2}",
    description="A warning message with named parameters",
)
```

Then from anywhere in your application code:

```python
from my_logger import my_logger

my_logger.log("ERR-001", "Something went wrong")
my_logger.log("VAL-001", value1=10, value2=9)
```

### Logging to a file and stdout

To log to a file, just add the filename parameter:

```python
my_logger = logaroo.Logger(
    filename="my_logger.log",
)
```

To suppress logging to stdout and just log to a file:

```python
my_logger = logaroo.Logger(
    filename="my_logger.log",
    stdout=False,
)
```

### Maximum messages per code

The default number of messages generated per code are 100. You can change this value or change to -1 for infinite messages:

```python
my_logger = logaroo.Logger(
    max_messages=10
)
```

### Timestamps

You can add ISO formatted timestamps to the beginning of messages:

```
my_logger = logaroo.Logger(
    with_timestamp=True,
)
```

### Generating a summary

You can generate a summary of message counts using the `get_summary()` method:

```python
print(my_logger.get_summary())
```

```
Message summary:
  DEBUG = 1
  INFO = 2
  WARNING = 0
  ERROR = 3
  CRITICAL = 0

Message codes:
  TEST-001: Test message: {} = 2
  TEST-002: Test message: {} = 1
  TEST-003: Test message: {} = 1
  TEST-004: Test message: {} = 1
  TEST-005: Syntax error on line {}:{} = 1
```
