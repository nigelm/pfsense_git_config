import pprint
from pathlib import Path
from typing import Any
from typing import Dict

import typer
import yaml
from loguru import logger
from typing_extensions import Annotated

from . import git_repo
from . import pfsense_configs

# -----------------------------------------------------------------------
app = typer.Typer()
state: Dict[str, Any] = {"verbose": False, "debug": False}


# -----------------------------------------------------------------------
def config_callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
    if value:
        logger.debug(f"Loading config file: {value}")
        try:
            with open(value) as f:  # Load config file
                conf = yaml.safe_load(f)
            ctx.default_map = ctx.default_map or {}  # Initialize the default map
            ctx.default_map.update(conf)  # Merge the config dict into default_map
        except FileNotFoundError:
            pass  # just let it go
    return value


# -----------------------------------------------------------------------
@app.callback()
def main(
    config: Annotated[str, typer.Option(callback=config_callback, is_eager=True)] = ".pfsense_git_configrc",
    debug: Annotated[bool, typer.Option(help="Output debug information.")] = False,
    verbose: Annotated[bool, typer.Option(help="Output verbose information.")] = False,
    config_dir: Annotated[Path, typer.Option()] = Path("/conf/backup"),
    git_dir: Annotated[Path, typer.Option()] = Path("."),
):
    """
    Common options for the app.
    """
    if debug:
        logger.debug("Will write debug output")
        state["debug"] = True
    if verbose:
        logger.debug("Will write verbose output")
        state["verbose"] = True
    if config_dir.is_dir():
        state["config_dir"] = config_dir
    else:
        typer.echo(f"config_dir must exist and be a directory - {config_dir}")
        raise typer.Exit(code=1)
    if git_dir.is_dir() and (git_dir / ".git").is_dir():
        state["git_dir"] = git_dir
    else:
        typer.echo(f"git_dir must exist and be a git directory - {git_dir}")
        raise typer.Exit(code=1)


# -----------------------------------------------------------------------
@app.command()
def test():
    logger.info("Run test")


# -----------------------------------------------------------------------
@app.command()
def git_config():
    config_set = pfsense_configs.read_configs(state["config_dir"])
    pprint.pp(config_set)
    git_repo.config_into_git_repo(config_set=config_set, git_dir=state["git_dir"])


# -----------------------------------------------------------------------
