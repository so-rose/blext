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

import typing as typ
from pathlib import Path

import cyclopts
import pydantic as pyd
from frozendict import frozendict

from blext import extyp
from blext.spec import BLExtSpec

from .global_config import GlobalConfig

####################
# - Constants: CLI Groups
####################
LOCATION_GROUP = cyclopts.Group('Location', sort_key=10)
SPECIFICATION_GROUP = cyclopts.Group('Target', sort_key=11)

####################
# - Constants: Error Messages
####################
ERR_EXPLAIN_PROJ: list[str] = [
	'> **What is `PROJ`**? An easy _positional_ argument that finds extensions.',
	'> - **Usage**: `blext <CMD> <PROJ> ...`',
	'> - **Example**: `blext build script-extension.py`',
	'> - **Example**: `blext build git+https://example.com/ext.git`',
	'>',
	'> _All `blext` commands that locate extensions accept `PROJ`._',
	'',
]

ERR_VALID_PROJS: list[str] = [
	'> **`PROJ` Options**:',
	'> - **Path** (default): `...`',
	'> - **Path** (detect):  `<path>`',
	'> - **Path** (script):  `script+<path>`.',
	'> - **Path** (project): `project+<path>`.',
	'> - **Path** (packed):  `packed+<path>`.',
	'> - **URL** (detect):   `<http_url>`.',
	'> - **URL** (script):   `script+<http_url>`.',
	'> - **URL** (project):  `project+<http_url>`.',
	'> - **URL** (packed):   `packed+<http_url>`.',
	'> - **git** (detect):   `git+<git_uri>`.',
	'',
	'> **`PROJ` Details**:',
	'> - **Path** (default): Search up for `pyproject.toml`, from `cwd`.',
	'> - **Path** (detect):  Search `<path>` for any kind of ext.',
	'> - **Path** (script):  `<path>` is a script-file ext, usually `.py`.',
	'> - **Path** (project): `<path>` is a `pyproject.toml` or its parent.',
	'> - **Path** (packed):  `<path>` is a packed extension `.zip`.',
	'> - **URL** (detect):   Search `<http_url>` for a script or packed ext.',
	'> - **URL** (script):   `<http_url>` is a script ext, usually `.py`.',
	'> - **URL** (packed):   `<http_url>` is packed extension `.zip`.',
	'> - **git** (detect):   `<git_uri>` is any kind of ext (use w/`--git.*`).',
	'',
]


####################
# - GitLocationUI: CLI Parameters to transform into BLExtLocationGit
####################
class GitLocationUI(pyd.BaseModel, frozen=True):
	"""Information about an extension project in a git repository.

	Attributes:
		url: URL of a `git` repository.
		rev: Reference to a particular commit.
		tag: Reference to a particular tag.
		branch: Reference to the head of a particular branch.
		entrypoint: Path to an extension specification file, relative to the repo root.
	"""

	url: typ.Annotated[
		str | None,
		cyclopts.Parameter(
			env_var='BLEXT_GIT_URL',
		),
	] = None
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


