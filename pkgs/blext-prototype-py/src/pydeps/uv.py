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


####################
# - UV Lock Management
####################
def update_uv_lock(
	path_uv_lock: Path,
	*,
	path_uv_exe: Path,
) -> None:
	"""Run `uv lock` within a `uv` project, which generates / update the lockfile `uv.lock`.

	Parameters:
		path_uv_lock: Where to generate the `uv.lock` file.
		path_uv_exe: Path to the `uv` executable.
	"""
	path_uv_lock = path_uv_lock.resolve()
	if path_uv_lock.name == 'uv.lock':
		with contextlib.chdir(path_uv_lock.parent):
			_ = subprocess.run(
				[str(path_uv_exe), 'lock'],
				check=True,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL,
			)
	elif path_uv_lock.name.endswith('.py.lock'):
		_ = subprocess.run(
			[
				str(path_uv_exe),
				'lock',
				'--script',
				str(path_uv_lock.parent / path_uv_lock.name.removesuffix('.lock')),
			],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
	else:
		msg = f"Couldn't find `uv.lock` file at {path_uv_lock}."
		raise ValueError(msg)


def parse_requirements_txt(
	path_uv_lock: Path,
	*,
	path_uv_exe: Path | None = None,
	include_hashes: bool = False,
	include_dev: bool = False,
	include_editable: bool = False,
	include_comment_header: bool = False,
) -> tuple[str, ...]:
	"""Get Python dependencies of a project as lines of a `requirements.txt` file.

	Notes:
		- Runs `uv export` with various options, under the hood.
		- Always runs with `--locked`, to ensure that `uv.lock` is unaltered by this function.

	Parameters:
		path_uv_lock: Where to generate the `uv.lock` file.
		path_uv_exe: Path to the `uv` executable.
		include_hashes: Include specific allowed wheel hashes in the generated `requirements.txt`.
		include_dev: Include dependencies marked as "development only".

			- In the context of extensions, development dependencies **should not** be included in the extension.
		include_editable: Include "editable" dependencies, for instance from local filesystem paths.
		include_comment_header: Include a comment describing how `uv` generated the file.
	"""
	# Find uv Executable
	path_uv_lock = path_uv_lock.resolve()

	# Lock UV
	uv_export_cmd_args = [
		*(['--no-dev'] if not include_dev else []),
		*(['--no-hashes'] if not include_hashes else []),
		*(['--no-editable'] if not include_editable else []),
		*(['--no-header'] if not include_comment_header else []),
		'--locked',
	]
	if path_uv_lock.name == 'uv.lock':
		with contextlib.chdir(path_uv_lock.parent):
			result = subprocess.run(
				[
					str(path_uv_exe),
					'export',
					*uv_export_cmd_args,
				],
				check=True,
				text=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.DEVNULL,
			)
	elif path_uv_lock.name.endswith('.py.lock'):
		result = subprocess.run(
			[
				str(path_uv_exe),
				'export',
				*uv_export_cmd_args,
				'--script',
				str(path_uv_lock.parent / path_uv_lock.name.removesuffix('.lock')),
			],
			check=True,
			text=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.DEVNULL,
		)
	else:
		msg = f"Couldn't find `uv.lock` file at {path_uv_lock}."
		raise ValueError(msg)

	return tuple(result.stdout.split('\n'))


def parse_uv_lock(
	path_uv_lock: Path,
	*,
	path_uv_exe: Path,
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
			update_uv_lock(
				path_uv_lock,
				path_uv_exe=path_uv_exe,
			)

		# Parse the Lockfile
		if path_uv_lock.is_file():
			with path_uv_lock.open('rb') as f:
				return deepfreeze(tomllib.load(f))  # pyright: ignore[reportAny]

		msg = f'Generating `{path_uv_lock}` failed, likely because it is not located within a valid `uv` project.'
		raise ValueError(msg)

	msg = f'The path `{path_uv_lock}` MUST refer to a file named `uv.lock`.'
	raise ValueError(msg)
