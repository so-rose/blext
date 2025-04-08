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

"""Implements the concept of "extension location" via the `BLExtLocation` object."""

import functools
from pathlib import Path

import pydantic as pyd

from .blext_location import BLExtLocation


####################
# - BLExtLocation: HTTP URL
####################
class BLExtLocationHttp(BLExtLocation, frozen=True):
	"""Internet location of a Blender extension.

	Attributes:
		url: URL of a script extension.
	"""

	url: pyd.HttpUrl

	@functools.cached_property
	def path_spec(self) -> Path:
		"""Path to a file from which the extension specification can be loaded.

		Notes:
			The specified `self.url` will be downloaded, then searched for an extension spec.

		See Also:
			- See `blext.spec.BLExtSpec` for more on how a valid specification path is parsed.
		"""
		raise NotImplementedError
