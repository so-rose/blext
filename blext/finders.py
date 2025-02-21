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

import os
import platform
import shutil
from pathlib import Path

from .supported import BLPlatform


####################
# - Project Information
####################
def search_parents(path: Path, filename: str) -> Path | None:
	"""Search all parents of a path for a file.

	Notes:
		The input `path` is itself searched for the filename, but only if it is a directory.

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
	return search_parents(p.parent, filename)


def find_proj_spec(proj_path: Path | None) -> Path:
	"""Locate the project specification by scanning the given project path.

	Parameters:
		proj_path: Use to search for a project specification.
			May refer to any of:

			- File (`pyproject.toml`): Must contain `[tool.blext]` fields.'
			- Script (`*.py`): Must contain `[tool.blext]` fields as "inline script metadata".'
			- Folder (w/`pyproject.toml`): Must contain a valid `pyproject.toml` file.'
			'- `None`: Will search upwards for `pyproject.toml` from the current folder ({Path.cwd()}).'

	Returns:
		The path to a file that **might** support a `blext` project specificaiton.

	Raises:
		ValueError: If no project specificaiton can be found.

	References:
		- Inline Script Metadata: <https://packaging.python.org/en/latest/specifications/inline-script-metadata/#reference-implementation>
	"""
	# Search for Project Specification
	if proj_path is None:
		path_proj_spec = search_parents(Path.cwd(), 'pyproject.toml')
	elif proj_path.is_file() and (
		proj_path.name.endswith('.py') or proj_path.name == 'pyproject.toml'
	):
		path_proj_spec = proj_path
	elif proj_path.is_dir():
		path_proj_spec = proj_path / 'pyproject.toml'
	else:
		path_proj_spec = None

	# Found Project Spec
	if path_proj_spec is not None:
		return path_proj_spec.resolve()

	msgs = [
		f'No Blender extension information could be found from the given path "{proj_path}".',
		'Path must be one of:',
		'- File (`pyproject.toml`): Must contain `[tool.blext]` fields.',
		'- Script (`*.py`): Must contain `[tool.blext]` fields as "inline script metadata".',
		'- Folder (w/`pyproject.toml`): Must contain a valid `pyproject.toml` file.',
		f'- `None`: Will search upwards for `pyproject.toml` from the current folder ({Path.cwd()}).',
	]
	raise ValueError(*msgs)


####################
# - Platform Information
####################
def detect_local_blplatform() -> BLPlatform:
	"""Deduce the local Blender platform from `platform.system()` and `platform.machine()`.

	References:
		Architecture Strings on Linus: <https://stackoverflow.com/questions/45125516/possible-values-for-uname-m>

	Warning:
		This method is mostly untested, especially on Windows.

	Returns:
		A local operating system supported by Blender, conforming to the format expected by Blender's extension manifest.

	Raises:
		ValueError: If a Blender-supported operating system could not be detected locally.
	"""
	platform_system = platform.system().lower()
	platform_machine = platform.machine().lower()

	match (platform_system, platform_machine):
		case ('linux', 'x86_64' | 'amd64'):
			return BLPlatform.linux_x64
		case ('linux', arch) if arch.startswith(('aarch64', 'arm')):
			return BLPlatform.linux_arm64
		case ('darwin', 'x86_64' | 'amd64'):
			return BLPlatform.macos_x64
		case ('darwin', arch) if arch.startswith(('aarch64', 'arm')):
			return BLPlatform.macos_arm64
		case ('windows', 'x86_64' | 'amd64'):
			return BLPlatform.windows_x64
		case ('windows', arch) if arch.startswith(('aarch64', 'arm')):
			return BLPlatform.windows_arm64
		case _:
			msg = "Could not detect a local operating system supported by Blender from 'platform.system(), platform.machine() = {platform_system}, {platform_machine}'"
			raise ValueError(msg)


####################
# - Executables
####################
def find_blender_exe() -> Path:
	"""Locate the Blender executable, using the current platform as a hint.

	Returns:
		Absolute path to a valid Blender executable, as a string.
	"""
	bl_platform = detect_local_blplatform()
	match bl_platform:
		case BLPlatform.linux_x64 | BLPlatform.linux_arm64:
			blender_exe = shutil.which('blender')
			if blender_exe is not None:
				return Path(blender_exe)

			msg = "Couldn't find executable command 'blender' on the system PATH. Is it installed?"
			raise ValueError(msg)

		case BLPlatform.macos_arm64 | BLPlatform.macos_x64:
			# Search PATH: 'blender'
			blender_exe = shutil.which('blender')
			if blender_exe is not None:
				return Path(blender_exe)

			# Search Applications
			blender_exe = Path('/Applications/Blender.app/Contents/MacOS/Blender')
			if blender_exe.is_file():
				return blender_exe

			msg = "Couldn't find Blender executable (tried searching for 'blender' on the system path, and at '/Applications/Blender.app/Contents/MacOS/Blender'). Is it installed?"
			raise ValueError(msg)

		case BLPlatform.windows_x64 | BLPlatform.windows_arm64:
			# Search PATH: 'blender'
			blender_exe = shutil.which('blender')
			if blender_exe is not None:
				return Path(blender_exe)

			# Search PATH: 'blender.exe'
			blender_exe = shutil.which('blender.exe')
			if blender_exe is not None:
				return Path(blender_exe)

			msg = "Couldn't find executable command 'blender' or 'blender.exe' on the system PATH. Is Blender installed?"
			raise ValueError(msg)


def find_uv_exe(search_venv: bool = True) -> Path:
	"""Locate the `uv` executable.

	Returns:
		Absolute path to a valid Blender executable, as a string.
	"""
	if search_venv and 'VIRTUAL_ENV' in os.environ:
		path_venv = Path(os.environ['VIRTUAL_ENV'])
		path_uv = path_venv / 'bin' / 'uv'

		if path_uv.is_file():
			return path_uv

	msg = "Could not find a 'uv' executable."
	raise ValueError(msg)
