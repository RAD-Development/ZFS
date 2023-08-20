from datetime import datetime, timezone
from re import compile as re_compile
from unittest.mock import patch, MagicMock, call

from zfs_snapshot_manager import (
    get_snapshots,
    create_snapshots,
    delete_snapshots,
    delete_snapshots_in_dataset,
)


class TestGetSnapshots:
    @patch(
        target="zfs_snapshot_manager.lib.bash_wrapper",
        return_value=MagicMock(),
    )
    def test_get_snapshots(self, mock_bash_wrapper):
        mock_bash_wrapper.return_value = "mock_snapshot_1@time\nmock_snapshot_2@time\n"

        expected_result = {"mock_snapshot_1": {"time"}, "mock_snapshot_2": {"time"}}
        assert get_snapshots() == expected_result


class TestCreateSnapshots:
    @patch(
        target="zfs_snapshot_manager.lib.bash_wrapper",
        return_value=MagicMock(),
    )
    def test_create_snapshots(self, mock_bash_wrapper):
        mock_bash_wrapper.return_value = ""
        now = datetime(2023, 8, 1, 0, 0, 0, 0, timezone.utc)

        create_snapshots(now, {"dataset1", "dataset2"})

        expected_calls = [
            call("zfs snapshot dataset1@auto_202308010000"),
            call("zfs snapshot dataset2@auto_202308010000"),
        ]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)


class TestManageSnapshots:
    @patch(target="zfs_snapshot_manager.lib.bash_wrapper", return_value="")
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
            call("zfs destroy test/data@auto_202208061215"),
            call("zfs destroy test/data@auto_202308061215"),
            call("zfs destroy test/data@auto_202308061230"),
        ]
        mock_bash_wrapper.assert_has_calls(expected_calls, any_order=True)


class TestDeleteSnapshots:
    @patch(target="zfs_snapshot_manager.lib.delete_snapshot", return_value="")
    @patch(target="zfs_snapshot_manager.lib.get_snapshots", return_value=MagicMock())
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
            "test/data4": snapshots,
            "test/data5": snapshots,
            "test/data6": snapshots,
        }

        config_data = {
            "test/data4": {"15_min": 6, "hourly": 2, "daily": 0, "monthly": 0},
            "test/data5": {"15_min": 2},
        }
        delete_snapshots(config_data=config_data)

        snapshot_names1 = (
            "auto_202208010030",
            "auto_202308010030",
            "auto_202308052345",
            "auto_202308060200",
        )
        expected_calls1 = [
            call(dataset_name="test/data4", snapshot_name=snapshot_name)
            for snapshot_name in snapshot_names1
        ]

        snapshot_names2 = (
            "auto_202208010030",
            "auto_202308010030",
            "auto_202308052345",
            "auto_202308060015",
            "auto_202308060030",
            "auto_202308060045",
            "auto_202308060145",
        )
        expected_calls2 = [
            call(dataset_name="test/data5", snapshot_name=snapshot_name)
            for snapshot_name in snapshot_names2
        ]

        expected_calls = expected_calls1 + expected_calls2
        mock_delete_snapshot.assert_has_calls(expected_calls, any_order=True)
