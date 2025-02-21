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

"""Tools for managing wheel-based dependencies."""

import contextlib
import subprocess
import tomllib
import typing as typ
from pathlib import Path

from frozendict import deepfreeze, frozendict

from blext import finders


####################
# - UV Lock Management
####################
def update_uv_lock(path_uv_lock: Path) -> None:
	"""Run `uv lock` within a `uv` project, which generates / update the lockfile `uv.lock`.

	Parameters:
		path_uv_root: Path to the root directory of a `uv` project.
	"""
	# Find uv Executable
	path_uv = finders.find_uv_exe()

	# Lock UV
	if path_uv_lock.name == 'uv.lock':
		with contextlib.chdir(path_uv_lock.parent):
			_ = subprocess.run(
				[str(path_uv), 'lock'],
				check=True,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
			)
	elif path_uv_lock.name.endswith('.py.lock'):
		with contextlib.chdir(path_uv_lock.parent):
			_ = subprocess.run(
				[
					str(path_uv),
					'lock',
					'--script',
					path_uv_lock.parent / path_uv_lock.name.removesuffix('.lock'),
				],
				check=True,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
			)

	## TODO: Check whether the lockfile was updated just now


def parse_uv_lock(
	path_uv_lock: Path,
	*,
	force_update: bool = True,
) -> frozendict[str, typ.Any]:
	"""Parse a `uv.lock` file.

	Notes:
		A `uv.lock` file contains the platform-independent dependency resolution for a Python project managed with `uv`.
		By working directly with `uv`'s lockfiles, accessing data such as size, hash, and download URLs for wheels may be done in a lightweight manner, ex. without the need for a `venv`.

	Parameters:
		path_uv_lock: Path to the `uv` lockfile.
			If it doesn't exist, then it will be generated

	Returns:
		The dictionary parsed from `uv.lock`.
	"""
	if path_uv_lock.name == 'uv.lock' or path_uv_lock.name.endswith('.py.lock'):
		# Generate/Update the Lockfile
		## - By default, the lockfile is only generated if it doesn't (yet) exist.
		## - Otherwise, setting it requires a forced update.
		if force_update or not path_uv_lock.is_file():
			update_uv_lock(path_uv_lock)
		## TODO: More robust automatic mechanism, so we can set force_update=False with good conscience.

		# Parse the Lockfile
		if path_uv_lock.is_file():
			with path_uv_lock.open('rb') as f:
				return deepfreeze(tomllib.load(f))  # pyright: ignore[reportAny]

		msg = 'Generating `{path_uv_lock}` failed, likely because it is not located within a valid `uv` project.'
		raise ValueError(msg)
		## TODO: Check if it's a valid uv project first. Somehow? Another function?

	msg = 'The path `{path_uv_lock}` MUST refer to a file named `uv.lock`.'
	raise ValueError(msg)
