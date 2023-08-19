import unittest
from datetime import datetime, timezone
from re import compile as re_compile
from unittest.mock import patch, MagicMock, call

from snapshot_manager import (
    get_snapshots,
    create_snapshots,
    delete_snapshots,
    delete_snapshots_in_dataset,
)


class TestGetSnapshots:
    @patch(
        target="snapshot_manager.lib.bash_wrapper",
        return_value=MagicMock(),
    )
    def test_get_snapshots(self, mock_bash_wrapper):
        mock_bash_wrapper.return_value = "mock_snapshot_1@time\nmock_snapshot_2@time\n"

        expected_result = {"mock_snapshot_1": {"time"}, "mock_snapshot_2": {"time"}}
        assert get_snapshots() == expected_result


class TestCreateSnapshots:
    @patch(
        target="snapshot_manager.lib.bash_wrapper",
        return_value=MagicMock(),
    )
    def test_create_snapshots(self, mock_bash_wrapper):
        mock_bash_wrapper.return_value = ""
        now = datetime(2023, 8, 1, 0, 0, 0, 0, timezone.utc)

        create_snapshots(now, {"dataset1", "dataset2"})

        expected_calls = [
            call("sudo zfs snapshot dataset1@auto_202308010000"),
            call("sudo zfs snapshot dataset2@auto_202308010000"),
        ]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)


class TestManageSnapshots:
    @patch(target="snapshot_manager.lib.bash_wrapper", return_value="")
    def test_manage_snapshots(self, mock_bash_wrapper):
        dataset_name = "test/data"
        snapshot_filter = re_compile(r"auto_\d{10}(?:15|30|45)")
        snapshots = [
            "auto_202208061215",
            "auto_202308010000",
            "auto_202308061215",
            "auto_202308061230",
            "auto_202308061245",
        ]

        snapshots_wanted = 1

        delete_snapshots_in_dataset(
            dataset_name=dataset_name,
            snapshot_filter=snapshot_filter,
            snapshots=snapshots,
            snapshots_wanted=snapshots_wanted,
        )

        expected_calls = [
            call("sudo zfs destroy test/data@auto_202208061215"),
            call("sudo zfs destroy test/data@auto_202308061215"),
            call("sudo zfs destroy test/data@auto_202308061230"),
        ]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)


class TestDeleteSnapshots:
    @patch(target="snapshot_manager.lib.delete_snapshot", return_value="")
    @patch(target="snapshot_manager.lib.get_snapshots", return_value=MagicMock())
    def test_delete_snapshots(self, mock_get_snapshots, mock_delete_snapshot):
        snapshots = {
            "auto_202208010030",
            "auto_202308010030",
            "auto_202308052345",
            "auto_202308060000",
            "auto_202308060015",
            "auto_202308060030",
            "auto_202308060045",
            "auto_202308060145",
            "auto_202308060200",
            "auto_202308060300",
            "auto_202308061200",
            "auto_202308061215",
            "auto_202308190030",
        }

        mock_get_snapshots.return_value = {
            "test/data": snapshots,
            "test/data2": snapshots,
            "test/data3": snapshots,
        }

        config_data = {
            "test/data": {"15_min": 6, "hourly": 2, "daily": 0, "monthly": 0},
            "test/data2": {"15_min": 2},
        }
        delete_snapshots(config_data=config_data)

        expected_calls = [
            call(dataset_name="test/data", snapshot="auto_202208010030"),
            call(dataset_name="test/data", snapshot="auto_202308010030"),
            call(dataset_name="test/data", snapshot="auto_202308052345"),
            call(dataset_name="test/data", snapshot="auto_202308060200"),
            call(dataset_name="test/data2", snapshot="auto_202208010030"),
            call(dataset_name="test/data2", snapshot="auto_202308010030"),
            call(dataset_name="test/data2", snapshot="auto_202308052345"),
            call(dataset_name="test/data2", snapshot="auto_202308060015"),
            call(dataset_name="test/data2", snapshot="auto_202308060030"),
            call(dataset_name="test/data2", snapshot="auto_202308060045"),
            call(dataset_name="test/data2", snapshot="auto_202308060145"),
        ]

        mock_delete_snapshot.assert_has_calls(expected_calls, any_order=True)


if __name__ == "__main__":
    unittest.main()
