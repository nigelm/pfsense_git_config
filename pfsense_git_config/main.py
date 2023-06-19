import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from loguru import logger
from typing_extensions import Annotated

from . import __version__
from . import pfsense_configs
from .git_repo import PfsenseGitRepo

# -----------------------------------------------------------------------
app = typer.Typer()  # app object


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
def version_callback(value: bool):
    if value:
        print(f"pfSense Git Config Version: {__version__}")
        raise typer.Exit()


# -----------------------------------------------------------------------
@app.command()
def pfsense_git_config(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, help="Report version"),
    ] = None,
    config: Annotated[
        str,
        typer.Option(callback=config_callback, is_eager=True, help="Configuration file", envvar="PGC_CONFIG"),
    ] = ".pfsense_git_configrc",
    verbose: Annotated[bool, typer.Option(help="Output verbose information.")] = False,
    pull: Annotated[bool, typer.Option(help="Pull the git repo before updating.")] = True,
    push: Annotated[bool, typer.Option(help="Push the git repo at the end.")] = True,
    config_dir: Annotated[
        Path,
        typer.Option(help="Location of the pfSense configs", envvar="PGC_PFSENSE_CONFIG_DIR"),
    ] = Path("/conf"),
    git_dir: Annotated[
        Path,
        typer.Option(
            help="Location of the git repo the pfSense config updates are to be stored in",
            envvar="PGC_GIT_DIR",
        ),
    ] = Path.home()
    / "pfsense_config",
):
    """
    Read pfSense configation changes, add them to a Git repo of config changes

    Reads the current pfsense configuration file (in `/conf/config.xml` by
    default), and the configuration backups
    (in `/conf/backup/config.<timestamp>.xml` by default) to contruct a set
    of timestamp config snapshots.  All of these that are more recent than
    the last timestamp in the git repo are written into the git repo, with
    their timestamps, in cronological order as one commit per config change.
    The revision description is used as the commit message.

    If `--pull` is specified (set by default), the git repo is pulled at the
    start of the process.

    If `--push` is specificed (set by default), the git repo is pushed to
    origin at the end of the process even if no updates are made.

    Remember that your pfsense configs should not be publically visible as
    they contain sensitive information about your network including hashed
    passwords stored within pfSense.

    """
    # deal with the options
    if verbose:
        logger.debug("Will write verbose output")
    else:
        logger.remove(0)  # replace default handler
        logger.add(sys.stderr, level="INFO")

    if not config_dir.is_dir():
        typer.echo(f"config_dir must exist and be a directory - {config_dir}")
        raise typer.Exit(code=1)

    if not (git_dir.is_dir() and (git_dir / ".git").is_dir()):
        typer.echo(f"git_dir must exist and be a non-bare git directory - {git_dir}")
        raise typer.Exit(code=1)

    # do the work...
    repo = PfsenseGitRepo(git_dir=git_dir)
    if pull:
        repo.pull()
    config_set = pfsense_configs.read_configs(config_dir, minimum_timestamp=repo.repo_timestamp)
    repo.configs_into_git_repo(config_set=config_set)
    if push:
        repo.push()


# -----------------------------------------------------------------------
