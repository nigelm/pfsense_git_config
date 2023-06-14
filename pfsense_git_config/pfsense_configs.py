from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

import defusedxml.ElementTree as ET
from loguru import logger


# -----------------------------------------------------------------------
def read_configs(config_dir: Path) -> List[Dict[str, Any]]:
    data: List[Dict[str, Any]] = []
    for config_file in config_dir.glob("*.xml"):
        logger.debug(f"Reading {config_file}")
        tree = ET.parse(config_file)
        root = tree.getroot()
        for elem in root:
            if elem.tag == "revision":
                datum = {"path": config_file, "name": config_file.name}
                for subelem in elem:
                    if subelem.tag == "time":
                        datum[subelem.tag] = int(subelem.text)
                    else:
                        datum[subelem.tag] = subelem.text
                logger.debug(f"result = {datum}")
                data.append(datum)

    return data


# -----------------------------------------------------------------------
