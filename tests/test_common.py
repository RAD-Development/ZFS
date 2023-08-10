import os
import pytest
from unittest.mock import patch, Mock
from src.common import get_logger_dict, bash_wrapper

@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_get_logger_dict_with_valid_level(level):
    with patch("os.path.isdir", return_value=True):
        logger_dict = get_logger_dict(level=level, log_path="/path/to/logfile.log")
        assert logger_dict['root']['level'] == level

def test_get_logger_dict_with_invalid_level():
    with pytest.raises(ValueError, match="Invalid logging level INVALID_LEVEL"):
        get_logger_dict(level="INVALID_LEVEL") 

def test_get_logger_dict_with_invalid_log_path():
    with patch("os.path.isdir", return_value=False):
        with pytest.raises(ValueError, match="Invalid log path: /path/to/logfile.log"):
            get_logger_dict(level="DEBUG", log_path="/path/to/logfile.log")

def test_get_logger_dict_without_log_path():
    logger_dict = get_logger_dict(level="DEBUG")
    assert 'file' not in logger_dict['handlers']
    assert 'console' in logger_dict['handlers']


def test_bash_wrapper_with_successful_command():
    stdout, stderr, returncode = bash_wrapper("echo test")

    assert stdout.strip() == 'test'
    assert stderr is None
    assert returncode == 0

def test_bash_wrapper_with_failing_command():
    stdout, stderr, returncode = bash_wrapper("ls /non/existent/directory")

    assert stdout == ''
    assert stderr == "ls: cannot access '/non/existent/directory': No such file or directory\n"
    assert returncode == 2
