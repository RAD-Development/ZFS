import logging
import logging.config
from datetime import datetime
from os import getenv
from pathlib import Path

from common import get_logger_dict, load_config_data
from zfs_snapshot_manager import create_snapshots, delete_snapshots


def main():
    logging.config.dictConfig(get_logger_dict("DEBUG", "./snapshot_manager.log"))

    logging.info("snapshot_manager starting")

    now = datetime.now()

    config_data = load_config_data(Path(__file__).parent / "config.toml")
    logging.debug("config_data %s", config_data)

    datasets = set(config_data.keys())
    logging.info("%s are being snapshotted", datasets)

    create_snapshots(now=now, dataset_names=datasets)

    delete_snapshots(config_data=config_data)

    logging.info("snapshot_manager done")


if __name__ == "__main__":
    main()
