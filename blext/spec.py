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

"""Defines the Blender extension specification."""

import functools
import json
import tomllib
import typing as typ
from pathlib import Path

import annotated_types as atyp
import pydantic as pyd
import tomli_w
from frozendict import deepfreeze, frozendict
from pydantic_extra_types.semantic_version import SemanticVersion

from . import extyp
from .pydeps import BLExtDeps, PyDep, PyDepWheel, uv
from .utils.inline_script_metadata import parse_inline_script_metadata
from .utils.pydantic_frozendict import FrozenDict


####################
# - Blender Extension Specification
####################
class BLExtSpec(pyd.BaseModel, frozen=True):
	"""Specifies a Blender extension.

	This model allows `pyproject.toml` to be the single source of truth for a Blender extension project.
	Thus, this model is designed to be parsed entirely from a `pyproject.toml` file, and in turn is capable of generating the Blender extension manifest file and more.

	To the extent possible, appropriate standard `pyproject.toml` fields are scraped for information relevant to a Blender extension. | None = None
	This includes name, version, license, desired dependencies, homepage, and more.
	Naturally, many fields are _quite_ specific to Blender extensions, such as Blender version constraints, permissions, and extension tags.
	For such options, the `[tool.blext]` section is introduced.

	Attributes:
		wheels_graph: All wheels that might be usable by this extension.
		release_profile: Optional initialization settings and spec overrides.
			**Overrides must be applied during construction**.
		id: Unique identifying name of the extension.
		name: Pretty, user-facing name of the extension.
		version: The version of the extension.
		tagline: Short description of the extension.
		maintainer: Primary maintainer of the extension (name and email).
		type: Type of extension.
			Currently, only `add-on` is supported.
		blender_version_min: The minimum version of Blender that this extension supports.
		blender_version_max: The maximum version of Blender that this extension supports.
		wheels: Relative paths to wheels distributed with this extension.
			These should be installed by Blender alongside the extension.
			See <https://docs.blender.org/manual/en/dev/extensions/python_wheels.html> for more information.
		permissions: Permissions required by the extension.
		tags: Tags for categorizing the extension.
		license: License of the extension's source code.
		copyright: Copyright declaration of the extension.
		website: Homepage of the extension.

	References:
		- <https://docs.blender.org/manual/en/4.2/extensions/getting_started.html>
		- <https://packaging.python.org/en/latest/guides/writing-pyproject-toml>
	"""

	####################
	# - Fields
	####################
	# Required
	id: str
	name: str
	tagline: str
	version: SemanticVersion
	blender_version_min: typ.Annotated[
		str,
		pyd.StringConstraints(
			pattern=r'^[4-9]+\.[2-9]+\.[0-9]+$',
		),
	]

	# Optional
	blender_version_max: (
		typ.Annotated[
			str,
			pyd.StringConstraints(
				pattern=r'^[4-9]+\.[2-9]+\.[0-9]+$',
			),
		]
		| None
	) = None
	bl_platforms: typ.Annotated[frozenset[extyp.BLPlatform], atyp.MinLen(1)]
	permissions: (
		FrozenDict[
			typ.Literal['files', 'network', 'clipboard', 'camera', 'microphone'],
			str,
		]
		| None
	) = None
	copyright: tuple[str, ...] | None = None
	maintainer: str | None = None
	tags: frozenset[str] | None = None
	website: pyd.HttpUrl | None = None
	license: tuple[extyp.SPDXLicense, ...] | None = None

	# Environment
	deps: BLExtDeps
	release_profile: extyp.ReleaseProfile | None = None

	####################
	# - Core Attributes
	####################
	@functools.cached_property
	def bl_versions(self) -> frozenset[extyp.BLVersion]:
		"""All Blender versions supported by this extension.

		Warnings:
			`blext` doesn't support official Blender versions released after a particular `blext` version was published.

			This is because `blext` has no way of knowing critical information about such future releases, ex. the versions of vendored `site-packages` dependencies.

		Notes:
			Derived by comparing `self.blender_version_min` and `self.blender_version_max` to hard-coded Blender versions that have already been released, whose properties are known.
		"""
		granular_bl_versions = sorted(
			{
				released_bl_version.bl_version
				for released_bl_version in extyp.BLReleaseOfficial.from_official_version_range(
					self.blender_version_min, self.blender_version_max
				)
			},
			key=lambda el: el.source.blender_version_min,  ## Sort by theoretical BLVersion
			## TODO: Use a tuple w/release datetime to distinguish identical bl_version_min.
			## - This is mainly important to get sequential git commits.
			## - This also presumes that nobody messses with the version in said git commits.
		)

		idx_smoosh = 0
		smooshed_bl_versions: list[extyp.BLVersion] = [granular_bl_versions[0]]
		for granular_bl_version in granular_bl_versions:
			if smooshed_bl_versions[idx_smoosh].is_smooshable_with(granular_bl_version):
				smooshed_bl_versions[idx_smoosh] = smooshed_bl_versions[
					idx_smoosh
				].smoosh_with(granular_bl_version)
			else:
				smooshed_bl_versions.append(granular_bl_version)
				idx_smoosh += 1

		return frozenset(smooshed_bl_versions)

	@functools.cached_property
	def is_universal(self) -> bool:
		"""Whether this extension is works on all platforms of all supported Blender versions.

		Notes:
			Pure-Python extensions that only use pure-Python dependencies are considered "universal".

			Once any non-pure-Python wheels are introduced, this condition may become very difficult to uphold, depending on which wheels are available for supported platforms.
		"""
		return all(
			bl_version.valid_bl_platforms.issubset(self.bl_platforms)
			for bl_version in self.bl_versions
		)

	@functools.cached_property
	def pydeps(
		self,
	) -> frozendict[extyp.BLVersion, frozenset[PyDep]]:
		"""Python dependencies by (smooshed) Blender version and Blender platform."""
		return frozendict(
			{
				bl_version: frozenset(
					{
						self.deps.pydeps_by(
							pkg_name=self.id,
							bl_version=bl_version,
							bl_platform=bl_platform,
						)
						for bl_platform in self.bl_platforms
					}
				)
				for bl_version in self.bl_versions
			}
		)

	@functools.cached_property
	def wheels(
		self,
	) -> frozendict[extyp.BLVersion, frozenset[PyDepWheel]]:
		"""Python wheels by (smooshed) Blender version and Blender platform."""
		return frozendict(
			{
				bl_version: frozenset(
					{
						self.deps.wheels_by(
							pkg_name=self.id,
							bl_version=bl_version,
							bl_platform=bl_platform,
						)
						for bl_platform in self.bl_platforms
					}
				)
				for bl_version in self.bl_versions
			}
		)

	@functools.cached_property
	def bl_versions_by_wheel(
		self,
	) -> frozendict[PyDepWheel, frozenset[extyp.BLVersion]]:
		"""Blender versions by wheel."""
		all_wheels = {wheel for wheels in self.wheels.values() for wheel in wheels}
		return frozendict(
			{
				wheel: frozenset(
					{
						bl_version
						for bl_version in self.bl_versions
						if wheel in self.wheels[bl_version]
					}
				)
				for wheel in all_wheels
			}
		)

	def bl_manifest(
		self,
		bl_manifest_version: extyp.BLManifestVersion,
		*,
		bl_version: extyp.BLVersion,
	) -> extyp.BLManifest:
		"""Export the Blender extension manifest.

		Warnings:
			Only `fmt='toml'` results in valid contents of `blender_manifest.toml`.
			_This is also the default._

			Other formats are included to enable easier interoperability with other systems - **not** with Blender.

		Parameters:
			fmt: String format to export Blender manifest to.

		Returns:
			String representing the Blender extension manifest.

		Raises:
			ValueError: When `fmt` is unknown.
		"""
		_empty_frozenset: frozenset[PyDepWheel] = frozenset()
		match bl_manifest_version:
			case extyp.BLManifestVersion.V1_0_0:
				return extyp.BLManifest_1_0_0(
					id=self.id,
					name=self.name,
					version=str(self.version),
					tagline=self.tagline,
					maintainer=self.maintainer,
					blender_version_min=bl_version.source.blender_version_min,
					blender_version_max=bl_version.source.blender_version_max,
					permissions=self.permissions,
					platforms=sorted(self.bl_platforms),  # pyright: ignore[reportArgumentType]
					tags=(tuple(sorted(self.tags)) if self.tags is not None else None),
					license=self.license,
					copyright=self.copyright,
					website=str(self.website) if self.website is not None else None,
					wheels=tuple(
						sorted(
							[
								f'./wheels/{wheel.filename}'
								for wheel in self.wheels[bl_version]
							]
						)
					)
					if len(self.wheels[bl_version]) > 0
					else None,
				)

	####################
	# - Exporters
	####################
	def export_extension_filenames(
		self,
		with_bl_version: bool = True,
		with_bl_platforms: bool = True,
	) -> frozendict[extyp.BLVersion, str]:
		"""Default filename of the extension zipfile."""
		extension_filenames: dict[extyp.BLVersion, str] = {}
		for bl_version in self.bl_versions:
			basename = f'{self.id}__{self.version}'

			if with_bl_version:
				basename += f'__{bl_version.version}'

			if with_bl_platforms:
				basename += '__' + '_'.join(self.bl_platforms)

			extension_filenames[bl_version] = f'{basename}.zip'
		return frozendict(extension_filenames)

	def export_blender_manifest(
		self,
		bl_manifest_version: extyp.BLManifestVersion,
		*,
		bl_version: extyp.BLVersion,
		fmt: typ.Literal['json', 'toml'],
	) -> str:
		"""Export the Blender extension manifest.

		Warnings:
			Only `fmt='toml'` results in valid contents of `blender_manifest.toml`.
			_This is also the default._

			Other formats are included to enable easier interoperability with other systems - **not** with Blender.

		Parameters:
			fmt: String format to export Blender manifest to.

		Returns:
			String representing the Blender extension manifest.

		Raises:
			ValueError: When `fmt` is unknown.
		"""
		# Dump Manifest to Formatted String
		bl_manifest = self.bl_manifest(bl_manifest_version, bl_version=bl_version)
		if isinstance(bl_manifest, pyd.BaseModel):
			manifest_export: dict[str, typ.Any] = bl_manifest.model_dump(
				mode='json', exclude_none=True
			)
			if fmt == 'json':
				return json.dumps(manifest_export)
			if fmt == 'toml':
				return tomli_w.dumps(manifest_export)

		msg = '`bl_manifest` is not an instance of `pyd.BaseModel`. This should not happen.'
		raise RuntimeError(msg)

	####################
	# - Replace Methods
	####################
	def replace_bl_platforms(
		self, bl_platforms: frozenset[extyp.BLPlatform]
	) -> typ.Self:
		"""Create a copy of this extension spec, with altered platform support.

		Notes:
			By default, an extension specification defines a wide range of supported platforms.

			Sometimes, it's important to consider the same extension defined only for a subset of platforms (for example, to build the extension only for Windows).
			This amounts to a "new extension", which can be generated using this method.

		Parameters:
			bl_platform: The Blender platform to support exclusively.
				- `frozenset[BLPlatform]`: Directly write to `self.bl_platforms`.
				- `set[BLPlatform]`: Directly write to `self.bl_platforms`.
				- `BLPlatform`: Place in a single-element set.

		Returns:
			A copy of `self`, with the following modifications:
				- `self.wheels_graph.valid_bl_platforms`: Modified according to parameters.

			In practice, `self.bl_platforms` will also reflect the change.l

		"""
		if bl_platforms.issubset(self.bl_platforms):
			return self.model_copy(
				update={
					'bl_platforms': bl_platforms,
				},
				deep=True,
			)

		msg = "Can't set BLPlatforms that aren't already supported by an extension."
		raise ValueError(msg)

	####################
	# - Wheels to Download
	####################
	def cached_wheels(
		self,
		*,
		path_wheels: Path,
		bl_versions: frozenset[extyp.BLVersion] | None = None,
	) -> frozenset[PyDepWheel]:
		"""Wheels that have already been correctly downloaded."""
		bl_versions = self.bl_versions if bl_versions is None else bl_versions

		return frozenset(
			{
				wheel
				for bl_version in bl_versions
				for bl_platform in self.bl_platforms
				for wheel in self.deps.wheels_by(
					pkg_name=self.id,
					bl_version=bl_version,
					bl_platform=bl_platform,
				)
				if wheel.is_download_valid(path_wheels / wheel.filename)
			}
		)

	def missing_wheels(
		self,
		*,
		path_wheels: Path,
		bl_versions: frozenset[extyp.BLVersion] | None = None,
	) -> frozenset[PyDepWheel]:
		"""Wheels that need to be downloaded, since they are not available / valid."""
		bl_versions = self.bl_versions if bl_versions is None else bl_versions

		return frozenset(
			{
				wheel
				for bl_version in bl_versions
				for bl_platform in self.bl_platforms
				for wheel in self.deps.wheels_by(
					pkg_name=self.id,
					bl_version=bl_version,
					bl_platform=bl_platform,
				)
				if not wheel.is_download_valid(path_wheels / wheel.filename)
			}
		)

	def wheel_paths_to_prepack(
		self, *, path_wheels: Path
	) -> frozendict[extyp.BLVersion, frozendict[Path, Path]]:
		"""Wheel file paths that should be pre-packed."""
		wheel_paths_to_prepack = {
			bl_version: {
				path_wheels / wheel.filename: Path('wheels') / wheel.filename
				for bl_platform in self.bl_platforms
				for wheel in self.deps.wheels_by(
					pkg_name=self.id,
					bl_version=bl_version,
					bl_platform=bl_platform,
				)
			}
			for bl_version in self.bl_versions
		}
		return deepfreeze(wheel_paths_to_prepack)  # pyright: ignore[reportAny]

	####################
	# - Creation
	####################
	@classmethod
	def from_proj_spec_dict(  # noqa: C901, PLR0912, PLR0915
		cls,
		proj_spec_dict: dict[str, typ.Any],
		*,
		path_uv_exe: Path,
		path_proj_spec: Path,
		release_profile_id: extyp.StandardReleaseProfile | str | None,
	) -> typ.Self:
		"""Parse an extension spec from a dictionary.

		Notes:
			- The dictionary is presumed to be loaded directly from either a `pyproject.toml` file or inline script metadata.
			Therefore, please refer to the `pyproject.toml` documentation for more on the dictionary's structure.

			- This method aims to "show its work", in explaining exactly why parsing fails.
			To provide pleasant user feedback, print `ValueError` arguments as Markdown.

		Parameters:
			proj_spec_dict: Dictionary representation of a `pyproject.toml` or inline script metadata.
			path_proj_spec: Path to the file that defines the extension project.
			release_profile_id: Identifier to deduce release profile settings with.
			path_uv_exe: Optional overriden path to a `uv` executable.
				_Generally sourced from `blext.ui.GlobalConfig.path_uv_exe`_.

		Raises:
			ValueError: If the dictionary cannot be parsed to a complete `BLExtSpec`.
				_Messages are valid Markdown_.

		"""
		is_proj_metadata = path_proj_spec.name == 'pyproject.toml'
		is_script_metadata = path_proj_spec.name.endswith('.py')

		####################
		# - Parsing: Stage 1
		####################
		###: Determine whether all required fields are accessible.

		# [project]
		if proj_spec_dict.get('project') is not None:
			project: dict[str, typ.Any] = proj_spec_dict['project']
		else:
			msgs = [
				f'**Invalid Extension Specification**: `{path_proj_spec}` exists, but has no `[project]` table.',
			]
			raise ValueError(*msgs)

		# [tool.blext]
		if (
			proj_spec_dict.get('tool') is not None
			and proj_spec_dict['tool'].get('blext') is not None  # pyright: ignore[reportAny]
			and isinstance(proj_spec_dict['tool']['blext'], dict)
		):
			blext_spec_dict: dict[str, typ.Any] = proj_spec_dict['tool']['blext']
		else:
			msgs = [
				'**Invalid Extension Specification**: No `[tool.blext]` table found.',
				f'> **Spec Path**: `{path_proj_spec}`',
				'>',
				'> **Suggestions**',
				'> - Is this project an extension?',
				'> - Add the `[tool.blext]` table. See the documentation for more.',
			]
			raise ValueError(*msgs)

		# [tool.blext.profiles]
		release_profile: None | extyp.ReleaseProfile = None
		if blext_spec_dict.get('profiles') is not None:
			project_release_profiles: dict[str, typ.Any] = blext_spec_dict['profiles']
			if release_profile_id in project_release_profiles:
				release_profile = extyp.ReleaseProfile(
					**project_release_profiles[release_profile_id]  # pyright: ignore[reportAny]
				)

		if release_profile is None and isinstance(
			release_profile_id, extyp.StandardReleaseProfile
		):
			release_profile = release_profile_id.release_profile

		elif release_profile_id is None:
			release_profile = None

		else:
			msgs = [
				'**Invalid Extension Specification**:',
				f'|    The selected "release profile" `{release_profile_id}` is not a standard release profile...',
				"|    ...and wasn't found in `[tool.blext.profiles]`.",
				'|',
				f'|    Please either define `{release_profile_id}` in `[tool.blext.profiles]`, or select a standard release profile.',
				'|',
				f'**Standard Release Profiles**: `{", ".join(extyp.StandardReleaseProfile)}`',
			]
			raise ValueError(*msgs)

		####################
		# - Parsing: Stage 2
		####################
		###: Parse values that require transformations.

		field_parse_errs: list[str] = []

		# project.requires-python
		project_requires_python: str | None = None
		if (is_proj_metadata and project.get('requires-python') is not None) or (
			is_script_metadata and proj_spec_dict.get('requires-python') is not None
		):
			if is_proj_metadata:
				requires_python_field = project['requires-python']  # pyright: ignore[reportAny]
			elif is_script_metadata:
				requires_python_field = proj_spec_dict['requires-python']  # pyright: ignore[reportAny]
			else:
				msg = 'BLExtSpec metadata is neither project nor script metadata. Something is very wrong.'
				raise RuntimeError(msg)

			if isinstance(requires_python_field, str):
				project_requires_python = requires_python_field.replace('~= ', '')
			else:
				field_parse_errs.append(
					f'- `project.requires-python` must be a string (current value: {project["requires-python"]})'
				)
		else:
			field_parse_errs.append('- `project.requires-python` is not defined.')

		# project.maintainers
		first_maintainer: dict[str, str] | None = None
		if project.get('maintainers') is not None:
			if isinstance(project['maintainers'], list):
				maintainers: list[typ.Any] = project['maintainers']
				if len(maintainers) > 0 and all(
					isinstance(maintainer, dict)
					and 'name' in maintainer
					and isinstance(maintainer['name'], str)
					and 'email' in maintainer
					and isinstance(maintainer['email'], str)
					for maintainer in maintainers  # pyright: ignore[reportAny]
				):
					first_maintainer = maintainers[0]
				else:
					field_parse_errs.append(
						f'- `project.maintainers` is malformed. It must be a **non-empty** list of dictionaries, where each dictionary has a "name: str" and an "email: str" field (current value: {maintainers}).'
					)
			else:
				field_parse_errs.append(
					f'- `project.maintainers` must be a list (current value: {project["maintainers"]})'
				)
		else:
			first_maintainer = {'name': 'Unknown', 'email': 'unknown@example.com'}

		# project.license
		extension_license: str | None = None
		if (
			project.get('license') is not None
			and isinstance(project['license'], dict)
			and project['license'].get('text') is not None  # pyright: ignore[reportUnknownMemberType]
			and isinstance(project['license']['text'], str)
		):
			extension_license = project['license']['text']
		else:
			field_parse_errs.append('- `project.license.text` is not defined.')
			field_parse_errs.append(
				'- Please note that all Blender addons MUST declare a GPL-compatible license: <https://docs.blender.org/manual/en/latest/advanced/extensions/licenses.html>'
			)

		## project.urls.homepage
		if (
			project.get('urls') is not None
			and isinstance(project['urls'], dict)
			and project['urls'].get('Homepage') is not None  # pyright: ignore[reportUnknownMemberType]
			and isinstance(project['urls']['Homepage'], str)
		):
			homepage = project['urls']['Homepage']
		else:
			homepage = None

		####################
		# - Parsing: Stage 3
		####################
		###: Parse field availability and provide for descriptive errors
		if blext_spec_dict.get('supported_platforms') is None:
			field_parse_errs += ['- `tool.blext.supported_platforms` is not defined.']
		if project.get('name') is None:
			field_parse_errs += ['- `project.name` is not defined.']
		if blext_spec_dict.get('pretty_name') is None:
			field_parse_errs += ['- `tool.blext.pretty_name` is not defined.']
		if project.get('version') is None:
			field_parse_errs += ['- `project.version` is not defined.']
		if project.get('description') is None:
			field_parse_errs += ['- `project.description` is not defined.']
		if blext_spec_dict.get('blender_version_min') is None:
			field_parse_errs += ['- `tool.blext.blender_version_min` is not defined.']
		if blext_spec_dict.get('blender_version_max') is None:
			field_parse_errs += ['- `tool.blext.blender_version_max` is not defined.']
		if blext_spec_dict.get('bl_tags') is None:
			field_parse_errs += ['- `tool.blext.bl_tags` is not defined.']
		if blext_spec_dict.get('copyright') is None:
			field_parse_errs += ['- `tool.blext.copyright` is not defined.']
			field_parse_errs += [
				'- Example: `copyright = ["<current_year> <proj_name> Contributors`'
			]

		if field_parse_errs:
			msgs = [
				f'In `{path_proj_spec}`:',
				*field_parse_errs,
			]
			raise ValueError(*msgs)

		####################
		# - Parsing: Stage 4
		####################
		###: Let pydantic take over the last stage of parsing.

		if (
			project_requires_python is None
			or extension_license is None
			or first_maintainer is None
		):
			msg = 'While parsing the project specification, some variables attained a theoretically impossible value. This is a serious bug, please report it!'
			raise RuntimeError(msg)

		# Compute Path to uv.lock
		if path_proj_spec.name == 'pyproject.toml':
			path_uv_lock = path_proj_spec.parent / 'uv.lock'
		elif path_proj_spec.name.endswith('.py'):
			path_uv_lock = path_proj_spec.parent / (path_proj_spec.name + '.lock')
		else:
			msg = f'Invalid project specification path: {path_proj_spec}. Please report this error as a bug.'
			raise RuntimeError(msg)

		_spec_params = {
			'wheels_graph': BLExtDeps.from_uv_lock(
				uv.parse_uv_lock(
					path_uv_lock,
					path_uv_exe=path_uv_exe,
				),
				module_name=project['name'],  # pyright: ignore[reportAny]
				min_glibc_version=blext_spec_dict.get('min_glibc_version'),
				min_macos_version=blext_spec_dict.get('min_macos_version'),
				valid_python_tags=blext_spec_dict.get('valid_python_tags'),
				valid_abi_tags=blext_spec_dict.get('valid_abi_tags'),
			),
			####################
			# - Init Settings
			####################
			'release_profile': release_profile,
			####################
			# - Blender Manifest
			####################
			# Basics
			'id': project['name'],
			'name': blext_spec_dict['pretty_name'],
			'version': project['version'],
			'tagline': project['description'],
			'maintainer': f'{first_maintainer["name"]} <{first_maintainer["email"]}>',
			# Blender Compatibility
			'blender_version_min': blext_spec_dict['blender_version_min'],
			'blender_version_max': blext_spec_dict['blender_version_max'],
			# Permissions
			'permissions': blext_spec_dict.get('permissions', {}),
			# Addon Tags
			'tags': blext_spec_dict['bl_tags'],
			'license': (f'SPDX:{extension_license}',),
			'copyright': blext_spec_dict['copyright'],
			'website': homepage,
		}

		# Inject Release Profile Overrides
		if release_profile is not None and release_profile.overrides:
			_spec_params.update(release_profile.overrides)
			return cls(**_spec_params)  # pyright: ignore[reportArgumentType]
		return cls(**_spec_params)  # pyright: ignore[reportArgumentType]

	@classmethod
	def from_proj_spec_path(
		cls,
		path_proj_spec: Path,
		*,
		path_uv_exe: Path,
		release_profile_id: extyp.StandardReleaseProfile | str | None,
	) -> typ.Self:
		"""Parse an extension specification from a compatible file.

		Args:
			path_proj_spec: Path to either a `pyproject.toml`, or `*.py` script with inline metadata.
			release_profile_id: Identifier for the release profile.
			path_uv_exe: Optional overriden path to a `uv` executable.
				_Generally sourced from `blext.ui.GlobalConfig.path_uv_exe`_.

		Raises:
			ValueError: If the `pyproject.toml` file cannot be loaded, or it does not contain the required tables and/or fields.
		"""
		if path_proj_spec.is_file():
			if path_proj_spec.name == 'pyproject.toml':
				with path_proj_spec.open('rb') as f:
					proj_spec_dict = tomllib.load(f)
			elif path_proj_spec.name.endswith('.py'):
				with path_proj_spec.open('r') as f:
					proj_spec_dict = parse_inline_script_metadata(
						py_source_code=f.read(),
					)

				if proj_spec_dict is None:
					msg = f'Could not find inline script metadata in "{path_proj_spec}" (looking for a `# /// script` block)`.'
					raise ValueError(msg)
			else:
				msg = f'Tried to load a Blender extension project specification from "{path_proj_spec}", but it is invalid: Only `pyproject.toml` and `*.py` scripts w/inline script metadata are supported.'
				raise ValueError(msg)
		else:
			msg = f'Tried to load a Blender extension project specification from "{path_proj_spec}", but no such file exists.'
			raise ValueError(msg)

		# Parse Extension Specification
		return cls.from_proj_spec_dict(
			proj_spec_dict,
			path_uv_exe=path_uv_exe,
			path_proj_spec=path_proj_spec,
			release_profile_id=release_profile_id,
		)

	####################
	# - Validation
	####################
	@pyd.model_validator(mode='before')
	@classmethod
	def set_default_bl_platforms_to_universal(cls, data: typ.Any) -> typ.Any:  # pyright: ignore[reportAny]
		"""Set the default BLPlatforms to the largest common subset of platforms supported by given Blender versions."""
		if isinstance(data, dict) and 'bl_platforms' not in data:
			if (
				'blender_version_min' in data
				and isinstance(data['blender_version_min'], str)
				and (
					'blender_version_max' not in data
					or (
						'blender_version_max' in data
						and isinstance(data['blender_version_max'], str)
					)
				)
			):
				released_bl_versions = (
					extyp.BLReleaseOfficial.from_official_version_range(
						data['blender_version_min'],
						data.get('blender_version_max'),  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
					)
				)
				valid_bl_platforms = functools.reduce(
					lambda a, b: a | b,
					[
						released_bl_version.bl_version.valid_bl_platforms
						for released_bl_version in released_bl_versions
					],
				)
				data['bl_platforms'] = valid_bl_platforms
			else:
				msg = 'blender_version_min must be given to deduce bl_platforms'
				raise ValueError(msg)

		return data  # pyright: ignore[reportUnknownVariableType]

	## TODO: Guarantee that manifest export will work for all bl_versions, bl_platforms, and bl_manifest_versions.

	@pyd.model_validator(mode='after')
	def validate_tags_against_bl_versions(self) -> typ.Self:
		"""Validate that all extension tags can actually be parsed by all supported Blender versions."""
		if self.tags is not None:
			valid_tags = functools.reduce(
				lambda a, b: a & b,
				[bl_version.valid_extension_tags for bl_version in self.bl_versions],
			)

			if self.tags.issubset(valid_tags):
				return self
			msgs = [
				'The following extension tags are not valid in all supported Blender versions:',
				*[f'- `{tag}`' for tag in sorted(self.tags - valid_tags)],
			]
			raise ValueError(*msgs)
		return self

	## TODO: Check that all bl_platforms is valid in at least one of `self.bl_versions`.
	## - It's a niche thing, but might as well get it right.
