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

"""Load various data from external sources."""

import functools
import typing as typ
from pathlib import Path

import cyclopts
import pydantic as pyd

from blext import extyp, finders, location, spec

from .global_config import GlobalConfig

####################
# - Release Profiles
####################
LOCATION_GROUP = cyclopts.Group('Location', sort_key=10)
SPECIFICATION_GROUP = cyclopts.Group('Target', sort_key=11)


class BLExtInfoGit(pyd.BaseModel, frozen=True):
	"""Information about an extension project in a git repository.

	Attributes:
		url: URL of a `git` repository.
		rev: Reference to a particular commit.
		tag: Reference to a particular tag.
		branch: Reference to the head of a particular branch.
		entrypoint: Path to an extension specification file, relative to the repo root.
	"""

	url: typ.Annotated[
		str,
		cyclopts.Parameter(
			env_var='BLEXT_GIT_URL',
		),
	]
	rev: typ.Annotated[
		str | None,
		cyclopts.Parameter(
			env_var='BLEXT_GIT_REV',
		),
	] = None
	tag: typ.Annotated[
		str | None,
		cyclopts.Parameter(
			env_var='BLEXT_GIT_TAG',
		),
	] = None
	branch: typ.Annotated[
		str | None,
		cyclopts.Parameter(
			env_var='BLEXT_GIT_BRANCH',
		),
	] = None
	entrypoint: typ.Annotated[
		Path | None,
		cyclopts.Parameter(
			env_var='BLEXT_GIT_ENTRYPOINT',
		),
	] = None


class BLExtInfo(pyd.BaseModel, frozen=True):
	"""Information about a Blender extension.

	Notes:
		Names are chosen to be friendly on a CLI interface.

	Attributes:
		path: Path to a Blender extension project:

			- **Current Directory** (**default**): Search upwards for a `pyproject.toml`.
			- **Project File** (`pyproject.toml`): Configure using the `[tool.blext]` table.
			- **Project Folder** (`*/pyproject.toml`): Folder containing a `pyproject.toml`.
			- **Script File** (`*.py`): Identical configuration using "inline script metadata".

		url: URL to a Blender extension _Script File_.
		git: A `git` repository containing `pyproject.toml`.
		platform: Blender platform(s) to target.
		profile: Release profile to apply.
		config: Global configuration of `blext`.
	"""

	path: typ.Annotated[
		Path | None,
		cyclopts.Parameter(
			group=LOCATION_GROUP,
			name=['--path', '-p'],
			env_var='BLEXT_PATH',
		),
	] = None
	url: typ.Annotated[
		str | None,
		cyclopts.Parameter(
			group=LOCATION_GROUP,
			env_var='BLEXT_URL',
		),
	] = None
	git: typ.Annotated[
		BLExtInfoGit | None,
		cyclopts.Parameter(group=LOCATION_GROUP),
	] = None

	platform: typ.Annotated[
		tuple[extyp.BLPlatform | typ.Literal['detect'], ...],
		cyclopts.Parameter(
			group=SPECIFICATION_GROUP,
			env_var='BLEXT_PLATFORM',
			negative=[],
		),
	] = ()
	profile: typ.Annotated[
		extyp.StandardReleaseProfile | str | None,
		cyclopts.Parameter(
			group=SPECIFICATION_GROUP,
			env_var='BLEXT_PROFILE',
		),
	] = None

	####################
	# - Parsed Properties
	####################
	@functools.cached_property
	def proj_uri(self) -> BLExtInfoGit | pyd.HttpUrl | Path | None:
		"""A project URI that allows uniquely locating an extension project."""
		if self.url:
			return pyd.HttpUrl(self.url)
		if self.git:
			return self.git
		return self.path

	@functools.cached_property
	def request_bl_platforms(self) -> frozenset[extyp.BLPlatform]:
		"""Set of BLPlatforms to request support for."""
		return frozenset(
			{
				finders.detect_local_blplatform() if platform == 'detect' else platform
				for platform in self.platform
			}
		)

	def blext_location(self, config: GlobalConfig) -> location.BLExtLocation:
		"""Find the Blender extension and return its (abstract) location.

		Notes:
			- Essentially a convenient way of calling `blext.finders.find_proj_spec`.
			- The "abstract location" returned exposes a standard interface for getting ex. the path to the extension specification.
			To achieve this functionality, it might first ex. download a URL, clone a git repository, etc. .


		Parameters:
			config: Global configuration.
				In particular, contains locations of global paths.

		See Also:
			- `blext.location.BLExtLocation`: Abstract location of a Blender extension.
			- `blext.finders.find_proj_spec`: Find a project by its URI, returning a location.
		"""
		return finders.find_proj_spec(
			self.proj_uri,
			path_global_project_cache=config.path_global_project_cache,
			path_global_download_cache=config.path_global_download_cache,
		)

	def blext_spec(self, config: GlobalConfig) -> spec.BLExtSpec:
		"""Load the extension specification.

		Notes:
			- Uses `self.blext_location` internally.
			- Runs `blext_spec.set_bl_platforms(self.request_bl_platforms)` after loading succeeds.

		Parameters:
			config: Global configuration.
				In particular, contains locations of global paths.

		See Also:
			- `blext.location.BLExtLocation`: Abstract location of a Blender extension.
			- `blext.finders.find_proj_spec`: Find a project by its URI, returning a location.
		"""
		blext_spec = spec.BLExtSpec.from_proj_spec_path(
			path_proj_spec=self.blext_location(config=config).path_spec,
			release_profile_id=self.profile,
			override_path_uv_exe=config.path_uv_exe,
		)

		if not self.platform:
			return blext_spec
		return blext_spec.set_bl_platforms(self.request_bl_platforms)
