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

"""Tools for finding common information and files using platform-specific methods."""

from pathlib import Path


####################
# - Utilities
####################
def search_in_parents(path: Path, filename: str) -> Path | None:
	"""Search all parents of a path for a file.

	Notes:
		If `path` is a directory, then it is also searched for a file named `filename`.

	Parameters:
		path: The path to search the parents of.

	Returns:
		Absolute path to the found file, else `None` if no file was found.
	"""
	# No File Found
	if path == Path(path.root) or path == path.parent:
		return None

	# File Found
	if path.is_dir():
		file_path = path / filename
		if file_path.is_file():
			return file_path.resolve()

	# Recurse
	return search_in_parents(path.parent, filename)
