import logging
import logging.config
from tomllib import load
from re import search, compile as re_compile
from datetime import datetime

from collections import defaultdict

from common import get_logger_dict, bash_wrapper


def load_config_data(file_path: str):
    with open(file_path, "rb") as f:
        config_data = load(f)
    return config_data


def get_snapshots():
    output, error, return_code = bash_wrapper("zfs list -Hp -t snapshot -o name")
    if return_code != 0:
        logging.critical("%s %i", error, return_code)
        raise ValueError(error)

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
        _, error, return_code = bash_wrapper(command)
        if return_code != 0:
            logging.critical("%s %i", error, return_code)


def manage_snapshots(
    dataset_name: str, snapshot_filter: str, snapshots: set[str], snapshots_wanted: int
):
    filtered_snapshots = [
        snapshot for snapshot in snapshots if search(snapshot_filter, snapshot)
    ]
    filtered_snapshots.sort()
    print(filtered_snapshots)

    test = filtered_snapshots[:-snapshots_wanted]
    print(test)
    for snapshot in test:
        command = f"sudo zfs destroy {dataset_name}@{snapshot}"
        _, error, return_code = bash_wrapper(command)
        if return_code != 0:
            logging.critical("%s %i", error, return_code)
            raise ValueError(error)


def main():
    logging.config.dictConfig(get_logger_dict("DEBUG", "./Log.log"))

    logging.info("snapshot_manager starting")

    now = datetime.now()

    config_data = load_config_data("snapshot.toml")

    create_snapshots(now=now, dataset_names=set(config_data.keys()))

    dataset_snapshots = get_snapshots()

    filters = {
        "15_min": re_compile(r"auto_[0-9]{10}(?:15|30|45)"),
        "hourly": re_compile(r"auto_[0-9]{8}(?!12)[0-9]{2}00"),
        "daily": re_compile(r"auto_[0-9]{6}(?!01)[0-9]{2}1200"),
        "monthly": re_compile(r"auto_[0-9]{6}011200"),
    }

    for dataset_name, filter_name_count in config_data.items():
        snapshots = dataset_snapshots.get(dataset_name)
        for filter_name, count in filter_name_count.items():
            manage_snapshots(
                dataset_name=dataset_name,
                snapshot_filter=filters.get(filter_name),
                snapshots_wanted=count,
                snapshots=snapshots,
            )

    logging.info("snapshot_manager done")


if __name__ == "__main__":
    main()