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
import functools
import subprocess
import sys
import time
import tomllib
import typing as typ
from pathlib import Path

import pydantic as pyd
import pypdl
import pypdl.utils
import rich
import rich.markdown
import rich.progress
import rich.prompt
import wheel_filename

from . import finders, supported

CONSOLE = rich.console.Console()

DELAY_DOWNLOAD_PROGRESS = 0.01
DOWNLOAD_DONE_THRESHOLD = 99

MANYLINUX_LEGACY_ALIASES = {
	'manylinux1_x86_64': 'manylinux_2_5_x86_64',
	'manylinux1_i686': 'manylinux_2_5_i686',
	'manylinux2010_x86_64': 'manylinux_2_12_x86_64',
	'manylinux2010_i686': 'manylinux_2_12_i686',
	'manylinux2014_x86_64': 'manylinux_2_17_x86_64',
	'manylinux2014_i686': 'manylinux_2_17_i686',
	'manylinux2014_aarch64': 'manylinux_2_17_aarch64',
	'manylinux2014_armv7l': 'manylinux_2_17_armv7l',
	'manylinux2014_ppc64': 'manylinux_2_17_ppc64',
	'manylinux2014_ppc64le': 'manylinux_2_17_ppc64le',
	'manylinux2014_s390x': 'manylinux_2_17_s390x',
}


####################
# - UV Management
####################
def _uv_lock(path_proj_root: Path) -> None:
	"""Run `uv lock` to generate / update the lockfile `uv.lock` for the given extension specification.

	Parameters:
		path_proj_root: Working directory for running `uv lock`.
	"""
	# Find uv Executable
	path_uv = finders.find_uv_exe()

	# Lock UV
	with contextlib.chdir(path_proj_root):
		# Generate uv.lock
		_ = subprocess.run(
			[str(path_uv), 'lock'],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)


def _uv_tree(path_proj_root: Path) -> str:
	"""Run `uv tree` to find the dependencies of the Blender extension package.

	This is a low-level method, used to filter which wheels to download.
	In particular, development dependencies are excluded.

	Parameters:
		path_proj_root: Working directory for running `uv tree`.

	Returns:
		A string guaranteed to contain the name of all packages that should be installed.
		The string's structure is not otherwise guaranteed.
	"""
	# Find uv Executable
	path_uv = finders.find_uv_exe()

	# Lock UV
	with contextlib.chdir(path_proj_root):
		# Retrieve Dependencies
		## - uv must declare which dependencies are NOT dev dependencies.
		return subprocess.check_output(
			[str(path_uv), 'tree', '--no-dev', '--locked'],
			stderr=subprocess.DEVNULL,
		).decode('utf-8')


def parse_lockfile(path_proj_root: Path) -> dict[str, typ.Any]:
	"""Parse the Blender extension's `uv.lock` file.

	The lockfile contains the platform-independent resolution.
	This may be directly accessed as URLs pointing at the exact wheels that must be downloaded.

	Parameters:
		path_proj_root: Directory to search for `uv.lock`.

	Returns:
		The dictionary parsed from `uv.lock`.
	"""
	# Update the Lockfile
	_uv_lock(path_proj_root)

	# Parse the Lockfile
	path_uv_lock = path_proj_root / 'uv.lock'
	if path_uv_lock.is_file():
		with path_uv_lock.open('rb') as f:
			return tomllib.load(f)

	msg = f"Couldn't find or create 'uv.lock' in project root '{path_proj_root}'"
	raise ValueError(msg)


