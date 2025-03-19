# blext
# Copyright (C) 2025 blext Project Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Shared context for `blext` commands."""

import importlib.metadata
import typing as typ
from pathlib import Path

import cyclopts
import platformdirs
import rich
import rich.theme

from blext import ui

####################
# - Constants
####################
__version__ = importlib.metadata.version('blext')

CMDS_GROUP = cyclopts.Group('Commands', sort_key=0)
SUBCMDS_GROUP = cyclopts.Group('Subcommands', sort_key=1)
HELP_GROUP = cyclopts.Group('Help', sort_key=2)

CONFIG_GROUP = cyclopts.Group('Global', sort_key=100)
PARAMS_GROUP = cyclopts.Group('Options', sort_key=20)

DEFAULT_BLEXT_INFO = ui.BLExtInfo()
DEFAULT_CONFIG = ui.GlobalConfig()

####################
# - Parameter Types
####################
ParameterProj: typ.TypeAlias = typ.Annotated[
	str | None,
	cyclopts.Parameter(
		group=ui.LOCATION_GROUP,
		help="""Location specifier for `blext` projects.
- **Path** (detect):  `<path>`
- **Path** (script):  `script+<path>`
- **Path** (project): `project+<path>`
- **Path** (packed):  `packed+<path>`
- **URL** (detect):   `<http_url>`
- **URL** (script):   `script+<http_url>`
- **URL** (project):  `project+<http_url>`
- **URL** (packed):   `packed+<http_url>`
- **git** (detect):   `git+<git_uri>`""",
	),
]
ParameterBLExtInfo: typ.TypeAlias = typ.Annotated[
	ui.BLExtInfo,
	cyclopts.Parameter(name='*'),
]
ParameterConfig: typ.TypeAlias = typ.Annotated[
	ui.GlobalConfig,
	cyclopts.Parameter(name='cfg', group=CONFIG_GROUP),
]
####################
# - Console
####################
CONSOLE = rich.console.Console(
	tab_size=4,
	theme=rich.theme.Theme(
		styles={
			'markdown.code': 'italic dim',
			'cyan': 'green',
		}
	),
)


####################
# - App
####################
APP = cyclopts.App(
	name='blext',
	help='`blext` simplifies making Blender extensions.',
	help_format='markdown',
	console=CONSOLE,
	version=__version__,
	version_format='plaintext',
	default_parameter=cyclopts.Parameter(
		show_env_var=False,
	),
	group_arguments=PARAMS_GROUP,
	group_parameters=PARAMS_GROUP,
	group_commands=CMDS_GROUP,
	config=[
		# 0. CLI Arguments (Implicit)
		# 1. Env Vars
		cyclopts.config.Env(
			prefix='BLEXT_',
			command=True,
		),
		# 2. Global Config
		cyclopts.config.Toml(
			path=Path(
				platformdirs.user_config_dir(
					ui.APPNAME,
					ui.APPAUTHOR,
					ensure_exists=True,
				)
			)
			/ 'config.toml',
			root_keys=(),
			must_exist=False,
			search_parents=False,
			allow_unknown=False,
			use_commands_as_keys=False,
		),
	],
)
APP['--help'].group = HELP_GROUP
APP['--version'].group = HELP_GROUP
