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

import functools

import pydantic as pyd
import wheel_filename

from blext import extyp

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
# - Wheel Management
####################
class BLExtWheel(pyd.BaseModel, frozen=True):
	"""A particular Python dependency needed by a Blender extension."""

	url: pyd.HttpUrl

	hash: str | None = None
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
		return frozenset(
			{
				platform_tag
				if not platform_tag in MANYLINUX_LEGACY_ALIASES
				else MANYLINUX_LEGACY_ALIASES[platform_tag]
				for platform_tag in self._parsed_wheel_filename.platform_tags
				if not (
					platform_tag in MANYLINUX_LEGACY_ALIASES
					and MANYLINUX_LEGACY_ALIASES[platform_tag]
					in self._parsed_wheel_filename.platform_tags
				)
			}
		)

	@property
	def pretty_bl_platforms(self) -> str:
		"""Retrieve prettified, unfiltered `bl_platforms` for this wheel."""
		wheel_bl_platforms: set[extyp.BLPlatform | str] = set()
		for platform_tag in self.platform_tags:
			# Universal
			if platform_tag == 'any':
				wheel_bl_platforms.add('any')

			# Windows
			elif platform_tag.startswith('win'):
				bl_platform = {
					'win32': extyp.BLPlatform.windows_x64,
					'win_amd64': extyp.BLPlatform.windows_x64,
					'win_arm32': None,
					'win_arm64': extyp.BLPlatform.windows_arm64,
				}.get(platform_tag)

				if bl_platform is not None:
					wheel_bl_platforms.add(bl_platform)

			# Mac
			elif platform_tag.startswith('macos'):
				for bl_platform in [
					extyp.BLPlatform.macos_x64,
					extyp.BLPlatform.macos_arm64,
				]:
					if any(
						platform_tag.endswith(pypi_arch)
						for pypi_arch in bl_platform.pypi_arches
					):
						wheel_bl_platforms.add(bl_platform)

			# Linux
			elif platform_tag.startswith('manylinux'):
				for bl_platform in [
					extyp.BLPlatform.linux_x64,
					extyp.BLPlatform.linux_arm64,
				]:
					if any(
						platform_tag.endswith(pypi_arch)
						for pypi_arch in bl_platform.pypi_arches
					):
						wheel_bl_platforms.add(bl_platform)

		return ', '.join(sorted(wheel_bl_platforms))

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
		return -int(self.size) if self.size is not None else 0
		## TODO: Sort such that highest valid MacOS version gets picked first.

	@functools.cached_property
	def sort_key_preferred_mac(self) -> int:
		"""Priority to assign to this wheel when selecting one of several MacOS wheels.

		Notes:
			Higher values will be chosen over lower values.
			The value should be deterministic from the platform tags.
		"""
		return -int(self.size) if self.size is not None else 0
		## TODO: Sort such that highest valid MacOS version gets picked first.

	@functools.cached_property
	def sort_key_preferred_windows(self) -> int:
		"""Priority to assign to this wheel when selecting one of several Windowws wheels.

		Notes:
			Higher values will be chosen over lower values.
			The value should be deterministic from the platform tags.
		"""
		return sum(
			{'any': 2, 'win32': 1, 'win_amd64': 0}[platform_tag]
			for platform_tag in self.platform_tags
		)

	# def macos_versions(
	# wheel: BLExtWheel,
	# bl_platform: BLPlatform,
	# ) -> list[tuple[int, int]]:
	# macos_versions = [
	# wheel.macos_version(platform_tag)
	# for platform_tag in wheel.platform_tags
	# if any(
	# platform_tag.endswith(pypi_arch)
	# for pypi_arch in bl_platform.pypi_arches
	# )
	# ]

	# return [
	# macos_version
	# for macos_version in macos_versions
	# if macos_version is not None
	# ]

	# def glibc_versions(
	# wheel: BLExtWheel,
	# bl_platform: BLPlatform,
	# ) -> list[tuple[int, int]]:
	# glibc_versions = [
	# wheel.glibc_version(platform_tag)
	# for platform_tag in wheel.platform_tags
	# if any(
	# platform_tag.endswith(pypi_arch)
	# for pypi_arch in bl_platform.pypi_arches
	# )
	# ]

	# return [
	# glibc_version
	# for glibc_version in glibc_versions
	# if glibc_version is not None
	# ]

	####################
	# - Match BLPlatform
	####################
	def compatible_bl_platforms(
		self,
		*,
		valid_python_tags: frozenset[str],
		valid_abi_tags: frozenset[str],
		min_glibc_version: tuple[int, int],
		min_macos_version: tuple[int, int],
	) -> frozenset[extyp.BLPlatform]:
		is_python_version_valid = len(valid_python_tags & self.python_tags) > 0
		is_abi_valid = len(valid_abi_tags & self.abi_tags) > 0

		supported_bl_platforms: set[extyp.BLPlatform] = set()
		accepted_platform_tags: set[str] = set()
		rejected_platform_tags: set[str] = set()
		if is_python_version_valid and is_abi_valid:
			if 'any' in self.platform_tags:
				return frozenset(bl_platform for bl_platform in extyp.BLPlatform)

			for platform_tag in self.platform_tags:
				macos_version = self.macos_version(platform_tag)
				glibc_version = self.glibc_version(platform_tag)

				# Windows
				if platform_tag.startswith('win'):
					bl_platform = {
						'win32': extyp.BLPlatform.windows_x64,
						'win_amd64': extyp.BLPlatform.windows_x64,
						'win_arm32': None,
						'win_arm64': extyp.BLPlatform.windows_arm64,
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
						extyp.BLPlatform.macos_x64,
						extyp.BLPlatform.macos_arm64,
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
						extyp.BLPlatform.linux_x64,
						extyp.BLPlatform.linux_arm64,
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
