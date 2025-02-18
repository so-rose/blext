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

from ._context import APP, CONSOLE

APP_SHOW = cyclopts.App(name='show', help='[Show] information about the extension.')
_ = APP.command(APP_SHOW)

APP_SHOW['--help'].group = 'Debug'
APP_SHOW['--version'].group = 'Debug'

__all__ = [
	'APP_SHOW',
	'CONSOLE',
]
