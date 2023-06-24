from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import defusedxml.ElementTree as ET
from loguru import logger


# -----------------------------------------------------------------------
def read_config(config_file: Path) -> Optional[Dict[str, Any]]:
    logger.debug(f"Reading {config_file}")
    tree = ET.parse(config_file)
    root = tree.getroot()
    datum: Optional[Dict[str, Any]] = None
    for elem in root:
        if elem.tag == "revision":
            datum = {"path": config_file, "name": config_file.name}
            for subelem in elem:
                if subelem.tag == "time":
                    datum[subelem.tag] = int(subelem.text)
                else:
                    datum[subelem.tag] = subelem.text
            logger.debug(f"result = {datum}")
    return datum


# -----------------------------------------------------------------------
def read_configs(config_dir: Path, minimum_timestamp: Optional[int] = None) -> List[Dict[str, Any]]:
    data: List[Dict[str, Any]] = []  # list of config files

    # read through the backup config files
    for config_file in config_dir.glob("backup/*.xml"):
        logger.debug(f"Examining {config_file}")
        try:
            timestamp = int(config_file.name.split("-", maxsplit=1)[1].split(".", maxsplit=1)[0])
            logger.debug(f"Timestamp is {timestamp}")
        except ValueError:
            timestamp = 0
        if minimum_timestamp is None or timestamp >= minimum_timestamp:
            datum = read_config(config_file)
            if datum:
                data.append(datum)

    # always read the curent active config
    datum = read_config(config_dir / "config.xml")
    if datum:
        data.append(datum)

    # make sure the records are sorted by time
    data.sort(key=lambda record: record["time"])
    return data


# -----------------------------------------------------------------------
