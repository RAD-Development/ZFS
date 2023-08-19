from pathlib import Path
from unittest.mock import patch
from tempfile import NamedTemporaryFile

import pytest

from src.common import get_logger_dict, bash_wrapper, load_config_data


class TestGetLoggerDict:
    @pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_get_logger_dict_with_valid_level(self, level):
        logger_dict = get_logger_dict(level=level)
        assert logger_dict["root"]["level"] == level

    def test_get_logger_dict_with_invalid_level(self):
        with pytest.raises(ValueError, match="Invalid logging level INVALID_LEVEL"):
            get_logger_dict(level="INVALID_LEVEL")

    @patch(target="common.lib.os.path.isdir", return_value=False)
    def test_get_logger_dict_with_invalid_log_path(self, _mock_isdir):
        with pytest.raises(ValueError, match="Invalid log path: /path/to/logfile.log"):
            get_logger_dict(level="DEBUG", log_path="/path/to/logfile.log")

    def test_get_logger_dict_without_log_path(self):
        logger_dict = get_logger_dict(level="DEBUG")
        assert "file" not in logger_dict["handlers"]
        assert "console" in logger_dict["handlers"]

    @patch(target="common.lib.os.path.isdir", return_value=True)
    def test_get_logger_dict_with_log_path(self, _mock_isdir):
        logger_dict = get_logger_dict(level="DEBUG", log_path="/path/to/logfile.log")
        assert "console", "file" in logger_dict["handlers"]


class TestBashWrapper:
    def test_bash_wrapper_with_successful_command(self):
        assert bash_wrapper("echo test"), "test"

    def test_bash_wrapper_with_failing_command(self):
        error = "ls: cannot access '/non/existent/directory': No such file or directory"
        with pytest.raises(ValueError, match=error):
            bash_wrapper("ls /non/existent/directory")


class TestLoadConfigData:
    def test_load_config_data(self):
        with NamedTemporaryFile() as temp_file:
            temp_file.write(b"['test/data']\n15_min = 6\nhourly = 2")
            temp_file.flush()

            test_result = {"test/data": {"15_min": 6, "hourly": 2}}
            assert load_config_data(Path(temp_file.name)) == test_result
