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

"""Defines an abstraction for a Blender extension wheel."""

import functools
import hashlib
import typing as typ
from pathlib import Path

import pydantic as pyd
import wheel_filename
from frozendict import frozendict

from blext import extyp

MANYLINUX_LEGACY_ALIASES: frozendict[str, str] = frozendict(
	{
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
)

WIN_PLATFORM_TAGS_TO_BL_PLATFORMS = {
	'win32': extyp.BLPlatform.windows_x64,
	'win_amd64': extyp.BLPlatform.windows_x64,
	'win_arm32': None,
	'win_arm64': extyp.BLPlatform.windows_arm64,
}


####################
# - Wheel Management
####################
class BLExtWheel(pyd.BaseModel, frozen=True):
	"""Representation of a Python dependency."""

	url: pyd.HttpUrl

	hash: str | None
	size: pyd.ByteSize | None = None

	@functools.cached_property
	def filename(self) -> str:
		"""Parse the filename of the wheel file."""
		if self.url.path is not None:
			url_parts = self.url.path.split('/')
			if url_parts[-1].endswith('.whl'):
				return url_parts[-1]

		msg = f"Wheel filename could not be found in URL '{self.url}'"
		raise RuntimeError(msg)

	####################
	# - Parsed Properties
	####################
	@functools.cached_property
	def _parsed_wheel_filename(self) -> wheel_filename.ParsedWheelFilename:
		"""Parse the wheel filename for information.

		Raises:
			InvalidFilenameError: Subclass of `ValueError`.
				Thrown when `self.filename` is an invalid wheel filename.
		"""
		return wheel_filename.parse_wheel_filename(self.filename)

	@functools.cached_property
	def project(self) -> str:
		"""The name of the project represented by the wheel.

		Name is normalized to use '_' instead of '-'.
		"""
		return (
			self._parsed_wheel_filename.project.replace('-', '_')
			.replace('.', '_')
			.lower()
		)

	@functools.cached_property
	def version(self) -> str:
		"""The version of the project represented by the wheel."""
		return self._parsed_wheel_filename.version

	@functools.cached_property
	def build(self) -> str | None:
		"""The build-tag of the project represented by the wheel, if any."""
		return self._parsed_wheel_filename.build

	@functools.cached_property
	def python_tags(self) -> frozenset[str]:
		"""The Python tags of the wheel."""
		return frozenset(self._parsed_wheel_filename.python_tags)

	@functools.cached_property
	def abi_tags(self) -> frozenset[str]:
		"""The ABI tags of the wheel."""
		return frozenset(self._parsed_wheel_filename.abi_tags)

	@functools.cached_property
	def platform_tags(self) -> frozenset[str]:
		"""The platform tags of the wheel.

		Notes:
			Legacy `manylinux` tags (such as `2014`) are normalized to their
			explicit `PEP600` equivalents (ex. `2014 -> 2_17`).

			This is done to avoid irregularities in how `glibc` versions are parsed
			for `manylinux` wheels in later methods.

		See Also:
			- `PEP600`: https://peps.python.org/pep-0600/

		"""
		return frozenset(
			{
				MANYLINUX_LEGACY_ALIASES.get(platform_tag, platform_tag)
				for platform_tag in self._parsed_wheel_filename.platform_tags
				if not (
					platform_tag in MANYLINUX_LEGACY_ALIASES
					and MANYLINUX_LEGACY_ALIASES[platform_tag]
					in self._parsed_wheel_filename.platform_tags
				)
			}
		)

	####################
	# - Platform Information
	####################
	@functools.cached_property
	def glibc_versions(self) -> frozendict[str, tuple[int, int] | None]:
		"""Minimum GLIBC versions supported by this wheel.

		Notes:
			- The smallest available GLIBC version indicates the minimum GLIBC support for this wheel.
			- Non-`manylinux` platform tags will always map to `None`.
		"""
		return frozendict(
			{
				platform_tag: tuple(
					int(glibc_version_part)
					for glibc_version_part in platform_tag.removeprefix(
						'manylinux_'
					).split('_')[:2]
				)
				if platform_tag.startswith('manylinux_')
				else None
				for platform_tag in self.platform_tags
			}
		)

	@functools.cached_property
	def macos_versions(self) -> frozendict[str, tuple[int, int] | None]:
		"""Minimum MacOS versions supported by this wheel.

		Notes:
			- The smallest available MacOS version indicates the minimum GLIBC support for this wheel.
			- Non-`macosx` platform tags will always map to `None`.
		"""
		return frozendict(
			{
				platform_tag: tuple(
					int(macos_version_part)
					for macos_version_part in platform_tag.removeprefix(
						'macosx_'
					).split('_')[:2]
				)
				if platform_tag.startswith('macosx')
				else None
				for platform_tag in self.platform_tags
			}
		)

	@functools.cached_property
	def windows_versions(self) -> frozendict[str, typ.Literal['win32'] | None]:
		"""Windows ABI versions supported by this wheel.

		Notes:
			- In terms of ABI, there is only one on Windows: `win32`.
			- Non-`win` platform tags will always map to `None`.
		"""
		return frozendict(
			{
				'win32' if platform_tag.startswith('win') else None
				for platform_tag in self.platform_tags
			}
		)

	####################
	# - Wheel Sorting
	####################
	@functools.cached_property
	def sort_key_size(self) -> int:
		"""Priority to assign to this wheel sorting by size.

		Notes:
			- Higher values will sort later in the list.
			- When `self.size is None`, then the "size" will be set to 0.
		"""
		return int(self.size) if self.size is not None else 0

	@functools.cached_property
	def sort_key_preferred_linux(self) -> int:
		"""Priority to assign to this wheel when selecting one of several Linux wheels.

		Notes:
			Higher values will be chosen over lower values.
			The value should be deterministic from the platform tags.
		"""
		return -sum(
			[
				1000 * glibc_version[0] + glibc_version[1]
				for glibc_version in self.glibc_versions.values()
				if glibc_version is not None
			],
			start=0,
		)

	@functools.cached_property
	def sort_key_preferred_mac(self) -> int:
		"""Priority to assign to this wheel when selecting one of several MacOS wheels.

		Notes:
			Higher values will be chosen over lower values.
			The value should be deterministic from the platform tags.
		"""
		return -sum(
			[
				1000 * macos_version[0] + macos_version[1]
				for macos_version in self.macos_versions.values()
				if macos_version is not None
			],
			start=0,
		)

	@functools.cached_property
	def sort_key_preferred_windows(self) -> int:
		"""Priority to assign to this wheel when selecting one of several Windows wheels.

		Notes:
			Higher values will be chosen over lower values.
			The value should be deterministic from the platform tags.
		"""
		return sum(
			{'any': 2, 'win32': 1, 'win_amd64': 0}[platform_tag]
			for platform_tag in self.platform_tags
		)

	####################
	# - Match BLPlatform
	####################
	def bl_platforms(
		self,
		*,
		min_glibc_version: tuple[int, int] | None = None,
		min_macos_version: tuple[int, int] | None = None,
	) -> frozenset[extyp.BLPlatform]:
		"""All BLPlatforms that this wheel will run on.

		Notes:
			`extyp.BLPlatform` only denotes a _partial_ set of compatibility constraints,
			namely, particular OS / CPU architecture combinations.

			It does **not** a sufficient set of compatibility constraints to be able to say,
			for instance, "this wheel will work with any Linux version of Blender".

			A version of Blender versions comes with a Python runtime environment that imposes
			very important constraints such as:
			- Supported Python tags.
			- Supported ABI tags.

			To deduce final wheel compatibility, _both_ the BLPlatform _and_ the information derived
			from the Blender version must be checked.
		"""
		if 'any' in self.platform_tags:
			return frozenset(bl_platform for bl_platform in extyp.BLPlatform)

		bl_platforms: set[extyp.BLPlatform] = set()
		for platform_tag in self.platform_tags:
			# Windows
			if platform_tag in WIN_PLATFORM_TAGS_TO_BL_PLATFORMS:
				bl_platform = WIN_PLATFORM_TAGS_TO_BL_PLATFORMS.get(platform_tag)
				if bl_platform is not None:
					bl_platforms.add(bl_platform)

			# MacOS
			elif (macos_version := self.macos_versions[platform_tag]) is not None:
				bl_platforms |= {
					bl_platform
					for bl_platform in [
						extyp.BLPlatform.macos_x64,
						extyp.BLPlatform.macos_arm64,
					]
					if any(
						platform_tag.endswith(pypi_arch)
						for pypi_arch in bl_platform.pypi_arches
					)
					and (
						min_macos_version is None
						or (
							macos_version[0] < min_macos_version[0]
							or (
								macos_version[0] == min_macos_version[0]
								and macos_version[1] <= min_macos_version[1]
							)
						)
					)
				}

			# Linux
			elif (glibc_version := self.glibc_versions[platform_tag]) is not None:
				bl_platforms |= {
					bl_platform
					for bl_platform in [
						extyp.BLPlatform.linux_x64,
						extyp.BLPlatform.linux_arm64,
					]
					if any(
						platform_tag.endswith(pypi_arch)
						for pypi_arch in bl_platform.pypi_arches
					)
					and (
						min_glibc_version is None
						or (
							glibc_version[0] < min_glibc_version[0]
							or (
								glibc_version[0] == min_glibc_version[0]
								and glibc_version[1] <= min_glibc_version[1]
							)
						)
					)
				}

		return frozenset(bl_platforms)

	####################
	# - Wheel Validation
	####################
	def works_with_python_tags(self, python_tags: frozenset[str]) -> bool:
		"""Does this wheel work with a runtime that supports `python_tags`?

		Notes:
			This method doesn't guarantee directly that the wheel will run.
			It only guarantees that there is no mismatch in Python tags between
			what the environment supports, and what the wheel supports.

		Parameters:
			python_tags: List of Python tags supported by a runtime environment.

		Returns:
			Whether the Python tags of the environment, and the wheel, are compatible.
		"""
		return len(python_tags & self.python_tags) > 0

	def works_with_abi_tags(self, abi_tags: frozenset[str]) -> bool:
		"""Does this wheel work with a runtime that supports `abi_tags`?

		Notes:
			- It is very strongly recommended to always pass `"none"` as one of the `abi_tags`,
				since this is the ABI tag of pure-Python wheels.
			- This method doesn't guarantee directly that the wheel will run.
				It only guarantees that there is no mismatch in Python ABI tags between
				what the environment supports, and what the wheel supports.

		Parameters:
			python_tags: List of Python tags supported by a runtime environment.

		Returns:
			Whether the Python tags of the environment, and the wheel, are compatible.
		"""
		return len(abi_tags & self.abi_tags) > 0

	def is_download_valid(self, wheel_path: Path) -> bool:
		"""Check whether a downloaded file is, in fact, this wheel.

		Notes:
			Implemented by comparing the file hash to the expected hash.

		Raises:
			ValueError: If the hash digest of `wheel_path` does not match `self.hash`.
		"""
		if self.hash is None:
			return True

		with wheel_path.open('rb', buffering=0) as f:
			file_digest = hashlib.file_digest(f, 'sha256').hexdigest()

		return 'sha256:' + file_digest == self.hash

	####################
	# - Display
	####################
	@functools.cached_property
	def pretty_bl_platforms(self) -> str:
		"""Retrieve prettified, unfiltered `bl_platforms` for this wheel."""
		return ', '.join(sorted(self.bl_platforms()))
