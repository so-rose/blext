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

import importlib.metadata
import platform
import shutil
from pathlib import Path

from blext import extyp


def detect_local_bl_platform() -> extyp.BLPlatform:
	"""Deduce the local Blender platform from `platform.system()` and `platform.machine()`.

	Warning:
		This method is reasoned through, not thoroughly tested.

	Returns:
		A local operating system supported by Blender, conforming to the format expected by Blender's extension manifest.

	Raises:
		ValueError: If a Blender-supported operating system could not be detected locally.

	References:
		- Possible Values from `uname -m`: <https://stackoverflow.com/questions/45125516/possible-values-for-uname-m>
		- Possible Values from `sys.platform`: https://stackoverflow.com/questions/446209/possible-values-from-sys-platform
	"""
	platform_system = platform.system().lower()
	platform_machine = platform.machine().lower()

	match (platform_system, platform_machine):
		case ('linux' | 'linux2', 'x86_64' | 'amd64'):
			return extyp.BLPlatform.linux_x64
		case ('linux' | 'linux2', arch) if arch.startswith(('aarch64', 'arm')):
			return extyp.BLPlatform.linux_arm64
		case ('darwin', 'x86_64' | 'amd64'):
			return extyp.BLPlatform.macos_x64
		case ('darwin', arch) if arch.startswith(('aarch64', 'arm')):
			return extyp.BLPlatform.macos_arm64
		case ('win32' | 'cygwin' | 'msys', 'x86_64' | 'amd64'):
			return extyp.BLPlatform.windows_x64
		case ('win32' | 'cygwin' | 'msys', arch) if arch.startswith(('aarch64', 'arm')):
			return extyp.BLPlatform.windows_arm64
		case _:
			msg = f"Could not detect a local operating system supported by Blender from 'platform.system(), platform.machine() = {platform_system}, {platform_machine}'"
			raise ValueError(msg)


def find_blender_exe() -> Path:
	"""Locate the Blender executable, using the current platform as a hint.

	Returns:
		Absolute path to a valid Blender executable, as a string.
	"""
	bl_platform = detect_local_bl_platform()
	match bl_platform:
		case extyp.BLPlatform.linux_x64 | extyp.BLPlatform.linux_arm64:
			blender_exe = shutil.which('blender')
			if blender_exe is not None:
				return Path(blender_exe)

			msg = "Couldn't find executable command 'blender' on the system PATH. Is it installed?"
			raise ValueError(msg)

		case extyp.BLPlatform.macos_arm64 | extyp.BLPlatform.macos_x64:
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

		case extyp.BLPlatform.windows_x64 | extyp.BLPlatform.windows_arm64:
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


def find_uv_exe() -> Path:
	"""Locate the `uv` executable.

	Parameters:
		search_venv: Search an active virtual environment based on the `VIRTUAL_ENV` env var.

	Returns:
		Absolute path to a valid `uv` executable.
	"""
	uv_files = importlib.metadata.files('uv')

	if uv_files is not None:
		uv_exe = None
		for package_path in uv_files:
			if package_path.name == 'uv' and package_path.parent.name == 'bin':
				located_uv_exe = package_path.locate()
				uv_exe = Path(located_uv_exe).resolve()
				break

		if uv_exe is not None and uv_exe.is_file():
			return uv_exe
		msgs = [
			'Could not locate a `uv` executable path on the filesystem.',
			'> This can happen if `blext` was installed in an unsupported manner, such that the files of its dependencies are not plain filesystem paths (user error).',
		]
		raise ValueError(*msgs)
	msg = "'uv' was not installed, even though it's a dependency of 'blext'. Please report this bug."
	raise RuntimeError(msg)
