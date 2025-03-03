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
import typing as typ
from pathlib import Path

import pydantic as pyd

from . import extyp, location


####################
# - Platform Information
####################
def detect_local_blplatform() -> extyp.BLPlatform:
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


####################
# - Executables
####################
def find_blender_exe(*, override_path_blender_exe: Path | None = None) -> Path:  # noqa: C901
	"""Locate the Blender executable, using the current platform as a hint.

	Returns:
		Absolute path to a valid Blender executable, as a string.
	"""
	if override_path_blender_exe is not None:
		blender_exe = override_path_blender_exe
		if blender_exe.exists():
			return blender_exe
		# TODO: Do more checks ex. is it executable?

		msg = f"Couldn't find Blender executable at specified path: {blender_exe}"
		raise ValueError(msg)

	bl_platform = detect_local_blplatform()
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


def find_uv_exe(
	*,
	search_venv: bool = True,
	override_path_uv_exe: Path | None = None,
) -> Path:
	"""Locate the `uv` executable.

	Parameters:
		search_venv: Search an active virtual environment based on the `VIRTUAL_ENV` env var.
		override_path_uv_exe: Override the path to search for a `uv` executable.

	Returns:
		Absolute path to a valid `uv` executable.
	"""
	if override_path_uv_exe is not None:
		uv_exe = override_path_uv_exe
		if uv_exe.exists():
			return uv_exe.resolve()

		msg = f"Couldn't find `uv` executable at specified path: {uv_exe}"
		raise ValueError(msg)

	if search_venv and 'VIRTUAL_ENV' in os.environ:
		path_venv = Path(os.environ['VIRTUAL_ENV'])
		path_uv = path_venv / 'bin' / 'uv'

		if path_uv.is_file():
			return path_uv.resolve()

	msg = "Could not find a 'uv' executable."
	raise ValueError(msg)


####################
# - Finder: Project Specification
####################
@typ.runtime_checkable
class GitInfo(typ.Protocol):
	"""An object that references a specific `git` repository and commit."""

	@property
	def url(self) -> str:  # pyright: ignore[reportReturnType]
		"""Link to the `git` repository."""

	@property
	def rev(self) -> str | None:
		"""Identifier for the commit in the `git` repository.

		Notes:
			When given, `self.tag` and `self.branch` must be `None`.
		"""

	@property
	def tag(self) -> str | None:
		"""Identifier for the tag in the `git` repository.

		Notes:
			When given, `self.rev` and `self.branch` must be `None`.
		"""

	@property
	def branch(self) -> str | None:
		"""Identifier for the branch in the `git` repository.

		Notes:
			When given, `self.rev` and `self.tag` must be `None`.
		"""

	@property
	def entrypoint(self) -> Path | None:
		"""Path to an extension specification file, relative to the repository root."""


def find_proj_spec(
	proj_uri: GitInfo | pyd.HttpUrl | Path | None,
	*,
	path_global_project_cache: Path,
	path_global_download_cache: Path,
) -> location.BLExtLocation:
	"""Locate the project specification.

	Parameters:
		proj_uri: Use to search for a project specification.

			- Current Project (`None -> **/pyproject.toml`): Search upwards for `pyproject.toml`, from current folder ({Path.cwd().resolve()}).
			- Project File (`pyproject.toml`): In the root folder of an extension project.
			- Project Folder (`*/pyproject.toml`): Folder containing a `pyproject.toml`.
			- Script File (`*.py`): Single-file extension.
			- Git URL: Local copy of repository containing `pyproject.toml`.
			- HTTP URL File: Local downloaded copy of a single-file extension.

		path_script_cache: Cache location to use for a single-file script extension.
		path_download_cache: Cache location to use for downloading extensions.

	Returns:
		Object specifying all paths needed to use/manage a Blender extension.

	Raises:
		ValueError: If no extension project could be located from `proj_uri`.

	See Also:
		- `blext.location.BLExtLocation`: Abstracts the discovery, creation, and use of paths associated with a particular Blender extension.

	References:
		- Inline Script Metadata: <https://packaging.python.org/en/latest/specifications/inline-script-metadata/#reference-implementation>
	"""
	match proj_uri:
		case Path() | None:
			return location.BLExtLocationPath(
				path=proj_uri,
				path_global_project_cache=path_global_project_cache,
				path_global_download_cache=path_global_download_cache,
			)

		case pyd.HttpUrl():
			return location.BLExtLocationHttp(
				url=proj_uri,
				path_global_project_cache=path_global_project_cache,
				path_global_download_cache=path_global_download_cache,
			)

		case GitInfo():
			return location.BLExtLocationGit(
				url=proj_uri.url,
				rev=proj_uri.rev,
				tag=proj_uri.tag,
				branch=proj_uri.branch,
				entrypoint=proj_uri.entrypoint,
				path_global_project_cache=path_global_project_cache,
				path_global_download_cache=path_global_download_cache,
			)

	msgs = [  # pyright: ignore[reportUnreachable]
		f'No Blender extension information could be found from the given URI "{proj_uri}".',
		'The following URIs are supported:',
		'- Current Project (`**/pyproject.toml`): Search upwards for `pyproject.toml`, from current folder ({Path.cwd().resolve()}).',
		'- Project File (`pyproject.toml`): In the root folder of an extension project.',
		'- Project Folder (`*/pyproject.toml`): Folder containing a `pyproject.toml`.',
		'- Script File (`*.py`): Single-file extension.',
		'- Git URL: Local copy of repository containing `pyproject.toml`.',
		'- HTTP URL File: Local downloaded copy of a single-file extension.',
	]
	raise ValueError(*msgs)
