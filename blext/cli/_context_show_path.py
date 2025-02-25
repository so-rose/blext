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

import cyclopts

from ._context_show import APP_SHOW, CONSOLE

APP_SHOW_PATH = cyclopts.App(
	name='path', help='[Show] paths found by `blext`.', group='Subcommands'
)
_ = APP_SHOW.command(APP_SHOW_PATH)

APP_SHOW_PATH['--help'].group = 'Info'
APP_SHOW_PATH['--version'].group = 'Info'

__all__ = [
	'APP_SHOW_PATH',
	'CONSOLE',
]
