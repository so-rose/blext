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
from frozendict import frozendict

from . import extyp, pydeps
from .utils.inline_script_metadata import parse_inline_script_metadata
from .utils.pydantic_frozen_dict import FrozenDict

####################
# - Build Process
####################
## TODO: Implement glob ignores.
## - Glob from the project root path (for scripts, this is the parent dir of the script path)
## - A file may not be included in the zip if it matches a path in ignore_globs.
## - Found items should always be injected at the same relative path in the zip as outside the zip.
## - Ideally, these could be (configurably) mined from a `.gitignores` file.
## - Also ideally, certain specific folders ex. .venv could be ignored by default.
## - **There's also a blender_manifest.toml entry for this**. Maybe that's where to start.
# IGNORE_GLOBS: tuple[str, ...] = ('**/__pycache__/**/*',)

## TODO: Implement glob prepacking.
## - Glob from the project root path (for scripts, this is the parent dir of the script path)
## - Set items are the glob patterns to use as `Path(...).glob(pattern)`
## - Found items should always be injected at the same relative path in the zip as outside the zip.
## - Ideally, these could be (configurably) mined from a `.gitattributes` file.
# PREPACK_GLOBS: tuple[str, ...] = ()


####################
# - Types
####################
class BLExtSpec(pyd.BaseModel, frozen=True):
	"""Specifies a Blender extension.

	This model allows `pyproject.toml` to be the single source of truth for a Blender extension project.
	Thus, this model is designed to be parsed entirely from a `pyproject.toml` file, and in turn is capable of generating the Blender extension manifest file and more.

	To the extent possible, appropriate standard `pyproject.toml` fields are scraped for information relevant to a Blender extension.
	This includes name, version, license, desired dependencies, homepage, and more.
	Naturally, many fields are _quite_ specific to Blender extensions, such as Blender version constraints, permissions, and extension tags.
	For such options, the `[tool.blext]` section is introduced.

	Attributes:
		bl_platforms: Blender platforms supported by this extension.
		wheels_graph: All wheels that might be usable by this extension.
		req_python_version: Python versions supported by this extension.
			**Must** correspond to `blender_version_min` and `blender_version_max`.
		release_profile: Optional initialization settings and spec overrides.
			**Overrides must be applied during construction**.
		manifest_filename: Filename of `blender_manifest.toml`.
			_This is hard-coded, and is unlikely to change._
		manifest_schema_version: Must be 1.0.0.
			_This is hard-coded, but may change._
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
	# - Platform Support
	####################
	bl_platforms: typ.Annotated[
		frozenset[extyp.BLPlatform],
		atyp.MinLen(1),
	]

	####################
	# - Python Dependencies
	####################
	wheels_graph: pydeps.BLExtWheelsGraph
	req_python_version: str
	## TODO: Generate this from the required Blender versions.
	## - Validate this against the pyproject.toml 'req_python_version' field while parsing.

	####################
	# - Init Settings
	####################
	release_profile: extyp.ReleaseProfile | None = None

	####################
	# - Extension Manifest
	####################
	manifest_filename: typ.Literal['blender_manifest.toml'] = 'blender_manifest.toml'
	manifest_schema_version: typ.Literal['1.0.0'] = pyd.Field(
		default='1.0.0', serialization_alias='schema_version'
	)

	# Basics
	id: str
	name: str
	version: str
	tagline: typ.Annotated[
		str,
		pyd.StringConstraints(
			max_length=64,
			# pattern=r'^[a-zA-Z0-9\ \=\+\!\@\#\$\%\^\&\*\(\)\-\_\\\|\;\:\'\"\/\?\{\[\}\]]{1,63}[a-zA-Z0-9]$',
		),
	]
	maintainer: str

	## TODO: Validator on tagline that prohibits ending with punctuation
	## - In fact, alpha-numeric suffix is required.

	# Blender Compatibility
	extension_type: typ.Literal['add-on'] = pyd.Field(
		default='add-on', serialization_alias='type'
	)
	blender_version_min: typ.Annotated[
		str,
		pyd.StringConstraints(
			max_length=64,
			pattern=r'^[4-9]+\.[2-9]+\.[0-9]+$',
		),
	]
	blender_version_max: typ.Annotated[
		str,
		pyd.StringConstraints(
			max_length=64,
			pattern=r'^[4-9]+\.[2-9]+\.[0-9]+$',
		),
	]

	# Permissions
	permissions: FrozenDict[extyp.ValidBLExtPerms, str] = frozendict()

	# Tagging
	tags: tuple[
		extyp.ValidBLTags,
		...,
	] = ()
	license: tuple[str, ...]
	copyright: tuple[str, ...]
	website: pyd.HttpUrl | None = None

	####################
	# - Identity Attributes
	####################
	@property
	def is_universal(self) -> bool:
		"""Whether this extension supports all Blender platforms.

		Notes:
			Pure-Python extensions that only use pure-Python dependencies are considered "universal".
		"""
		return frozenset(extyp.BLPlatform) == self.bl_platforms

	####################
	# - Packing Information
	####################
	@pyd.computed_field(alias='platforms')
	@property
	def packed_platforms(self) -> list[extyp.BLPlatform]:
		"""All supported Blender platforms, sorted for consistency."""
		return sorted(self.bl_platforms)

	@pyd.computed_field(alias='wheels')
	@property
	def vendored_wheel_paths(self) -> tuple[str, ...]:
		"""Path to vendored wheels, from the zipfile root."""
		return tuple(
			[
				f'./wheels/{wheel.filename}'
				for wheel in sorted(
					self.wheels_graph.wheels, key=lambda wheel: wheel.project
				)
			]
		)

	@functools.cached_property
	def packed_zip_filename(self) -> str:
		"""Default filename of the extension zipfile."""
		if self.is_universal:
			return f'{self.id}__{self.version}.zip'
		return f'{self.id}__{self.version}_{"_".join(sorted(self.bl_platforms))}.zip'

	####################
	# - Exporters
	####################
	def export_init_settings(self, *, fmt: typ.Literal['json', 'toml']) -> str:
		"""Alias for `self.release_profile.export_init_settings`.

		Parameters:
			fmt: String format to export initialization settings to.

		Returns:
			String representing the Blender extension manifest.

		Raises:
			ValueError: When `self.release_profile is None`, or `fmt` is unknown.
		"""
		if self.release_profile is not None:
			return self.release_profile.export_init_settings(fmt=fmt)

		msg = 'No release profile was specified.'
		raise ValueError(msg)

	def export_blender_manifest(self, *, fmt: typ.Literal['json', 'toml']) -> str:
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
		# Parse Model to JSON
		## - JSON is used like a Rosetta Stone, since it is best supported by pydantic.
		_includes: set[str] = (
			{
				'manifest_schema_version',
				'id',
				'name',
				'version',
				'tagline',
				'maintainer',
				'extension_type',
				'blender_version_min',
				'blender_version_max',
				'packed_platforms',
				'vendored_wheel_paths',
				'tags',
				'license',
				'copyright',
			}
			| ({'website'} if self.website is not None else set())
			| ({'permissions'} if self.website is not None else set())
		)
		json_str = self.model_dump_json(
			include=_includes,
			by_alias=True,
		)

		# Return String as Format
		if fmt == 'json':
			return json_str
		if fmt == 'toml':
			json_dict: dict[str, typ.Any] = json.loads(json_str)
			return tomli_w.dumps(json_dict)

		msg = (  # pyright: ignore[reportUnreachable]
			f'Cannot export initialization settings to the given unknown format: {fmt}'
		)
		raise ValueError(msg)

	####################
	# - Methods
	####################
	def set_bl_platforms(
		self,
		bl_platform: frozenset[extyp.BLPlatform]
		| set[extyp.BLPlatform]
		| extyp.BLPlatform,
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
				- `self.bl_platforms`: Modified according to parameters.
				- `self.wheels_graph.supported_bl_platforms`: Modified according to parameters.

		"""
		# Parse FrozenSet of Platforms
		match bl_platform:
			case frozenset():
				bl_platforms = bl_platform
			case set():
				bl_platforms = frozenset(bl_platform)
			case extyp.BLPlatform():
				bl_platforms = frozenset({bl_platform})

		# Perform Deep-Copy w/Altered BLPlatforms
		return self.model_copy(
			update={
				'bl_platforms': bl_platforms,
				'wheels_graph': self.wheels_graph.model_copy(
					update={'supported_bl_platforms': bl_platforms}
				),
			},
			deep=True,
		)

	####################
	# - Creation
	####################
	@classmethod
	def from_proj_spec_dict(  # noqa: C901, PLR0912, PLR0915
		cls,
		proj_spec_dict: dict[str, typ.Any],
		*,
		path_proj_spec: Path,
		release_profile_id: extyp.StandardReleaseProfile | str | None,
		override_path_uv_exe: Path | None = None,
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
			override_path_uv_exe: Optional overriden path to a `uv` executable.
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
				'**Invalid Extension Specification**:',
				f'|    `[project]` table was not found in: `{path_proj_spec}`',
				'|',
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
				'**Invalid Extension Specification**:',
				f'|    `[tool.blext]` table was not found in: `{path_proj_spec}`',
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

		if release_profile is None and release_profile_id in typ.get_args(
			extyp.StandardReleaseProfile
		):
			release_profile = extyp.ReleaseProfile.default_spec(release_profile_id)  # pyright: ignore[reportArgumentType]

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
				f'**Standard Release Profiles**: `{", ".join(typ.get_args(extyp.StandardReleaseProfile))}`',
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
			## TODO: Use validator to check that Blender version corresponds to the Python version.

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
		## TODO: Use validator to check that the email has a valid format.

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
		## TODO: Check that the license is one of the licenses compatible with Blender. Consider providing a CLI option to ignore this (--i-have-consulted-legal-council-and-swear-its-okay)

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
		## TODO: Use a validator to check that the URL is valid.

		####################
		# - Parsing: Stage 3
		####################
		###: Parse field availability and provide for descriptive errors
		_valid_bl_tags: tuple[str] = typ.get_args(extyp.ValidBLTags)

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
			field_parse_errs += [
				'- Valid `bl_tags` values are: '
				+ ', '.join([f'"{el}"' for el in _valid_bl_tags])
			]
		if blext_spec_dict.get('copyright') is None:
			field_parse_errs += ['- `tool.blext.copyright` is not defined.']
			field_parse_errs += [
				'- Example: `copyright = ["<current_year> <proj_name> Contributors`'
			]

		## TODO:
		## - Validator name and prety name match Blender's validation.
		## - Validator version string, match Blender's validation routine.
		## - Validator for Blender version strings.
		## - Validator for description, esp. the period at the end.
		## - Validator for copyright format.

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
			'req_python_version': project_requires_python,
			'wheels_graph': pydeps.BLExtWheelsGraph.from_uv_lock(
				pydeps.uv.parse_uv_lock(
					path_uv_lock, override_path_uv_exe=override_path_uv_exe
				),
				requirements_txt=pydeps.uv.parse_requirements_txt(
					path_uv_lock, override_path_uv_exe=override_path_uv_exe
				),
				supported_bl_platforms=blext_spec_dict['supported_platforms'],  # pyright: ignore[reportAny]
				min_glibc_version=blext_spec_dict.get('min_glibc_version', (2, 20)),
				min_macos_version=blext_spec_dict.get('min_macos_version', (11, 0)),
			),
			'bl_platforms': blext_spec_dict['supported_platforms'],
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
		release_profile_id: extyp.StandardReleaseProfile | str | None,
		override_path_uv_exe: Path | None = None,
	) -> typ.Self:
		"""Parse an extension specification from a compatible file.

		Args:
			path_proj_spec: Path to either a `pyproject.toml`, or `*.py` script with inline metadata.
			release_profile_id: Identifier for the release profile.
			override_path_uv_exe: Optional overriden path to a `uv` executable.
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
			path_proj_spec=path_proj_spec,
			release_profile_id=release_profile_id,
			override_path_uv_exe=override_path_uv_exe,
		)
