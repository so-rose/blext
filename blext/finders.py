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
# - Find: Project Information
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


def find_proj_spec(proj_path: Path | None) -> Path:
	"""Locate the project specification using the given hint.

	Parameters:
		proj_path: Search for a `pyproject.toml` project specification at this path.
			When `None`, search in the current working directory.
	"""
	# Deduce Project Path
	match proj_path:
		case None:
			path_proj_spec = Path.cwd() / 'pyproject.toml'
		case p if p.exists() and p.is_file():
			path_proj_spec = proj_path
		case p if p.exists() and p.is_dir():
			path_proj_spec = proj_path / 'pyproject.toml'
		case p:
			msgs = [
				f'No Blender extension information could be found at the path `{p}`.',
				'Path must reference one of:',
				'- File (`pyproject.toml`): Must contain `[tool.blext]` fields.',
				'- Folder (w/`pyproject.toml`): Must contain a valid `pyproject.toml` file.',
				'- Script (`*.py`): Must contain `[tool.blext]` fields as "inline script metadata" (see <https://packaging.python.org/en/latest/specifications/inline-script-metadata/>).',
			]
			raise ValueError(*msgs)

	return path_proj_spec.resolve()


####################
# - Find: Executables
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
