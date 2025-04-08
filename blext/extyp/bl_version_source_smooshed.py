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

from .bl_version_source import BLVersionSource
from .bl_version_source_official import BLVersionSourceOfficial


class BLVersionSourceSmooshed(BLVersionSource, frozen=True):
	"""Several combined Blender version sources."""

	sources: frozenset[BLVersionSource]

	####################
	# - Overrides
	####################
	@functools.cached_property
	def version(self) -> str:
		"""Deduce the range of Blender version sources."""
		if self.are_official_sources_consecutive:
			if len(self.official_sources) == 1:
				return next(iter(self.official_sources)).version
			if len(self.official_sources) > 1:
				return f'v{self.blender_version_min}-v{self.blender_version_max}'

			return ','.join([
				bl_version_location.version
				for bl_version_location in self.unofficial_sources
			])
		msg = f"'BLVersionSourceSmooshed' doesn't support non-consecutive 'BLVersionLocationOfficial' releases: {self.official_sources}"
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
			return self.official_sources[-1].blender_version_max

		raise NotImplementedError

	####################
	# - Filtering
	####################
	@functools.cached_property
	def unofficial_sources(self) -> frozenset[BLVersionSource]:
		"""All non-official sources in `self.sources`."""
		official_version_locations = frozenset(self.unofficial_sources)

		return frozenset({
			location
			for location in self.sources
			if location in official_version_locations
		})

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

				else:
					major_counter += 1
					minor_counter = 0
					patch_counter = 0

		return True
