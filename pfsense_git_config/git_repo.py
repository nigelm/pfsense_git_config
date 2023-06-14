import shutil
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from loguru import logger


# -----------------------------------------------------------------------
def read_timestamp(git_dir: Path) -> Optional[int]:
    timestamp_file = git_dir / "timestamp"
    timestamp = None
    if timestamp_file.is_file():
        logger.debug(f"Found a timestamp file - {timestamp_file}")
        contents = timestamp_file.read_text()
        lines = contents.splitlines()
        try:
            timestamp = int(lines[0])
        except ValueError:
            pass
    return timestamp


# -----------------------------------------------------------------------
def write_timestamp(git_dir: Path, timestamp: int):
    timestamp_file = git_dir / "timestamp"
    timestamp_file.write_text(f"{timestamp}\n")


# -----------------------------------------------------------------------
def build_config_commit(config: Dict[str, Any], git_dir: Path):
    logger.debug(f"setting up to snapshot timestamp={config['time']}")
    write_timestamp(git_dir=git_dir, timestamp=config["time"])
    shutil.copyfile(config["path"], git_dir / "config.xml")


# -----------------------------------------------------------------------
def config_into_git_repo(config_set: List[Dict[str, Any]], git_dir: Path):
    latest_timestamp = read_timestamp(git_dir)
    for config in config_set:
        if latest_timestamp is None or latest_timestamp < config["time"]:
            build_config_commit(config, git_dir)
        else:
            logger.debug(f"skipping config timestamp={config['time']}")


# -----------------------------------------------------------------------
