import logging

from datetime import datetime
from re import search, compile as re_compile

from collections import defaultdict

from common import bash_wrapper


def get_snapshots() -> dict[str, set[str]]:
    """Gets all snapshots from zfs and process then is test dicts of sets

    Returns:
        dict[str, set[str]]: a dicts of all pool names that have snapshots with a set of all snapshot names
    """
    output = bash_wrapper("zfs list -Hp -t snapshot -o name")

    snapshot_list = output.strip().split("\n")

    split_snapshots = [item.split("@") for item in snapshot_list]

    snapshots_dict = defaultdict(set)
    [snapshots_dict[name].add(item) for name, item in split_snapshots]

    return dict(snapshots_dict)


def create_snapshots(now: datetime, dataset_names: set[str]):
    """Create a zfs snapshot with timestamp at the nearest 15 min

    Args:
        now (datetime): the current time
        dataset_names (set[str]): a set of all the pools you want to be snapshotted
    """
    nearest_15_min = now.replace(minute=(now.minute - (now.minute % 15)))
    time_stamp = nearest_15_min.strftime("auto_%Y%m%d%H%M")
    for dataset_name in dataset_names:
        command = f"sudo zfs snapshot {dataset_name}@{time_stamp}"
        bash_wrapper(command)


def delete_snapshot(dataset_name: str, snapshot: str):
    """Deletes a zfs snapshot

    Args:
        dataset_name (str): a dataset name
        snapshot (str): a snapshot name
    """
    logging.debug("deleting %s@%s", dataset_name, snapshot)
    bash_wrapper(f"sudo zfs destroy {dataset_name}@{snapshot}")


def delete_snapshots_in_dataset(
    dataset_name: str,
    snapshot_filter: str,
    snapshots: set[str],
    snapshots_wanted: int,
):
    """deletes  all the snapshot in a dataset that match a filter

    Args:
        dataset_name (str): the name of the data set name
        snapshot_filter (str): the snapshot filter
        snapshots (set[str]): set of snapshot names
        snapshots_wanted (int): the number of snapshot that are wanted
    """
    filtered_snapshots = [
        snapshot for snapshot in snapshots if search(snapshot_filter, snapshot)
    ]
    filtered_snapshots.sort()

    logging.debug("snapshot_filter %s", snapshot_filter)
    logging.debug("filtered_snapshots %s", filtered_snapshots)
    
    snapshots_being_deleted = filtered_snapshots[:-snapshots_wanted]
    logging.info("%s are being deleted", snapshots_being_deleted)

    for snapshot in snapshots_being_deleted:
        delete_snapshot(dataset_name=dataset_name, snapshot=snapshot)


def delete_snapshots(config_data: dict):
    """delete all snapshots that match the pattern in config data

    Args:
        config_data (dict): the data from config.toml
    """
    dataset_snapshots = get_snapshots()

    FILTERS = {
        "15_min": re_compile(r"auto_\d{10}(?:15|30|45)"),
        "hourly": re_compile(r"auto_\d{8}(?!00)\d{2}00"),
        "daily": re_compile(r"auto_\d{6}(?!01)\d{2}0000"),
        "monthly": re_compile(r"auto_\d{6}010000"),
    }

    for dataset_name, filter_name_count in config_data.items():
        snapshots = dataset_snapshots.get(dataset_name)
        for filter_name, count in filter_name_count.items():
            delete_snapshots_in_dataset(
                dataset_name=dataset_name,
                snapshot_filter=FILTERS.get(filter_name),
                snapshots_wanted=count,
                snapshots=snapshots,
            )
