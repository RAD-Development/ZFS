import unittest
from datetime import datetime, timezone
from re import compile as re_compile
from tempfile import NamedTemporaryFile
from unittest.mock import patch, MagicMock, call

from snapshot_manager import (
    load_config_data,
    get_snapshots,
    create_snapshots,
    manage_snapshots,
)


class TestGetSnapshots(unittest.TestCase):
    @patch(target="snapshot_manager.snapshot_manager.bash_wrapper", return_value=MagicMock())
    def test_get_snapshots(self, mock_bash_wrapper):
        comand_return = "mock_snapshot_1@time\nmock_snapshot_2@time\n"
        mock_bash_wrapper.return_value = (comand_return, "", 0)

        expected_result = {"mock_snapshot_1": {"time"}, "mock_snapshot_2": {"time"}}
        self.assertEqual(get_snapshots(), expected_result)

    @patch(target="snapshot_manager.snapshot_manager.bash_wrapper", return_value=MagicMock())
    def test_get_snapshots_error(self, mock_bash_wrapper):
        mock_bash_wrapper.return_value = ("", "", 1)
        with self.assertRaises(ValueError):
            get_snapshots()


class TestCreateSnapshots(unittest.TestCase):
    @patch(target="snapshot_manager.snapshot_manager.bash_wrapper", return_value=MagicMock())
    def test_create_snapshots(self, mock_bash_wrapper):
        mock_bash_wrapper.return_value = ("", "", 0)
        now = datetime(2023, 8, 1, 0, 0, 0, 0, timezone.utc)

        create_snapshots(now, {"dataset1", "dataset2"})

        expected_calls = [
            call(f"sudo zfs snapshot dataset1@auto_202308010000"),
            call(f"sudo zfs snapshot dataset2@auto_202308010000"),
        ]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)

    @patch(
        target="snapshot_manager.snapshot_manager.bash_wrapper",
        return_value=("", "An error occurred", 1),
    )
    @patch(target="snapshot_manager.snapshot_manager.logging")
    def test_create_snapshots_error(self, mock_logging, mock_bash_wrapper):
        now = datetime(2023, 8, 1, 0, 0, 0, 0, timezone.utc)

        create_snapshots(now, {"dataset1", "dataset2"})

        expected_calls = [
            call(f"sudo zfs snapshot dataset1@auto_202308010000"),
            call(f"sudo zfs snapshot dataset2@auto_202308010000"),
        ]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)

        expected_calls = [
            call("%s %i", "An error occurred", 1),
            call("%s %i", "An error occurred", 1),
        ]
        mock_logging.critical.assert_has_calls(expected_calls, any_order=True)


class TestManageSnapshots(unittest.TestCase):
    @patch(target="snapshot_manager.snapshot_manager.bash_wrapper", return_value=MagicMock())
    def test_manage_snapshots(self, mock_bash_wrapper):
        mock_bash_wrapper.return_value = ("", "", 0)

        dataset_name = "test/data"
        snapshot_filter = re_compile(r"auto_[0-9]{10}(?:15|30|45)")
        snapshots = [
            "auto_202208061215",
            "auto_202308010000",
            "auto_202308061215",
            "auto_202308061230",
            "auto_202308061245",
        ]

        snapshots_wanted = 1

        manage_snapshots(dataset_name, snapshot_filter, snapshots, snapshots_wanted)

        expected_calls = [
            call(f"sudo zfs destroy test/data@auto_202208061215"),
            call(f"sudo zfs destroy test/data@auto_202308061215"),
            call(f"sudo zfs destroy test/data@auto_202308061230"),
        ]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)

    @patch(target="snapshot_manager.snapshot_manager.bash_wrapper", return_value=MagicMock())
    @patch(target="snapshot_manager.snapshot_manager.logging")
    def test_bash_wrapper_error(self, mock_logging, mock_bash_wrapper):
        mock_bash_wrapper.return_value = ("", "An error occurred", 1)

        dataset_name = "test/data"
        snapshot_filter = re_compile(r"auto_[0-9]{10}(?:15|30|45)")
        snapshots = [
            "auto_202208061215",
            "auto_202308010000",
            "auto_202308061215",
        ]

        snapshots_wanted = 1

        with self.assertRaises(ValueError):
            manage_snapshots(dataset_name, snapshot_filter, snapshots, snapshots_wanted)

        expected_calls = [call(f"sudo zfs destroy test/data@auto_202208061215")]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)
        mock_logging.critical.assert_called_once_with("%s %i", "An error occurred", 1)


class TestLoadConfigData(unittest.TestCase):
    def test_load_config_data(self):
        with NamedTemporaryFile() as temp_file:
            temp_file.write(b"['test/data']\n15_min = 6\nhourly = 2")
            temp_file.flush()

            expected_result = {"test/data": {"15_min": 6, "hourly": 2}}
            self.assertEqual(load_config_data(temp_file.name), expected_result)


class TestLoadConfigData(unittest.TestCase):
    def test_load_config_data(self):
        with NamedTemporaryFile() as temp_file:
            temp_file.write(b"['test/data']\n15_min = 6\nhourly = 2")
            temp_file.flush()

            expected_result = {"test/data": {"15_min": 6, "hourly": 2}}
            self.assertEqual(load_config_data(temp_file.name), expected_result)


if __name__ == "__main__":
    unittest.main()