####################
# - Wheel Management
####################
class BLExtWheel(pyd.BaseModel, frozen=True):
	"""A Python dependency needed by a Blender extension."""

	url: pyd.HttpUrl | None = None
	path: Path | None = None

	hash: str | None = None
	size: pyd.ByteSize | None = None

	@functools.cached_property
	def filename(self) -> str:
		"""Parse the filename of the wheel file."""
		if self.url is not None:
			if self.url.path is not None:
				url_parts = self.url.path.split('/')
				if url_parts[-1].endswith('.whl'):
					return url_parts[-1]

			msg = f"Wheel filename could not be found in URL '{self.url}'"
			raise RuntimeError(msg)

		if self.path is not None:
			return self.path.name

		msg = f'BLExtWheel has neither a URL or a Path: {self}'
		raise RuntimeError(msg)

	####################
	# - Wheel Filename Parsing
	####################
	@functools.cached_property
	def _parsed_wheel_filename(self) -> wheel_filename.ParsedWheelFilename:
		"""Parse the wheel filename for information.

		Raises:
			InvalidFilenameError: Subclass of `ValueError`.
				Thrown when `self.filename` is an invalid wheel filename.
		"""
		return wheel_filename.parse_wheel_filename(self.filename)

	@property
	def project(self) -> str:
		"""The name of the project represented by the wheel.

		Name is normalized to use '_' instead of '-'.
		"""
		return (
			self._parsed_wheel_filename.project.replace('-', '_')
			.replace('.', '_')
			.lower()
		)

	@property
	def version(self) -> str:
		"""The version of the project represented by the wheel."""
		return self._parsed_wheel_filename.version

	@property
	def build(self) -> str | None:
		"""The build-tag of the project represented by the wheel, if any."""
		return self._parsed_wheel_filename.build

	@property
	def python_tags(self) -> frozenset[str]:
		"""The Python tags of the wheel."""
		return frozenset(self._parsed_wheel_filename.python_tags)

	@property
	def abi_tags(self) -> frozenset[str]:
		"""The ABI tags of the wheel."""
		return frozenset(self._parsed_wheel_filename.abi_tags)

	@property
	def platform_tags(self) -> frozenset[str]:
		"""The platform tags of the wheel."""
		return frozenset(self._parsed_wheel_filename.platform_tags)

	def glibc_version(self, platform_tag: str) -> tuple[int, int] | None:
		"""The GLIBC version that this wheel was compiled with.

		Examine all the supported GLIBC versions specified by platform tags, then select the smallest one.
		"""
		if platform_tag in self.platform_tags:
			platform_tag = MANYLINUX_LEGACY_ALIASES.get(platform_tag, platform_tag)

			if platform_tag.startswith('manylinux_'):
				version_elements = platform_tag.split('_')
				return (
					int(version_elements[1]),
					int(version_elements[2]),
				)
		return None

	def macos_version(self, platform_tag: str) -> tuple[int, int] | None:
		"""The platform tags of the wheel."""
		if platform_tag in self.platform_tags and platform_tag.startswith('macosx'):
			version_elements = platform_tag.split('_')
			return (
				int(version_elements[1]),
				int(version_elements[2]),
			)
		return None

	####################
	# - Match BLPlatform
	####################
	def get_compatible_bl_platforms(
		self,
		*,
		valid_python_tags: frozenset[str],
		valid_abi_tags: frozenset[str],
		min_glibc_version: tuple[int, int],
		min_macos_version: tuple[int, int],
	) -> frozenset[supported.BLPlatform | None]:
		is_python_version_valid = len(valid_python_tags & self.python_tags) > 0
		is_abi_valid = len(valid_abi_tags & self.abi_tags) > 0

		supported_bl_platforms: set[supported.BLPlatform] = set()
		accepted_platform_tags: set[str] = set()
		rejected_platform_tags: set[str] = set()
		if is_python_version_valid and is_abi_valid:
			if 'any' in self.platform_tags:
				return frozenset(bl_platform for bl_platform in supported.BLPlatform)

			for platform_tag in self.platform_tags:
				macos_version = self.macos_version(platform_tag)
				glibc_version = self.glibc_version(platform_tag)

				# Windows
				if platform_tag.startswith('win'):
					bl_platform = {
						'win32': supported.BLPlatform.windows_x64,
						'win_amd64': supported.BLPlatform.windows_x64,
						'win_arm32': None,
						'win_arm64': supported.BLPlatform.windows_arm64,
					}.get(platform_tag)

					if bl_platform is not None:
						supported_bl_platforms.add(bl_platform)
						accepted_platform_tags.add(platform_tag)
					else:
						rejected_platform_tags.add(platform_tag)

				# Mac
				elif macos_version is not None and (
					macos_version[0] < min_macos_version[0]
					or (
						macos_version[0] == min_macos_version[0]
						and macos_version[1] <= min_macos_version[1]
					)
				):
					for bl_platform in [
						supported.BLPlatform.macos_x64,
						supported.BLPlatform.macos_arm64,
					]:
						if any(
							platform_tag.endswith(pypi_arch)
							for pypi_arch in bl_platform.pypi_arches
						):
							supported_bl_platforms.add(bl_platform)
							accepted_platform_tags.add(platform_tag)
						else:
							rejected_platform_tags.add(platform_tag)

				# Linux
				elif glibc_version is not None and (
					glibc_version[0] < min_glibc_version[0]
					or (
						glibc_version[0] == min_glibc_version[0]
						and glibc_version[1] <= min_glibc_version[1]
					)
				):
					for bl_platform in [
						supported.BLPlatform.linux_x64,
						supported.BLPlatform.linux_arm64,
					]:
						if any(
							platform_tag.endswith(pypi_arch)
							for pypi_arch in bl_platform.pypi_arches
						):
							supported_bl_platforms.add(bl_platform)
							accepted_platform_tags.add(platform_tag)
						else:
							rejected_platform_tags.add(platform_tag)

		return frozenset(supported_bl_platforms)


