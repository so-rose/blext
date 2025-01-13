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

import platform
import shutil
from pathlib import Path

from .supported import BLPlatform


def detect_local_blplatform() -> BLPlatform:
	"""Deduce the local Blender platform from `platform.system()` and `platform.machine()`.

	References:
		Architecture Strings on Linus: <https://stackoverflow.com/questions/45125516/possible-values-for-uname-m>

	Warnings:
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
		case ('linux', 'x86_64' | 'amd64'):
			return BLPlatform.windows_x64
		case ('linux', arch) if arch.startswith(('aarch64', 'arm')):
			return BLPlatform.windows_arm64

	msg = "Could not detect a local operating system supported by Blender from 'platform.system(), platform.machine() = {platform_system}, {platform_machine}'"
	raise ValueError(msg)


def find_proj_spec(proj_path: Path | None) -> Path:
	"""Locate the project specification using the given hint.

	Parameters:
		proj_path: Search for a `pyproject.toml` project specification at this path.
			When `None`, search in the current working directory.
	"""
	if proj_path is None:
		path_proj_spec = Path.cwd() / 'pyproject.toml'
		if not path_proj_spec.is_file():
			symptom = (
				'does not exist' if not path_proj_spec.exists() else 'is not a file'
			)
			msg = "Couldn't find 'pyproject.toml' in the current working directory"

	elif proj_path.is_dir() and (proj_path / 'pyproject.toml').is_file():
		path_proj_spec = proj_path / 'pyproject.toml'

	elif not proj_path.is_file():
		symptom = 'does not exist' if not proj_path.exists() else 'is not a file'
		msg = f"Provided project specification {symptom} (tried to load '{proj_path}')"
		raise ValueError(msg)

	return path_proj_spec.resolve()


def find_blender_exe() -> str:
	"""Locate the Blender executable, using the current platform as a hint.

	Parameters:
		os: The currently supported operating system.

	Returns:
		Absolute path to a valid Blender executable, as a string.
	"""
	bl_platform = detect_local_blplatform()
	match bl_platform:
		case BLPlatform.linux_x64:
			blender_exe = shutil.which('blender')
			if blender_exe is not None:
				return blender_exe

			msg = "Couldn't find executable command 'blender' on the system PATH. Is it installed?"
			raise ValueError(msg)

		case BLPlatform.macos_arm64:
			blender_exe = '/Applications/Blender.app/Contents/MacOS/Blender'
			if Path(blender_exe).is_file():
				return blender_exe

			msg = f"Couldn't find Blender executable at standard path. Is it installed? (searched '{blender_exe}')"
			raise ValueError(msg)

		case BLPlatform.windows_x64:
			blender_exe = shutil.which('blender.exe')
			if blender_exe is not None:
				return blender_exe

			msg = "Couldn't find executable command 'blender.exe' on the system PATH. Is it installed?"
			raise ValueError(msg)

	msg = f"Could not detect a Blender executable for the current Blender platform '{bl_platform}'."
	raise ValueError(msg)
