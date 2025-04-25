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

"""Extension types serving as meaningful abstractions for managing Blender extensions."""

import collections.abc
import functools
import typing as typ

from frozendict import frozendict

from .bl_platform import BLPlatform
from .bl_version import BLVersion


####################
# - Type Stubs
####################
@typ.runtime_checkable
class IPyDepWheel(typ.Protocol):
	"""Matches `blext.pydeps.PyDepWheel`."""

	def works_with_platform(
		self,
		bl_platform: BLPlatform,
		*,
		min_glibc_version: tuple[int, int] | None,
		min_macos_version: tuple[int, int] | None,
	) -> bool:
		"""Matches `blext.pydeps.PyDepWheel`."""
		...


####################
# - Class
####################
class BLPlatformSet(str):
	"""Several `BLPlatform`s represented with similar semantics."""

	####################
	# - BLPlatform Access
	####################
	@functools.cached_property
	def sorted_bl_platforms(self) -> tuple[BLPlatform, ...]:
		"""Retrieve the `BLPlatform` of this string."""
		return tuple(BLPlatform(v) for v in self.split('_'))

	@functools.cached_property
	def bl_platforms(self) -> frozenset[BLPlatform]:
		"""Retrieve the `BLPlatform` of this string."""
		return frozenset(self.sorted_bl_platforms)

	####################
	# - BLPlatform: Platform Checks
	####################
	@functools.cached_property
	def is_windows(self) -> bool:
		"""Whether this contains a Windows-based platform."""
		return any(bl_platform.is_windows for bl_platform in self.bl_platforms)

	####################
	# - BLPlatform: Archive File Extension
	####################
	@functools.cached_property
	def official_archive_file_exts(self) -> frozenset[str]:
		"""Set of official archive file extensions, each used by one of these BLPlatformSet."""
		return frozenset({
			bl_platform.wheel_platform_tag_prefix for bl_platform in self.bl_platforms
		})

	####################
	# - BLPlatform: PyPi Information
	####################
	@functools.cached_property
	def pypi_arches(self) -> frozenset[str]:
		"""Set of PyPi CPU-architecture tags supported by one of these BLPlatformSet."""
		return functools.reduce(
			lambda a, b: a | b,
			(bl_platform.pypi_arches for bl_platform in self.bl_platforms),
		)

	@functools.cached_property
	def wheel_platform_tag_prefixes(self) -> frozenset[str]:
		"""Set of wheel platform tag prefixes, each used by one of these BLPlatformSet."""
		return frozenset({
			bl_platform.wheel_platform_tag_prefix for bl_platform in self.bl_platforms
		})

	####################
	# - BLPlatform: Pymarker Information
	####################
	@functools.cached_property
	def pymarker_os_names(self) -> frozenset[typ.Literal['posix', 'nt']]:
		"""Set of pymarker OS names, each used by one of these BLPlatformSet."""
		return frozenset({
			bl_platform.pymarker_os_name for bl_platform in self.bl_platforms
		})

	@functools.cached_property
	def pymarker_platform_machines(self) -> frozenset[str]:
		"""Value of `platform.machine()`, each used by one of these BLPlatformSet."""
		return functools.reduce(
			lambda a, b: a | b,
			(
				bl_platform.pymarker_platform_machines
				for bl_platform in self.bl_platforms
			),
		)

	@functools.cached_property
	def pymarker_platform_systems(
		self,
	) -> frozenset[typ.Literal['Linux', 'Darwin', 'Windows']]:
		"""Set of pymarker OS names, each used by one of these BLPlatformSet."""
		return frozenset({
			bl_platform.pymarker_platform_system for bl_platform in self.bl_platforms
		})

	@functools.cached_property
	def pymarker_sys_platforms(
		self,
	) -> frozenset[typ.Literal['linux', 'darwin', 'win32']]:
		"""Set of pymarker `sys.platform` values, each used by one of these BLPlatformSet."""
		return frozenset({
			bl_platform.pymarker_sys_platform for bl_platform in self.bl_platforms
		})

	####################
	# - Creation
	####################
	@classmethod
	def from_bl_platform(cls, bl_platform: BLPlatform) -> typ.Self:
		"""Create from a single `BLPlatform`."""
		return cls(bl_platform)

	@classmethod
	def from_bl_platforms(
		cls, bl_platforms: collections.abc.Collection[BLPlatform]
	) -> typ.Self:
		"""Create from a sequence of `BLPlatform`s."""
		if len(bl_platforms) > 0:
			return cls('_'.join(sorted(bl_platforms)))

		msg = '`from_bl_platforms` must be called with a collection of `bl_platforms` whose length is greater than `0`.'
		raise ValueError(msg)

	####################
	# - Smooshing
	####################
	def is_smooshable_with(
		self,
		bl_platform: BLPlatform,
		*,
		ext_bl_versions: frozenset[BLVersion],
		ext_min_glibc_version: tuple[int, int] | None,
		ext_min_macos_version: tuple[int, int] | None,
		ext_wheels_granular: frozendict[
			BLVersion, frozendict[BLPlatform, frozenset[IPyDepWheel]]
		],
	) -> bool:
		"""Check is this `BLPlatformSet` can be safely combined with a `BLPlatform`."""
		# IF all wheels that work with me, also work with you, then smoosh is valid.
		##
		return all(
			wheel.works_with_platform(
				bl_platform,
				min_glibc_version=(
					bl_version.min_glibc_version
					if ext_min_glibc_version is None
					else ext_min_glibc_version
				),
				min_macos_version=(
					bl_version.min_macos_version
					if ext_min_macos_version is None
					else ext_min_macos_version
				),
			)
			for bl_version in ext_bl_versions
			for self_bl_platform in self.bl_platforms
			for wheel in ext_wheels_granular[bl_version][self_bl_platform]
		)

	def smoosh_with(
		self,
		bl_platform: BLPlatform,
	) -> typ.Self:
		"""Combine this `BLPlatformSet` with a `BLPlatform`."""
		return self.__class__.from_bl_platforms(
			sorted([*self.sorted_bl_platforms, bl_platform])
		)
