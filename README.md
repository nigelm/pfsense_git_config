# pfSense Git Config

Import pfSense config changes into a git repo.

## Current Version

Version: `0.4.4`

## Usage

Usage: `pfsense_git_config` [OPTIONS]

Read pfSense configation changes, add them to a Git repo of config changes

Reads the current pfsense configuration file (in `/conf/config.xml` by default),
and the configuration backups (in `/conf/backup/config-<timestamp>.xml` by
default) to contruct a set of timestamp config snapshots. All of these that are
more recent than the last timestamp in the git repo are written into the git
repo, with their timestamps, in cronological order as one commit per config
change. The revision description is used as the commit message.

If `--pull` is specified (set by default), the git repo is pulled at the start
of the process. If `--push` is specificed (set by default), the git repo is
pushed to origin at the end of the process even if no updates are made.

Remember that your pfsense configs should not be publically visible as they
contain sensitive information about your network including hashed passwords
stored within pfSense.

### Options

- `--version` - Report version
- `--config` - Configuration file `[env var: PGC_CONFIG]` Default
  .pfsense_git_config
- `--verbose` / `--no-verbose` - Output verbose information.
- `--pull` / `--no-pull` - Pull the git repo before updating (set by default)
- `--push` / `--no-push` - Push the git repo at the end (set by default)
- `--config-dir` - Directory with pfSense configurations
  `[env var: PGC_PFSENSE_CONFIG_DIR]` Default `/conf`
- `--git-dir` - Location of the git repo the pfSense config updates are to be
  stored in `[env var: PGC_GIT_DIR]` Default `~/pfsense_config`

## Installation and Setup

- Create a user account (with ssh access)
- Ensure that the Cron additional package is installed (required to run the
  checks regularly)
- Ensure that python and git are installed (this needs a root login session to
  use pkg install)
- Logged in to your user account:-
  - create a python venv - `python3.11 -m venv venv`
  - activate it - `source venv/bin/activate.csh`
  - install the package - `pip install --update pfsense_git_config`
  - create/clone a git repo in `~/pfsense_config` to put the configs into. The
    git repo should have a remote elsewhere - I use a local gitea instance.
    There should be a local ssh key or other authentication mechanism that
    allows push/pull to the remote.
  - run `pfsense_git_config`
  - add an invocation script - such as `run_pfsense_git_config.sh` form this
    repo
  - set up cron to run this regularly - say once or twice a day

---
