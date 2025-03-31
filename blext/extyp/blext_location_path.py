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

"""Implements `BLExtLocationPath`."""

import functools
from pathlib import Path

from blext.utils.search_in_parents import search_in_parents

from .blext_location import BLExtLocation


class BLExtLocationPath(BLExtLocation, frozen=True):
	"""Local filesystem location of a Blender extension.

	Attributes:
		path: Path to a Blender extension project.
			`None` indicates that the current working directory should be used.
	"""

	path: Path | None

	@functools.cached_property
	def path_spec(self) -> Path:
		"""Path to a file from which the extension specification can be loaded."""
		# Find Path to Project Spec
		## None: Search **/cwd() for 'pyproject.toml'
		if self.path is None:
			path_spec = search_in_parents(Path.cwd(), 'pyproject.toml')
			if path_spec is not None:
				return path_spec

			msgs = [
				f'No Blender extension could be found in the current directory "{Path().resolve()}".',
				'- Project Extension: `pyproject.toml` must exist in the current folder, or one of its (recursive) parents.',
			]
			raise ValueError(*msgs)

		## File: Check Support
		if self.path.is_file():
			if self.path.name.endswith('.py') or self.path.name == 'pyproject.toml':
				return self.path

			msgs = [
				f'No Blender extension could be found in the file "{self.path}".',
				'- Script Extensions: Only Python files (`*.py`) are supported.',
				'- Project Extensions: Only `pyproject.toml` files are supported.',
			]
			raise ValueError(*msgs)

		## Dir: Check dir/pyproject.toml
		if self.path.is_dir():
			path_spec = self.path / 'pyproject.toml'
			if path_spec.is_file():
				return path_spec

			msgs = [
				f'No Blender extension could be found within "{self.path}".',
				'- Project Extensions: Only `pyproject.toml` files are supported.',
			]
			raise ValueError(*msgs)

		## Error
		if not self.path.exists():
			msg = f"No Blender extension project could be found at '{self.path}', since the path doesn't exist."
			raise ValueError(msg)

		msg = f'No Blender extension project could be found at "{self.path}".'
		raise ValueError(msg)
