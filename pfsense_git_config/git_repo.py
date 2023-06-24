import datetime
import html
import re
import shutil
from dataclasses import dataclass
from dataclasses import field
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
@dataclass
class PfsenseGitRepo:
    git_dir: Path
    repo: Repo = field(init=False)
    repo_timestamp: Optional[int] = field(init=False)
    repo_timestamp_path: Path = field(init=False)
    repo_timestamp_filename: str = "timestamp"
    commit_email: str = "pfsense@example.com"
    tz: datetime.tzinfo = TZ

    # -----------------------------------------------------------------------
    def __post_init__(self):
        self.repo = Repo(self.git_dir)
        self.repo_timestamp_path = self.git_dir / self.repo_timestamp_filename
        self.read_timestamp()

    # -----------------------------------------------------------------------
    def read_timestamp(self):
        timestamp: Optional[int] = None
        if self.repo_timestamp_path.is_file():
            logger.debug(f"Found a timestamp file - {self.repo_timestamp_path}")
            contents = self.repo_timestamp_path.read_text()
            lines = contents.splitlines()
            try:
                timestamp = int(lines[0])
            except ValueError:
                pass
        self.repo_timestamp = timestamp

    # -----------------------------------------------------------------------
    def write_timestamp(self):
        self.repo_timestamp_path.write_text(f"{self.repo_timestamp}\n")

    # -----------------------------------------------------------------------
    def set_timestamp(self, timestamp: int):
        self.repo_timestamp = timestamp
        self.write_timestamp()

    # -----------------------------------------------------------------------
    def config_author(self, config: Dict[str, Any]) -> Actor:
        author = html.unescape(config["username"])
        match = re.match(r"[a-zA-Z0-9_\.-]+@[a-zA-Z0-9_\.:-]+", author)
        if match:
            author = match[0]
        return Actor(name=author, email=self.commit_email)

    # -----------------------------------------------------------------------
    def build_config_commit(self, config: Dict[str, Any]):
        logger.debug(f"setting up to snapshot timestamp={config['time']}")
        self.set_timestamp(timestamp=config["time"])
        shutil.copyfile(config["path"], self.git_dir / "config.xml")
        self.repo.index.add(["timestamp", "config.xml"])
        author = self.config_author(config)
        description = config["description"].removeprefix(config["username"] + ": ")
        commit_timestamp = datetime.datetime.fromtimestamp(config["time"], tz=self.tz)
        self.repo.index.commit(
            message=html.unescape(description),
            author_date=commit_timestamp,
            commit_date=commit_timestamp,
            author=author,
            committer=author,
        )

    # -----------------------------------------------------------------------
    def configs_into_git_repo(self, config_set: List[Dict[str, Any]]):
        for config in config_set:
            if self.repo_timestamp is None or self.repo_timestamp < config["time"]:
                self.build_config_commit(config)
            else:
                logger.debug(f"skipping config timestamp={config['time']}")

    # -----------------------------------------------------------------------
    def push(self):
        self.repo.remotes.origin.push()

    # -----------------------------------------------------------------------
    def pull(self):
        self.repo.remotes.origin.pull()
        self.read_timestamp()

    # -----------------------------------------------------------------------


# -----------------------------------------------------------------------