####################
# - BLExtUI: CLI inter BLExtLocation and BLExtSpec
####################
class BLExtUI(pyd.BaseModel, frozen=True):
	"""CLI parameters-interface making it easy to create `BLExtLocation` and `BLExtSpec`.

	Notes:
		Names are chosen to be friendly on a CLI interface.

	Attributes:
		path: Path to a `blext` project:

			- **Current Directory** (_default_): Search upwards for a `pyproject.toml`.
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
		GitLocationUI | None,
		cyclopts.Parameter(group=LOCATION_GROUP),
	] = None

	# TODO: --bl-version parameter, which can be specified once.
	## --bl-version <default>: Specify every extension-supported BLVersion.
	## --bl-version detect: Detect the BLVersion of the default Blender executable.
	## --bl-version 4.4.0: Specify the 4.4.0 release.
	## --bl-version 4.3: Specify every 4.3 release.
	## --bl-version 4.[3:5]: Select every release from 4.3 to 4.5
	## --bl-version 4.2.[1:]: Select all 4.2 releases except 4.2.0.
	##
	## TODO: Include options on what how the raw versions specified by --bl-version are simplified.
	## --simplify-bl-version include
	##     - Smoosh the extension's supported BLVersions, then pick as few as possible from there.
	## --simplify-bl-version exact
	##     - Smoosh the specified BLVersions, and constrain BLExtSpec to whatever's left.
	## --simplify-bl_version none
	##     - No smooshing.
	##
	## **Several BLVersions may come out of this**. In practice, this is dealt with by:
	## - show valid_bl_versions: Print out all valid BLVersions for the ext, after simplification.
	## - run: Choose the highest BLVersion that we have an executable for.
	## - build/check/etc.: Enforce that the user can only choose one (smooshed) BLVersion!
	##     - The error should provide a suggestion for how to set --bl-version.
	##     - Only show valid possibility of --bl-version for each possibility.
	##     - Document how to use 'show valid_bl_versions' and a bash for loop to build many.
	##
	## TODO: For 'build', add an option to control many small zips vs. few large zips.
	bl_version: typ.Annotated[
		tuple[extyp.BLReleaseOfficial | typ.Literal['detect'], ...],
		cyclopts.Parameter(
			group=SPECIFICATION_GROUP,
			env_var='BLEXT_BL_VERSION',
			negative=[],
		),
	] = ()
	bl_platform: typ.Annotated[
		tuple[extyp.BLPlatform | typ.Literal['detect'], ...],
		cyclopts.Parameter(
			group=SPECIFICATION_GROUP,
			env_var='BLEXT_BL_PLATFORM',
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
	# - Derived BLExt Types
	####################
	def requested_bl_platforms(
		self, global_config: GlobalConfig
	) -> frozenset[extyp.BLPlatform]:
		"""Set of BLPlatforms that the user requested."""
		return frozenset(
			{
				global_config.local_bl_platform
				if bl_platform == 'detect'
				else bl_platform
				for bl_platform in self.bl_platform
			}
		)

	def requested_bl_versions(
		self, global_config: GlobalConfig
	) -> frozenset[extyp.BLVersion]:
		"""Set of BLPlatforms that the user requested."""
		return frozenset(
			{
				global_config.local_default_bl_version
				if bl_release == 'detect'
				else bl_release.bl_version
				for bl_release in self.bl_version
			}
		)

	def blext_location(self, global_config: GlobalConfig) -> extyp.BLExtLocation:
		"""Extension location that the user requested.

		Notes:
			- Essentially a convenient way of calling `blext.finders.find_proj_spec`.
			- The "abstract location" returned exposes a standard interface for getting ex. the path to the extension specification.
			To achieve this functionality, it might first ex. download a URL, clone a git repository, etc. .


		Parameters:
			proj: String shorthand for specifying a `blext` project location.
			config: Global configuration.
				In particular, contains locations of global paths.

		See Also:
			- `blext.location.BLExtLocation`: Abstract location of a Blender extension.
			- `blext.finders.find_proj_spec`: Find a project by its URI, returning a location.
		"""
		config_paths = {
			'path_global_project_cache': global_config.path_global_project_cache,
			'path_global_download_cache': global_config.path_global_download_cache,
		}

		err_msgs: list[str] = []
		match (self.path, self.url, self.git):
			case (path, None, None):
				return extyp.BLExtLocationPath(
					path=path,
					**config_paths,  # pyright: ignore[reportArgumentType]
				)

			case (None, str() as url, None):
				return extyp.BLExtLocationHttp(
					url=url,  # pyright: ignore[reportArgumentType]
					**config_paths,  # pyright: ignore[reportArgumentType]
				)

			case (None, None, GitLocationUI() as git) if git.url is not None:
				return extyp.BLExtLocationGit(
					url=pyd.HttpUrl(git.url),
					rev=git.rev,
					tag=git.tag,
					branch=git.branch,
					entrypoint=git.entrypoint,
					**config_paths,  # pyright: ignore[reportArgumentType]
				)

			case (None, None, GitLocationUI()):
				err_msgs += [
					'**No `git` URL Given**: `--git.url` must be given.',
					'',
					*ERR_EXPLAIN_PROJ,
				]

			case (
				(None, str(), GitLocationUI())
				| (Path(), None, GitLocationUI())
				| (Path(), str(), None)
				| (Path(), str(), GitLocationUI())
			):
				err_msgs += [
					'**Multiple Locations Given**: Only one of `--path`, `--url`, or `--git` may be given.',
					'> **Given Locations**:',
					*[
						f'> - `{name}`: `{spec}`'
						for name, spec in {
							'--path': self.path,
							'--url': self.url,
							'--git': self.git,
						}.items()
					],
					'>',
					'> _Exactly one must be given._',
					'',
					*ERR_EXPLAIN_PROJ,
				]

		raise ValueError(*err_msgs)

	def blext_spec(self, global_config: GlobalConfig) -> BLExtSpec:
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
		blext_spec = BLExtSpec.from_proj_spec_path(
			self.blext_location(global_config=global_config).path_spec,
			path_uv_exe=global_config.path_uv_exe,
			release_profile_id=self.profile,
		)

		bl_platforms = self.requested_bl_platforms(global_config)
		if not bl_platforms:
			return blext_spec
		return blext_spec.replace_bl_platforms(bl_platforms)

	def bl_versions(self, global_config: GlobalConfig) -> frozenset[extyp.BLVersion]:
		"""All selected Blender versions."""
		requested_bl_versions = self.requested_bl_versions(global_config)
		if not requested_bl_versions:
			return self.blext_spec(global_config).bl_versions
		return requested_bl_versions

	####################
	# - Zip Paths
	####################
	def path_zip_prepacks(
		self, global_config: GlobalConfig
	) -> frozendict[extyp.BLVersion, Path]:
		"""Paths of all extension pre-packed archives that should be prepared from `self.blext_spec`.

		Parameters:
			global_config: Global configuration parameters.

		Returns:
			Mapping from `BLVersion` to the corresponding `Path` to prepare pre-packed archive for that version (chunk) at.
		"""
		blext_location = self.blext_location(global_config)
		blext_spec = self.blext_spec(global_config)

		extension_filenames = blext_spec.export_extension_filenames()
		return frozendict(
			{
				bl_version: (
					blext_location.path_prepack_cache / extension_filenames[bl_version]
				)
				for bl_version in blext_spec.bl_versions
			}
		)

	def path_zips(
		self, global_config: GlobalConfig
	) -> frozendict[extyp.BLVersion, Path]:
		"""Paths of all extension `.zip`s that should be built from `self.blext_spec`.

		Parameters:
			global_config: Global configuration parameters.

		Returns:
			Mapping from `BLVersion` to the corresponding `Path` to build the extension for that version (chunk) at.
		"""
		blext_location = self.blext_location(global_config)
		blext_spec = self.blext_spec(global_config)

		extension_filenames = blext_spec.export_extension_filenames()
		return frozendict(
			{
				bl_version: (
					blext_location.path_build_cache / extension_filenames[bl_version]
				)
				for bl_version in blext_spec.bl_versions
			}
		)

	####################
	# - Parse Positional Parameter
	####################
	def parse_proj(self, proj: str | None) -> typ.Self:  # noqa: C901, PLR0912
		"""Alter the information with information from the position argument `PROJ`.

		Parameters:
			proj: Positional argument making it easy for users to specify a project.
		"""
		err_msgs: list[str] = []
		kwargs = self.model_dump()
		match (proj, self.path, self.url, self.git):
			case (None, _, _, _):
				return self

			####################
			# - Project String: HTTP
			####################
			case (str() as proj, None, None, None) if proj.startswith('script+http'):
				kwargs['url'] = proj.removeprefix('script+')

			case (str() as proj, None, None, None) if proj.startswith('packed+http'):
				kwargs['url'] = proj.removeprefix('packed+')

			case (str() as proj, _, str() as url, _) if proj.startswith(
				('script+http', 'packed+http', 'http')
			):
				err_msgs += [
					f"**Two URLs Given**: Both `PROJ` ('{proj}') and `--url` ('{url}') are given.",
					'> There are two ways to locate a `blext` extension by URL:',
					'> 1. Specify `PROJ` (ex. `https://example.org/ext.py`).',
					'> 2. Specify `--url` explicitly.',
					'>',
					'> _Exactly one must be given._',
					'',
				]

			####################
			# - Project String: Path
			####################
			case (str() as proj, None, None, None) if proj.startswith('script+'):
				kwargs['path'] = proj.removeprefix('script+')

			case (str() as proj, None, None, None) if proj.startswith('project+'):
				kwargs['path'] = proj.removeprefix('project+')

			case (str() as proj, None, None, None) if proj.startswith('packed+'):
				kwargs['path'] = proj.removeprefix('packed+')

			case (str() as proj, Path() as path, _, _) if proj.startswith(
				('script+', 'packed+')
			) or not proj.startswith(('script+', 'project+', 'packed+', 'git+')):
				err_msgs += [
					f"**Two Paths Given**: Both `PROJ` ('{proj}') and `--path` ('{path}') are given.",
					'> There are two ways to locate a `blext` extension by path:',
					'> 1. Specify `PROJ` (ex. `path/to/script.py`).',
					'> 2. Specify `--path` explicitly.',
					'>',
					'> _Exactly one must be given._',
					'',
				]

			####################
			# - Project String: Git
			####################
			case (str() as proj, None, None, GitLocationUI() as git) if (
				proj.startswith('git+') and git.url is None
			):
				kwargs['git']['url'] = proj.removeprefix('git+')

			case (str() as proj, None, None, None as git) if proj.startswith('git+'):
				kwargs['git'] = {'url': proj.removeprefix('git+')}

			case (str() as proj, _, _, GitLocationUI() as git) if (
				proj.startswith('git+') and git.url is not None
			):
				err_msgs += [
					f"**Two `git` URLs Given**: Both `PROJ` ('{proj}') and `--git.url` ('{git.url}') are given.",
					'> There are two ways to locate a `blext` extension by `git`:',
					'> 1. Specify `PROJ` (ex. `git+https://example.org/repo.git`).',
					'> 2. Specify `--git.url` explicitly.',
					'>',
					'> _Exactly one must be given._',
					'',
				]

			####################
			# - Project String: Unprefixed
			####################
			# URL
			case (str() as proj, None, None, None) if proj.startswith('http'):
				kwargs['url'] = proj

			# Path: Detect
			case (str() as proj, None, None, None) if Path(proj).exists():
				kwargs['path'] = proj

			####################
			# - Project String: Handle Errors
			####################
			case (str() as proj, None, None, None):
				err_msgs += [
					f'**Invalid `PROJ`**: `{proj}` does not exist, or is not specified correctly.',
					*ERR_VALID_PROJS,
				]

			case (str() as proj, _, _, _):
				err_msgs += [
					'**Invalid Location**: There is not one, unambiguous location to search for a `blext` project.',
					f'> **Implicit Location** (`PROJ`): `{proj}`',
					'>',
					'> **Explicit Locations** (`--<options>`):',
					*[
						f'> - `{name}`: `{spec}`'
						for name, spec in {
							'--path': self.path if self.path is not None else '...',
							'--url': self.url if self.url is not None else '...',
							'--git': self.git if self.git is not None else '...',
						}.items()
					],
					'>',
					'> _Only one location may be given._',
					'',
					*ERR_EXPLAIN_PROJ,
					# *ERR_VALID_PROJS,
				]

		if err_msgs:
			raise ValueError(*err_msgs)

		return self.__class__(**kwargs)  # pyright: ignore[reportAny]
