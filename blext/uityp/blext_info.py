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
import tomlkit
import tomlkit.items
from frozendict import frozendict

from blext import extyp, pydeps
from blext.blext_spec import BLExtSpec
from blext.utils.inline_script_metadata import (
	parse_inline_script_metadata_str,
	replace_inline_script_metadata_str,
)
from blext.utils.lru_method import lru_method

from .global_config import GlobalConfig

####################
# - Constants
####################
TOML_MANAGED_COMMENTS = (
	tomlkit.comment('⭳⭳⭳ MANAGED BY BLEXT ⭳⭳⭳'),
	tomlkit.comment('⭱⭱⭱ MANAGED BY BLEXT ⭱⭱⭱'),
)

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

	bl_version: typ.Annotated[
		tuple[extyp.BLReleaseOfficial | typ.Literal['detect'], ...],
		cyclopts.Parameter(
			group=SPECIFICATION_GROUP,
			env_var='BLEXT_BL_VERSION',
			negative=[],
		),
	] = ()
	platform: typ.Annotated[
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
	@lru_method()
	def requested_bl_versions(
		self, global_config: GlobalConfig
	) -> frozenset[extyp.BLVersion]:
		"""Set of granular `BLVersion`s that the user requested."""
		return frozenset({
			global_config.local_default_bl_version
			if bl_release == 'detect'
			else bl_release.bl_version
			for bl_release in self.bl_version
		})

	@lru_method()
	def requested_bl_platforms(
		self, global_config: GlobalConfig
	) -> frozenset[extyp.BLPlatform]:
		"""Set of BLPlatforms that the user requested."""
		return frozenset({
			global_config.local_bl_platform if bl_platform == 'detect' else bl_platform
			for bl_platform in self.platform
		})

	@lru_method()
	def blext_location(self, global_config: GlobalConfig) -> extyp.BLExtLocation:
		"""Extension location that the user requested.

		Notes:
			- Essentially a convenient way of calling `blext.finders.find_proj_spec`.
			- The "abstract location" returned exposes a standard interface for getting ex. the path to the extension specification.
			To achieve this functionality, it might first ex. download a URL, clone a git repository, etc. .


		Parameters:
			global_config: Global configuration.

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

	@lru_method()
	def blext_spec(self, global_config: GlobalConfig) -> BLExtSpec:
		"""Load the extension specification.

		Notes:
			- Uses `self.blext_location` internally.
			- Runs `blext_spec.set_bl_platforms(self.request_bl_platforms)` after loading succeeds.

		Parameters:
			global_config: Global configuration.

		See Also:
			- `blext.location.BLExtLocation`: Abstract location of a Blender extension.
			- `blext.finders.find_proj_spec`: Find a project by its URI, returning a location.
		"""
		blext_location = self.blext_location(global_config=global_config)

		# Load BLExtSpec
		## Also, update project specification.
		blext_spec = BLExtSpec.from_proj_spec_path(
			blext_location.path_spec,
			path_uv_exe=global_config.path_uv_exe,
			release_profile_id=self.profile,
		)
		if self.update_proj_spec(global_config, blext_spec=blext_spec):
			pydeps.uv.update_uv_lock(
				blext_location.path_uv_lock,
				path_uv_exe=global_config.path_uv_exe,
			)
			blext_spec = BLExtSpec.from_proj_spec_path(
				blext_location.path_spec,
				path_uv_exe=global_config.path_uv_exe,
				release_profile_id=self.profile,
			)
		return blext_spec

	@lru_method()
	def bl_versions(self, global_config: GlobalConfig) -> tuple[extyp.BLVersion, ...]:
		"""All selected Blender versions."""
		blext_spec = self.blext_spec(global_config)

		requested_bl_versions = self.requested_bl_versions(global_config)
		if not requested_bl_versions:
			return blext_spec.sorted_bl_versions

		# Select Maximally Smooshed BLVersions
		## We must also verify that the desired BLVersion works with the ext.
		bl_versions = set[extyp.BLVersion]()
		for requested_bl_version in requested_bl_versions:
			if requested_bl_version in blext_spec.granular_bl_versions:
				bl_versions.add(
					blext_spec.bl_versions_by_granular[requested_bl_version]
				)
			else:
				msgs = [
					f'Requested Blender version `{requested_bl_version.pretty_version}` is not supported by this extension.',
					'> **Supported Blender Versions**:',
					*[
						f'> - {bl_version.pretty_version}'
						for bl_version in blext_spec.sorted_bl_versions
					],
					'>',
					'> **Remedies**:',
					'> 1. Select an extension-supported `BLVersion`.',
					f'> 2. Alter the extension to support `{requested_bl_version.pretty_version}`.',
				]
				raise ValueError(*msgs)

		return tuple(
			(
				bl_version
				if bl_version in blext_spec.bl_versions
				else blext_spec.bl_versions_by_granular[bl_version]
			)
			for bl_version in requested_bl_versions
		)

	@lru_method()
	def bl_platforms(
		self, global_config: GlobalConfig
	) -> tuple[extyp.BLPlatformSet, ...]:
		"""All selected Blender versions."""
		blext_spec = self.blext_spec(global_config)

		requested_bl_platforms = self.requested_bl_platforms(global_config)
		if not requested_bl_platforms:
			return blext_spec.sorted_bl_platforms

		# Select Maximally Smooshed BLVersions
		## We must also verify that the desired BLVersion works with the ext.
		bl_platforms = set[extyp.BLPlatformSet]()
		for requested_bl_platform in requested_bl_platforms:
			if requested_bl_platform in blext_spec.granular_bl_platforms:
				bl_platforms.add(
					blext_spec.bl_platforms_by_granular[requested_bl_platform]
				)
			else:
				msgs = [
					f'Requested platform `{requested_bl_platform}` is not supported by this extension.',
					'> **Supported Blender Platforms**:',
					*[
						f'> - {bl_platform}'
						for bl_platform in blext_spec.sorted_bl_platforms
					],
					'>',
					'> **Remedies**:',
					'> 1. Select an extension-supported `BLPlatform`.',
					f'> 2. Alter the extension to support `{requested_bl_platform}`.',
				]
				raise ValueError(*msgs)

		return tuple(
			bl_platform
			for bl_platform in blext_spec.bl_platforms
			if bl_platform in bl_platforms
		)

	####################
	# - Zip Paths
	####################
	@lru_method()
	def path_zip_prepacks(
		self, global_config: GlobalConfig
	) -> frozendict[extyp.BLVersion, frozendict[extyp.BLPlatformSet, Path]]:
		"""Paths of all extension pre-packed archives that should be prepared from `self.blext_spec`.

		Parameters:
			global_config: Global configuration parameters.

		Returns:
			Mapping from `BLVersion` to the corresponding `Path` to prepare pre-packed archive for that version (chunk) at.
		"""
		blext_location = self.blext_location(global_config)
		blext_spec = self.blext_spec(global_config)

		return blext_spec.extension_zip_paths(
			path_base=blext_location.path_prepack_cache
		)

	@lru_method()
	def path_zips(
		self, global_config: GlobalConfig
	) -> frozendict[extyp.BLVersion, frozendict[extyp.BLPlatformSet, Path]]:
		"""Paths of all extension `.zip`s that should be built from `self.blext_spec`.

		Parameters:
			global_config: Global configuration parameters.

		Returns:
			Mapping from `BLVersion` to the corresponding `Path` to build the extension for that version (chunk) at.
		"""
		blext_location = self.blext_location(global_config)
		blext_spec = self.blext_spec(global_config)

		return blext_spec.extension_zip_paths(path_base=blext_location.path_build_cache)

	@lru_method()
	def path_final_zips(
		self, global_config: GlobalConfig
	) -> frozendict[extyp.BLVersion, frozendict[extyp.BLPlatformSet, Path]]:
		"""Paths of all extension `.zip`s that should be built from `self.blext_spec`.

		Parameters:
			global_config: Global configuration parameters.

		Returns:
			Mapping from `BLVersion` to the corresponding `Path` to build the extension for that version (chunk) at.
		"""
		blext_location = self.blext_location(global_config)
		blext_spec = self.blext_spec(global_config)

		return blext_spec.extension_zip_paths(path_base=blext_location.path_build)

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

			case (str() as proj, _, str() as url, _) if proj.startswith((
				'script+http',
				'packed+http',
				'http',
			)):
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

			case (str() as proj, Path() as path, _, _) if proj.startswith((
				'script+',
				'packed+',
			)) or not proj.startswith(('script+', 'project+', 'packed+', 'git+')):
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

	####################
	# - Modify Project Specification
	####################
	def update_proj_spec(  # noqa: C901, PLR0912, PLR0915
		self, global_config: GlobalConfig, *, blext_spec: BLExtSpec
	) -> bool:
		"""Update a project specification to take vendored `site-packages` into account from all supported Blender versions."""
		altered_spec = False

		blext_location = self.blext_location(global_config=global_config)
		all_extras = {
			(
				pymarker_extra.replace(
					'-', '_'
				),  ## '-'/'_' differ between uv.lock/pyproject.toml
				bl_version.vendored_site_packages,
			)
			for bl_version in sorted(blext_spec.bl_versions)
			for pymarker_extra in bl_version.pymarker_extras
		}
		if len({extra[0] for extra in all_extras}) < len(all_extras):
			msg = 'In BLReleaseOfficial, two entries with identical `pymarker_extra`s have differing `vendored_site_packages`. Please report this as a bug in `blext`.'
			raise RuntimeError(msg)

		if blext_location.path_spec.name == 'pyproject.toml':
			####################
			# - Stage 0: Handle Blender Versions in [projects.optional-dependencies]
			####################
			with blext_location.path_spec.open('r') as f:
				doc = tomlkit.parse(f.read())

			original_doc = tomlkit.dumps(doc)  # pyright: ignore[reportUnknownMemberType]

			# The user must already have defined a `[project]` table.
			## If it's not a table, then that's an error.
			## Otherwise, `pyproject.toml` isn't valid.
			if 'project' not in doc:
				msgs = [
					'In `pyproject.toml`, `[project]` does not exists.',
					'> Please define the `[project]` table.',
				]
				raise ValueError(*msgs)
			if not isinstance(doc['project'], tomlkit.items.Table):
				msgs = [
					"In `pyproject.toml`, `[project]` exists, but isn't a table.",
					'> Please define `[project]` as a table.',
				]
				raise ValueError(*msgs)

			# The user need not have defined optional-dependencies - otherwise we do it for them.
			## If it isn't a table, then that's an error.
			if 'optional-dependencies' not in doc['project']:  # pyright: ignore[reportOperatorIssue]
				doc['project']['optional-dependencies'] = tomlkit.table()  # pyright: ignore[reportIndexIssue]
			elif not isinstance(
				doc['project']['optional-dependencies'],  # pyright: ignore[reportIndexIssue]
				tomlkit.items.Table,
			):
				msg = "In `pyproject.toml`, `[project.optional-dependencies]` exists, but isn't a table."
				raise ValueError(msg)

			# Now we iterate over all the extras aka. Blender versions with vendored pydep versions.
			for extra in sorted(all_extras, key=lambda el: el[0]):
				extra_name = extra[0]
				vendored_site_packages = [
					f'{pkg_name}=={pkg_version!s}'
					for pkg_name, pkg_version in extra[1].items()
				]  ## Use explicit `==` to precisely match what Blender ships with

				# If 'extra_name' is already there, we need to be very precise.
				## Since pyproject.toml is user-authored, we must be careful to preserve styling.
				if extra_name not in doc['project']['optional-dependencies']:  # pyright: ignore[reportOperatorIssue, reportIndexIssue]
					doc['project'][  # pyright: ignore[reportIndexIssue, reportUnknownMemberType, reportUnusedCallResult]
						'optional-dependencies'
					].append(  # pyright: ignore[reportAttributeAccessIssue]
						extra_name,
						tomlkit.array(),
					)

				# The 'extras' dependency group must be an array.
				if not isinstance(
					doc['project']['optional-dependencies'][extra_name],  # pyright: ignore[reportIndexIssue]
					tomlkit.items.Array,
				):
					msgs = [
						f"In `pyproject.toml`, `project.optional-dependencies.{extra_name}` exists, but isn't an array.",
						f'> **Value**: `{doc["project"]["optional-dependencies"][extra_name]}`',  # pyright: ignore[reportIndexIssue]
					]
					raise TypeError(*msgs)

				# All elements of that array must be strings.
				if not all(
					isinstance(el, str)
					for el in doc['project']['optional-dependencies'][extra_name]  # pyright: ignore[reportIndexIssue, reportGeneralTypeIssues, reportUnknownVariableType]
				):
					msgs = [
						f"In `pyproject.toml`, `project.optional-dependencies.{extra_name}` exists, but isn't an array.",
						f'> **Value**: `{doc["project"]["optional-dependencies"][extra_name]}`',  # pyright: ignore[reportIndexIssue]
					]
					raise ValueError(*msgs)

				# We must delete those retained strings that conflict with vendored_site_packages.
				## Why not error? If the user sets an incompatible version, they're wrong.
				## By considering it "managed", we don't have to bug the user for a rote fix.
				## This also naturally allows non-conflicting user deps to "float to the top".
				## Be good to the user, for they are benevolent.
				pydep_strs_to_delete: set[str] = {
					current_pydep_str
					for current_pydep_str in doc['project']['optional-dependencies'][  # pyright: ignore[reportIndexIssue, reportGeneralTypeIssues, reportUnknownVariableType]
						extra_name
					]
					if any(
						current_pydep_str.startswith(pkg_name)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
						for pkg_name in extra[1]
					)
				}
				for pydep_str_to_delete in pydep_strs_to_delete:
					_ = doc['project']['optional-dependencies'][extra_name].remove(  # pyright: ignore[reportIndexIssue, reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
						pydep_str_to_delete
					)

				# Finally, all vendored site-packages are dumped to the TOML
				## Why not error? If the user sets an incompatible version, they're wrong.
				for i, pydep_str in enumerate(vendored_site_packages):
					if i == 0:
						comment = TOML_MANAGED_COMMENTS[0]
					elif i == len(vendored_site_packages) - 1:
						comment = TOML_MANAGED_COMMENTS[1]
					else:
						comment = None

					doc['project']['optional-dependencies'][extra_name].add_line(  # pyright: ignore[reportIndexIssue, reportAttributeAccessIssue, reportUnknownMemberType]
						pydep_str,
						comment=comment,
						indent=' ' * 4,
					)

				doc['project']['optional-dependencies'][extra_name].multiline(True)  # pyright: ignore[reportIndexIssue, reportAttributeAccessIssue, reportUnknownMemberType]

			####################
			# - Stage 1: Handle Extra Conflicts in [tool.uv]
			####################
			# The extras are not supplementary - they are mutually exclusive.
			## We can tell 'uv' about this situation by setting tool.uv.conflicts correctly.
			if 'tool' not in doc and 'uv' not in doc['tool']:  # pyright: ignore[reportOperatorIssue]
				msgs = [
					'In `pyproject.toml`, `[tool.uv]` does not exists.',
					'> Please define the `[tool.uv]` table.',
				]
				raise ValueError(*msgs)

			# Make sure tool.uv.package is False.
			## As far as uv is concerned, extensions are virtual packages.
			if doc['tool']['uv'].get('package', True):  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportIndexIssue]
				msgs = [
					'In `pyproject.toml`, `tool.uv.package` is either undefined or `true`.',
					'> `blext` projects must define `tool.uv.package = false`.',
					'>',
					'> **See**: <https://docs.astral.sh/uv/reference/settings/#package>',
				]
				raise ValueError(*msgs)

			# Create tool.uv.conflicts if it doesn't exist.
			if 'conflicts' not in doc['tool']['uv']:  # pyright: ignore[reportIndexIssue, reportOperatorIssue]
				doc['tool']['uv']['conflicts'] = tomlkit.array()  # pyright: ignore[reportIndexIssue]

			# Ensure tool.uv.conflicts is an array.
			if not isinstance(doc['tool']['uv']['conflicts'], tomlkit.items.Array):  # pyright: ignore[reportIndexIssue]
				msgs = [
					"In `pyproject.toml`, `tool.uv.conflicts` exists, but isn't an array.",
					'> Please define `tool.uv.conflicts` as an array.',
				]
				raise ValueError(*msgs)

			# Scan conflicts array for those with only { extra = <extra in all_extras> }
			## These should be removed, as they are redundant together with what we're adding.
			all_extra_names = {extra[0] for extra in all_extras}
			conflict_idxs_to_remove = {
				i
				for i, conflict_spec_arr in enumerate(doc['tool']['uv']['conflicts'])  # pyright: ignore[reportUnknownVariableType, reportIndexIssue, reportArgumentType]
				if all(
					# There exactly one key specifying the conflicting element.
					len(conflict_spec_table) == 1  # pyright: ignore[reportUnknownArgumentType]
					# That one key is 'extra'.
					and conflict_spec_table.get('extra') is not None  # pyright: ignore[reportUnknownMemberType]
					# The output of that key is one of the extra names.
					and conflict_spec_table['extra'] in all_extra_names
					for conflict_spec_table in conflict_spec_arr  # pyright: ignore[reportUnknownVariableType]
				)
			}
			for idx_to_remove in sorted(conflict_idxs_to_remove, reverse=True):
				_ = doc['tool']['uv']['conflicts'].pop(idx_to_remove)  # pyright: ignore[reportIndexIssue, reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]

			# Add the conflicts entry line by line.
			## These should be removed, as they are redundant together with what we're adding.
			if len(all_extras) > 1:
				conflict_spec_arr_to_add = tomlkit.array()
				for i, extra in enumerate(sorted(all_extras, key=lambda el: el[0])):
					extra_name = extra[0]

					extra_conflict_table = tomlkit.inline_table()
					extra_conflict_table['extra'] = extra_name

					if i == 0:
						comment = TOML_MANAGED_COMMENTS[0]
					elif i == len(all_extras) - 1:
						comment = TOML_MANAGED_COMMENTS[1]
					else:
						comment = None

					conflict_spec_arr_to_add.add_line(
						extra_conflict_table,
						indent=' ' * 8,
						comment=comment,  # pyright: ignore[reportArgumentType]
					)
				_ = conflict_spec_arr_to_add.multiline(True)
				conflict_spec_arr_to_add._trivia.indent = ' ' * 4  # pyright: ignore[reportPrivateUsage] # noqa: SLF001

				doc['tool']['uv']['conflicts'].add_line(  # pyright: ignore[reportAttributeAccessIssue, reportIndexIssue, reportUnknownMemberType]
					conflict_spec_arr_to_add,
					indent=' ' * 4,
				)
				doc['tool']['uv']['conflicts'].multiline(True)  # pyright: ignore[reportAttributeAccessIssue, reportIndexIssue, reportUnknownMemberType]

			if original_doc != tomlkit.dumps(doc):  # pyright: ignore[reportUnknownMemberType]
				with blext_location.path_spec.open('w') as f:
					_ = f.write(tomlkit.dumps(doc))  # pyright: ignore[reportUnknownMemberType]

				altered_spec = True

		elif blext_location.path_spec.name.endswith('.py'):
			# Check for single smooshed version
			if len(all_extras) != 1:
				msgs = [
					'Script extensions may not support more than one "smooshable" version of Blender.'
				]
				raise ValueError(*msgs)

			vendored_site_packages = next(iter(extra[1] for extra in all_extras))

			# Load the inline script metadata
			with blext_location.path_spec.open('r') as f:
				py_source_code = f.read()
				doc_str = parse_inline_script_metadata_str(
					py_source_code=py_source_code
				)

			# Ensure there's inline script metadata actually available
			if doc_str is None:
				msg = f'No inline script metadata found in script extension: {blext_location.path_spec}'
				raise ValueError(msg)

			# Load the document.
			doc = tomlkit.parse(doc_str)

			####################
			# - Stage 0: Handle Vendored site-package in 'dependencies'
			####################
			if 'dependencies' not in doc:
				msg = f'No `dependencies` field found in inline script metadata: {blext_location.path_spec}'
				raise ValueError(msg)
			pydep_strs_to_delete_from_script: set[str] = {
				current_pydep_str
				for current_pydep_str in doc['dependencies']  # pyright: ignore[reportGeneralTypeIssues, reportUnknownVariableType]
				if any(
					current_pydep_str.startswith(pkg_name)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
					for pkg_name in vendored_site_packages
				)
			}
			for pydep_str_to_delete in pydep_strs_to_delete_from_script:
				_ = doc['dependencies'].remove(  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
					pydep_str_to_delete
				)

			# All vendored site-packages are dumped to the TOML
			## Why not error? If the user sets an incompatible version, they're wrong.
			for i, pydep_str in enumerate([
				f'{pkg_name}=={pkg_version!s}'
				for pkg_name, pkg_version in vendored_site_packages.items()
			]):
				if i == 0:
					comment = TOML_MANAGED_COMMENTS[0]
				elif i == len(vendored_site_packages) - 1:
					comment = TOML_MANAGED_COMMENTS[1]
				else:
					comment = None

				doc['dependencies'].add_line(  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
					pydep_str,
					comment=comment,
					indent=' ' * 4,
				)

			doc['dependencies'].multiline(True)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
			if doc_str != tomlkit.dumps(doc):  # pyright: ignore[reportUnknownMemberType]
				new_py_source_code = replace_inline_script_metadata_str(
					py_source_code=py_source_code,
					metadata_str=tomlkit.dumps(doc),  # pyright: ignore[reportUnknownMemberType]
				)
				with blext_location.path_spec.open('w') as f:
					_ = f.write(new_py_source_code)

				altered_spec = True

		return altered_spec