def parse_all_packages(path_proj_root: Path) -> tuple[dict[str, typ.Any], ...]:
	"""Parse all required dependencies, for each of which there must be one wheel available per supported platform."""
	# Parse Dependencies and Packages
	uv_lock = parse_lockfile(path_proj_root)
	uv_tree_str = _uv_tree(path_proj_root)

	return tuple(
		[
			package
			for package in uv_lock['package']
			if 'name' in package
			and package['name'] in uv_tree_str
			and not (
				'source' in package
				and 'virtual' in package['source']
				and package['source']['virtual'] == '.'
			)
		]
	)


def parse_all_package_names(path_proj_root: Path) -> list[str]:
	return [
		package['name'].replace('-', '_')
		for package in parse_all_packages(path_proj_root)
	]


def parse_all_possible_wheels(path_proj_root: Path) -> set[BLExtWheel]:
	"""Deduce the filenames and URLs of the desired wheels."""
	packages = parse_all_packages(path_proj_root)

	# Parse Wheels: URL
	wheels_url = {
		BLExtWheel(
			url=wheel_info['url'],
			hash=wheel_info.get('hash'),
			size=wheel_info.get('size'),
		)
		for package in packages
		for wheel_info in package.get('wheels', [])
		if (
			'source' in package
			and 'registry' in package['source']
			and 'url' in wheel_info
		)
	}
	wheels_path_editable = {
		BLExtWheel(
			path=package['source']['editable'].resolve(),
		)
		for package in packages
		if ('source' in package and 'editable' in package['source'])
	}
	wheels_path_directory = {
		BLExtWheel(
			path=package['source']['directory'].resolve(),
		)
		for package in packages
		if ('source' in package and 'directory' in package['source'])
	}

	return wheels_url | wheels_path_editable | wheels_path_directory


