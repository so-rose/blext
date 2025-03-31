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

"""Implements `BLVersionSource`."""

import functools

import pydantic as pyd

from .bl_platform import BLPlatform


####################
# - Blender Version Source
####################
class BLVersionSource(pyd.BaseModel, frozen=True):
	"""A locatable version of Blender."""

	####################
	# - Overrides
	####################
	@functools.cached_property
	def version(self) -> str:
		"""Some kind of unique identifier of the referenced Blender version."""
		raise NotImplementedError

	@functools.cached_property
	def blender_version_min(self) -> str:
		"""Minimum supported Blender version.

		Warnings:
			**Do not parse**. Only for specialized use.

			**Do not use `self.version`** either.

			Instead, handle versions in a manner consistent with each particular `BLVersionLocation` subclass.

		Notes:
			- Must correspond to an official releases `>=4.2.0`.
			- Corresponds directly to the same-named property in `blender_manifest.toml`.
			- The `blender_manifest.toml` format enforces that this be given by all `BLVersion`s. For ex. forks that don't always have such a clean descriptor, it's okay to lie to make it work.
		"""
		raise NotImplementedError

	@functools.cached_property
	def blender_version_max(self) -> str | None:
		"""Maximum supported Blender version, **not including** this version.

		Warnings:
			**Do not parse**. Only for specialized use.

			**Do not use `self.version`** either.

			Instead, handle versions in a manner consistent with each particular `BLVersionLocation` subclass.

		Notes:
			- Must correspond to an official release `>=4.2.1`.
			- Corresponds directly to the same-named property in `blender_manifest.toml`.
			- Does not have to be given.
		"""
		return None


class BLVersionSourceGit(BLVersionSource, frozen=True):
	"""A version of Blender located at a `git` repository."""

	rev: str | None = None
	tag: str | None = None

	url: pyd.HttpUrl = pyd.HttpUrl('https://projects.blender.org/blender/blender.git')

	@functools.cached_property
	def version(self) -> str:
		"""Tag or commit ID of this Blender version."""
		if self.tag is not None:
			return self.tag

		raise NotImplementedError

	@functools.cached_property
	def blender_version_min(self) -> str:
		"""Not yet implemented."""
		raise NotImplementedError


class BLVersionSourceOfficial(BLVersionSource, frozen=True):
	"""An officially released version of Blender."""

	official_version: tuple[int, int, int]

	base_download_url: pyd.HttpUrl = pyd.HttpUrl('https://download.blender.org/release')

	####################
	# - Overrides
	####################
	@functools.cached_property
	def version(self) -> str:
		"""Release version prefixed with `v`."""
		return 'v' + self.version_major_minor_patch

	@functools.cached_property
	def blender_version_min(self) -> str:
		"""This exact `M.m.p` version is the minimum."""
		return self.version_major_minor_patch

	@functools.cached_property
	def blender_version_max(self) -> str:
		"""The exact next `M.m+1.0` version is the maximum."""
		return f'{self.official_version[0]}.{self.official_version[1] + 1}.0'

	####################
	# - Version Information
	####################
	@functools.cached_property
	def version_major_minor(self) -> str:
		"""Release version with no prefix, including only `M.m`."""
		return f'{self.official_version[0]}.{self.official_version[1]}'

	@functools.cached_property
	def version_major_minor_patch(self) -> str:
		"""Release version with no prefix, including `M.m.p`."""
		return f'{self.official_version[0]}.{self.official_version[1]}.{self.official_version[2]}'

	####################
	# - Downloading
	####################
	def portable_download_url(self, bl_platform: BLPlatform) -> pyd.HttpUrl:
		"""URL to a portable variant of this Blender release.

		Warnings:
			Currently, it is not checked whether `bl_platform` has an official Blender download available.

			Always check that this URL exists and looks reasonable before downloading.

		"""
		return pyd.HttpUrl(
			'/'.join(
				[
					str(self.base_download_url),
					f'Blender{self.version_major_minor}',
					f'blender-{self.version_major_minor}-{bl_platform}.{bl_platform.official_archive_file_ext}',
				]
			)
		)


class BLVersionSources(BLVersionSource, frozen=True):
	"""Several combined Blender version sources."""

	sources: frozenset[BLVersionSource]

	####################
	# - Overrides
	####################
	@functools.cached_property
	def version(self) -> str:
		"""Deduce the range of Blender version sources."""
		if self.are_official_sources_consecutive:
			if self.official_sources:
				return f'{self.blender_version_min}-{self.blender_version_max}'
			return ','.join(
				[
					bl_version_location.version
					for bl_version_location in self.unofficial_sources
				]
			)
		msg = f"'BLVersionLocationSmooshed' doesn't support non-consecutive 'BLVersionLocationOfficial' releases: {self.official_sources}"
		raise ValueError(msg)

	@functools.cached_property
	def blender_version_min(self) -> str:
		"""This exact `M.m.p` version is the minimum."""
		if self.official_sources:
			return self.official_sources[0].blender_version_min

		raise NotImplementedError

	@functools.cached_property
	def blender_version_max(self) -> str:
		"""The exact next `M.m.p+1` version is the maximum."""
		if self.official_sources:
			return self.official_sources[0].blender_version_max

		raise NotImplementedError

	####################
	# - Filtering
	####################
	@functools.cached_property
	def unofficial_sources(self) -> frozenset[BLVersionSource]:
		"""All non-official sources in `self.sources`."""
		official_version_locations = frozenset(self.unofficial_sources)

		return frozenset(
			{
				location
				for location in self.sources
				if location in official_version_locations
			}
		)

	@functools.cached_property
	def official_sources(self) -> list[BLVersionSourceOfficial]:
		"""All official sources in `self.sources`."""
		return sorted(
			[
				bl_version_location_official
				for bl_version_location_official in self.sources
				if isinstance(bl_version_location_official, BLVersionSourceOfficial)
			],
			key=lambda el: el.official_version,
		)

	@functools.cached_property
	def are_official_sources_consecutive(self) -> bool:
		"""Whether all official sources are consecutive, without holes."""
		if len(self.official_sources) > 1:
			major_counter, minor_counter, patch_counter = self.official_sources[
				0
			].official_version
			for official_location in self.official_sources[1:]:
				if (
					official_location.official_version[0] == major_counter
					and official_location.official_version[1] == minor_counter
				):
					if official_location.official_version[2] != patch_counter + 1:
						return False
					patch_counter += 1

				elif official_location.official_version[0] == major_counter:
					if (
						official_location.official_version[1] != minor_counter + 1
						or official_location.official_version[2] != 0
					):
						return False
					minor_counter += 1
					patch_counter = 0

				elif (
					official_location.official_version[0] != major_counter + 1
					or official_location.official_version[1] != 0
					or official_location.official_version[2] != 0
				):
					return False

				major_counter += 1
				minor_counter = 0
				patch_counter = 0

		return True
