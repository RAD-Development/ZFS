import os
from subprocess import Popen, PIPE
from typing import Optional, Tuple


def get_logger_dict(
    level: Optional[str] = "DEBUG", log_path: Optional[str] = ""
) -> dict:
    """Get the logging configuration dictionary.

    Args:
        level (str, optional): The logging level. Allowed values are 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
            Defaults to "DEBUG".
        log_path (str, optional): The path to the log file. Defaults to "" (empty string).

    Returns:
        dict: The logging configuration dictionary.

    Raises:
        ValueError: If an invalid logging level is provided.
        ValueError: If the log path directory does not exist.
    """

    level = level.strip().upper()
    allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if level not in allowed:
        raise ValueError(f"Invalid logging level {level}. Allowed values are {allowed}")

    handlers = {
        "console": {
            "level": level,
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    }

    if log_path:
        log_dir = os.path.dirname(log_path)
        if not os.path.isdir(log_dir):
            raise ValueError(
                f"Invalid log path: {log_path}. The directory does not exist."
            )
        handlers["file"] = {
            "level": level,
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": log_path,
        }

    return {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S %Z",
            }
        },
        "handlers": handlers,
        "root": {"level": level, "handlers": list(handlers.keys())},
        "disable_existing_loggers": False,
    }


def bash_wrapper(command: str) -> Tuple[str, Optional[str], int]:
    """Execute a bash command and capture the output.

    Args:
        command (str): The bash command to be executed.

    Returns:
        Tuple[str, Optional[str], int]: A tuple containing the output of the command (stdout) as a string,
        the error output (stderr) as a string (optional), and the return code as an integer.
    """

    process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        return output.decode(), error.decode(), process.returncode

    return output.decode(), None, process.returncode
