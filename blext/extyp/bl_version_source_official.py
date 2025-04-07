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

"""Implements `BLVersionSourceOfficial`."""

import functools

import pydantic as pyd

from .bl_platform import BLPlatform
from .bl_version_source import BLVersionSource


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
