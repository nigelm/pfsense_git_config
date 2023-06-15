import datetime
import shutil
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytz
from git import Repo
from git.util import Actor
from loguru import logger


TZ = pytz.timezone("Europe/London")


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
def build_config_commit(config: Dict[str, Any], git_dir: Path, repo: Repo):
    logger.debug(f"setting up to snapshot timestamp={config['time']}")
    write_timestamp(git_dir=git_dir, timestamp=config["time"])
    shutil.copyfile(config["path"], git_dir / "config.xml")
    repo.index.add(["timestamp", "config.xml"])
    author_name, description = config["description"].split(": ", maxsplit=1)
    repo.index.commit(
        message=description,
        author_date=datetime.datetime.fromtimestamp(config["time"], tz=TZ),
        author=Actor(name=author_name, email="pfsense@example.com"),
    )


# -----------------------------------------------------------------------
def config_into_git_repo(config_set: List[Dict[str, Any]], git_dir: Path):
    latest_timestamp = read_timestamp(git_dir)
    repo = Repo(git_dir)
    for config in config_set:
        if latest_timestamp is None or latest_timestamp < config["time"]:
            build_config_commit(config, git_dir, repo)
        else:
            logger.debug(f"skipping config timestamp={config['time']}")
    logger.debug("pushing repo")
    repo.remotes.origin.push()


# -----------------------------------------------------------------------