####################
# - Wheel Download
####################
def download_wheels(
	wheels: frozenset[BLExtWheel],
	*,
	path_wheels: Path,
	no_prompt: bool = False,
) -> None:
	"""Download universal and binary wheels for all platforms defined in `pyproject.toml`.

	Each blender-supported platform requires specifying a valid list of PyPi platform constraints.
	These will be used as an allow-list when deciding which binary wheels may be selected for ex. 'mac'.

	It is recommended to start with the most compatible platform tags, then work one's way up to the newest.
	Depending on how old the compatibility should stretch, one may have to omit / manually compile some wheels.

	There is no exhaustive list of valid platform tags - though this should get you started:
	- https://stackoverflow.com/questions/49672621/what-are-the-valid-values-for-platform-abi-and-implementation-for-pip-do
	- Examine https://pypi.org/project/pillow/#files for some widely-supported tags.

	Parameters:
		blext_spec: The extension specification to pack the zip file base on.
		bl_platform: The Blender platform to get wheels for.
		no_prompt: Don't protect wheel deletion with an interactive prompt.
	"""
	path_wheels = path_wheels.resolve()
	wheel_paths_current = frozenset(
		{path_wheel.resolve() for path_wheel in path_wheels.rglob('*.whl')}
	)

	# Compute Wheel Diff
	## - Missing: Will be downloaded.
	## - Superfluous: Will be deleted.
	wheels_to_download = {
		path_wheels / wheel.filename: wheel
		for wheel in wheels
		if path_wheels / wheel.filename not in wheel_paths_current
		and wheel.url is not None
	}
	wheel_paths_to_delete = wheel_paths_current - frozenset(
		{path_wheels / wheel.filename for wheel in wheels}
	)
	## TODO: Check hash of existing wheels.

	# Delete Superfluous Wheels
	CONSOLE.print()
	CONSOLE.rule('[bold green]Wheels to Download')
	if wheels_to_download:
		CONSOLE.print(f'[italic]Downloading to: {path_wheels}')
		CONSOLE.print(
			rich.markdown.Markdown(
				'\n'.join(
					[
						f'- {wheel_path_to_download.relative_to(path_wheels)}'
						for wheel_path_to_download in wheels_to_download
					]
				)
			),
		)
		CONSOLE.print()

	CONSOLE.print()
	CONSOLE.rule('[bold green]Wheels to Delete')
	if wheel_paths_to_delete:
		CONSOLE.print(f'[italic]Deleting from: {path_wheels}:')
		CONSOLE.print(
			rich.markdown.Markdown(
				'\n'.join(
					[
						f'- {wheel_path_to_delete.relative_to(path_wheels)}'
						for wheel_path_to_delete in wheel_paths_to_delete
					]
				)
			),
		)
		CONSOLE.print()

		if not no_prompt:
			if rich.prompt.Confirm.ask('[bold]OK to delete?'):
				for path_wheel in wheel_paths_to_delete:
					if path_wheel.is_file() and path_wheel.name.endswith('.whl'):
						path_wheel.unlink()
					else:
						msg = f"While deleting superfluous wheels, a wheel path was computed that doesn't point to a valid .whl wheel: {path_wheel}"
						raise RuntimeError(msg)
			else:
				CONSOLE.print('[italic]Aborting...[/italic]')
				sys.exit(1)

	# Download Missing Wheels
	if wheels_to_download:
		CONSOLE.print()
		CONSOLE.rule('[bold green]Wheels to Download')
		CONSOLE.print(f'[italic]Downloading to: {path_wheels}')
		CONSOLE.print(
			rich.markdown.Markdown(
				'\n'.join(
					[
						f'- {wheel_to_download}'
						for wheel_to_download in wheels_to_download
					]
				)
			),
		)
		CONSOLE.print()

		# Start Download
		dl_tasks = [
			{
				'url': str(wheel.url),
				'file_path': str(path_wheel),
			}
			for path_wheel, wheel in wheels_to_download.items()
		]
		if dl_tasks:
			dl = pypdl.Pypdl(  # pyright: ignore[reportPrivateLocalImportUsage]
				max_concurrent=8,
				allow_reuse=False,
			)
			dl_promise: pypdl.utils.EFuture = dl.start(  # pyright: ignore[reportUnknownMemberType, reportAssignmentType]
				tasks=dl_tasks,
				retries=3,
				display=False,
				block=False,
			)

			# Monitor Download w/Progress Bar
			with rich.progress.Progress() as progress:
				task = progress.add_task('Downloading...', total=100)

			# Wait for Download to Start
			while dl.progress is None:
				time.sleep(DELAY_DOWNLOAD_PROGRESS)

			# Monitor Download
			## - 99% seems to be the maximum value.
			while dl.progress < DOWNLOAD_DONE_THRESHOLD:
				progress.update(task, completed=dl.progress)
				time.sleep(DELAY_DOWNLOAD_PROGRESS)

			# Stop the Download @ 99%
			## - Essentially, we must wait on the future from the started download.
			## - This also merges the downloaded segments and cleans up.
			_ = dl_promise.result()

			# Finalize Progress Bar to 100%
			progress.update(task, completed=100)

		## TODO: Reimplement for locally built wheels w/Copy
		# copy_tasks = [
		# {
		# 'from': wheel_path,
		# 'to': blext_spec.path_wheels / wheel_filename,
		# }
		# for wheel_filename, wheel_path in wheel_target_urls.items()
		# if wheel_filename in wheels_to_download and isinstance(wheel_path, Path)
		# ]
		# for copy_task in copy_tasks:
		# shutil.copyfile(str(copy_task['from']), str(copy_task['to']))
