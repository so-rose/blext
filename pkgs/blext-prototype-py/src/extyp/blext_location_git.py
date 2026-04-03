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
import typing as typ
from pathlib import Path

import pydantic as pyd

from .blext_location import BLExtLocation


####################
# - BLExtLocation: Git
####################
class BLExtLocationGit(BLExtLocation, frozen=True):
	"""`git` repository location of a Blender extension.

	Attributes:
		url: URL of a `git` repository.
		rev: Reference to a particular commit.
		tag: Reference to a particular tag.
		branch: Reference to the head of a particular branch.
		entrypoint: Path to an extension specification file, relative to the repository root.
	"""

	url: pyd.HttpUrl
	rev: str | None = None
	tag: str | None = None
	branch: str | None = None
	entrypoint: Path | None = None

	force_global_project_cache: bool = True

	####################
	# - Validators
	####################
	@pyd.model_validator(mode='before')
	@classmethod
	def check_only_one_ref(cls, data: typ.Any) -> typ.Any:  # pyright: ignore[reportAny]
		"""Check that only one ref is given.

		If only `git_url` is given, then `branch` is set to `'main'`.

		Parameters:
			data: Raw data passed to `pydantic`'s model construction.
				Tends to be a dictionary.

		Returns:
			Altered and/or validated raw data for continuing `pydantic`s model construction.
		"""
		if isinstance(data, dict):
			num_refs_that_are_none = sum(
				1 if data.get(attr) is not None else 0  # pyright: ignore[reportUnknownMemberType]
				for attr in ['rev', 'tag', 'branch']
			)

			if num_refs_that_are_none == 0:
				data['branch'] = 'main'
				return data  # pyright: ignore[reportUnknownVariableType]

			if num_refs_that_are_none > 1:
				msg = f'Only one `git` reference can be given, but {num_refs_that_are_none} were found (data={data})'
				raise ValueError(msg)

		return data  # pyright: ignore[reportUnknownVariableType]

	####################
	# - Protocol: ExtProjLocation
	####################
	@functools.cached_property
	def path_spec(self) -> Path:
		"""Path to a file from which the extension specification can be loaded.

		Notes:
			The specified `git` repository will be cloned, checked out, then searched for an extension spec.

		See Also:
			- See `blext.spec.BLExtSpec` for more on how a valid specification path is parsed.
		"""
		raise NotImplementedError
