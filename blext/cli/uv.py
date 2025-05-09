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

"""Implements a dummy-command for `blext uv`, to ensure this alias command shows up in `blext --help`."""

from ._context import APP


@APP.command(group='Aliases')
def uv() -> None:
	"""Alias to the default found `uv` executable."""
	msg = (
		"It shouldn't be possible to run this command directly. Please report this bug!"
	)
	raise RuntimeError(msg)
