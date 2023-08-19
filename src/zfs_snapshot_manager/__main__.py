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

    config_dir = getenv("ZFS_SNAPSHOT_MANAGER_CONFIG_DIR", __file__)
    config_file = getenv("ZFS_SNAPSHOT_MANAGER_CONFIG_FILE", "config.toml")
    config_data = load_config_data(Path(config_dir).parent / config_file)
    create_snapshots(now=now, dataset_names=set(config_data.keys()))

    delete_snapshots(config_data=config_data)

    logging.info("snapshot_manager done")


if __name__ == "__main__":
    main()
