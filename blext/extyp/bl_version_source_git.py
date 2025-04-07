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

from .bl_version_source import BLVersionSource


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
