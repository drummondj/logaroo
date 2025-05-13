# Logaroo

Yet another python package for logging. Why is this different?

The idea behind Logaroo is to provide a very simple way to generate documented log messages to users of your application or package.

Each message has a code that is documented, so a user knows what to do when that message occurs.

This is useful for complex applications that have many different types of messages, that need to be processed and documented individually.



Feature list (under development):

1. Documented message structure
2. Log to a file, stream, stdout/err or a combination of them

## Usage

### Basic examples

To use Logaroo, create a `logger` module in your Python package containing:

**my_logger.py**
```python
import logaroo

my_logger = logaroo.Logger(
    level = "INFO",
    verbosity = 1,
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

Then from anywhere in you application code:

```python
from my_logger import my_logger

my_logger.log("ERR-001", "Something went wrong")
my_logger.log("VAL-001", value1=10, value2=9)
```

### Logging to a file and stdout

To log to a file, just add the filename parameter:

```python
my_logger = logaroo.Logger(
    level = "INFO",
    verbosity = 1,
    filename="my_logger.log",
)
```
