from datetime import datetime
from re import search, compile as re_compile

from collections import defaultdict

from common import bash_wrapper


def get_snapshots() -> dict[str, set[str]]:
    output = bash_wrapper("zfs list -Hp -t snapshot -o name")

    snapshot_list = output.strip().split("\n")

    split_snapshots = [item.split("@") for item in snapshot_list]

    snapshots_dict = defaultdict(set)
    [snapshots_dict[name].add(item) for name, item in split_snapshots]

    return dict(snapshots_dict)


def create_snapshots(now: datetime, dataset_names: set[str]):
    # Im not a math major
    # time = now.replace(minute=(int(now.minute/15)*15)).strftime("%Y-%m-%d-%H-%M")
    nearest_15_min = now.replace(minute=(now.minute - (now.minute % 15)))
    time_stamp = nearest_15_min.strftime("auto_%Y%m%d%H%M")
    for dataset_name in dataset_names:
        command = f"sudo zfs snapshot {dataset_name}@{time_stamp}"
        bash_wrapper(command)


def delete_snapshot(dataset_name: str, snapshot: str):
    bash_wrapper(f"sudo zfs destroy {dataset_name}@{snapshot}")


def delete_snapshots_in_dataset(
    dataset_name: str,
    snapshot_filter: str,
    snapshots: set[str],
    snapshots_wanted: int,
):
    filtered_snapshots = [
        snapshot for snapshot in snapshots if search(snapshot_filter, snapshot)
    ]
    filtered_snapshots.sort()

    for snapshot in filtered_snapshots[:-snapshots_wanted]:
        delete_snapshot(dataset_name=dataset_name, snapshot=snapshot)


def delete_snapshots(config_data: dict):
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
