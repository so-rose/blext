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

"""Defines the `BLExtSpec` model."""

import functools
import json
import tomllib
import typing as typ
from pathlib import Path

import annotated_types as atyp
import pydantic as pyd
import rich
import tomli_w
from frozendict import frozendict

from . import extyp, pydeps
from .utils.inline_script_metadata import parse_inline_script_metadata
from .utils.pydantic_frozen_dict import FrozenDict

CONSOLE = rich.console.Console()

ValidBLTags: typ.TypeAlias = typ.Literal[
	'3D View',
	'Add Curve',
	'Add Mesh',
	'Animation',
	'Bake',
	'Camera',
	'Compositing',
	'Development',
	'Game Engine',
	'Geometry Nodes',
	'Grease Pencil',
	'Import-Export',
	'Lighting',
	'Material',
	'Modeling',
	'Mesh',
	'Node',
	'Object',
	'Paint',
	'Pipeline',
	'Physics',
	'Render',
	'Rigging',
	'Scene',
	'Sculpt',
	'Sequencer',
	'System',
	'Text Editor',
	'Tracking',
	'User Interface',
	'UV',
]


####################
# - Types
####################
class BLExtSpec(pyd.BaseModel, frozen=True):
	"""Completely encapsulates information about the packaging of a Blender extension.

	This model allows `pyproject.toml` to be the single source of truth for a Blender extension project.
	Thus, this model is designed to be parsed entirely from a `pyproject.toml` file, and in turn is capable of generating the Blender extension manifest file and more.

	To the extent possible, appropriate standard `pyproject.toml` fields are scraped for information relevant to a Blender extension.
	This includes name, version, license, desired dependencies, homepage, and more.
	Naturally, many fields are _quite_ specific to Blender extensions, such as Blender version constraints, permissions, and extension tags.
	For such options, the `[tool.blext]` section is introduced.

	Attributes:
		init_settings_filename: Must be `init_settings.toml`.
		use_log_file: Whether the extension should default to the use of file logging.
		log_file_name: The path to the file log (if enabled).
		log_file_level: The file log level to use (if enabled).
		use_log_console: Whether the extension should default to the use of console logging.
		log_console_level: The console log level to use (if enabled).
		schema_version: Must be 1.0.0.
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

	# Platform Support
	## - For building a platform-specific extension, just copy the model w/this field altered.
	bl_platforms: typ.Annotated[
		frozenset[extyp.BLPlatform],
		atyp.MinLen(1),
	]
	wheels_graph: pydeps.BLExtWheelsGraph

	# Versions
	req_python_version: str
	min_glibc_version: tuple[int, int] = (2, 20)
	min_macos_version: tuple[int, int] = (11, 0)
	## TODO: Constrained integers for both
	## TODO: Perhaps keep a BLExtWheelsGraph on here instead?

	####################
	# - Init Settings
	####################
	init_settings_filename: typ.Literal['init_settings.toml'] = 'init_settings.toml'
	init_settings_schema_version: typ.Literal['0.1.0'] = pyd.Field(
		default='0.1.0', serialization_alias='schema_version'
	)
	## TODO: Conform to extension version?

	# File Logging
	use_log_file: bool
	log_file_name: str
	log_file_level: extyp.StrLogLevel

	# Console Logging
	use_log_console: bool
	log_console_level: extyp.StrLogLevel

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
	tagline: pyd.constr(
		max_length=64,
		pattern=r'^[a-zA-Z0-9\ \=\+\!\@\#\$\%\^\&\*\(\)\-\_\\\|\;\:\'\"\/\?\{\[\}\]]{1,63}[a-zA-Z0-9]$',
	)
	maintainer: str

	## TODO: Validator on tagline that prohibits ending with punctuation
	## - In fact, alpha-numeric suffix is required.

	# Blender Compatibility
	type: typ.Literal['add-on'] = 'add-on'
	blender_version_min: pyd.constr(pattern=r'^[4-9]+\.[2-9]+\.[0-9]+$')
	blender_version_max: pyd.constr(pattern=r'^[4-9]+\.[2-9]+\.[0-9]+$')

	# OS/Arch Compatibility

	# Permissions
	## - "files" (for access of any filesystem operations)
	## - "network" (for internet access)
	## - "clipboard" (to read and/or write the system clipboard)
	## - "camera" (to capture photos and videos)
	## - "microphone" (to capture audio)
	permissions: FrozenDict[
		typ.Literal['files', 'network', 'clipboard', 'camera', 'microphone'], str
	] = frozendict()

	# Addon Tags
	tags: tuple[
		ValidBLTags,
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

		This will generally be the case for pure-Python extensions.
		"""
		return frozenset(extyp.BLPlatform) == self.bl_platforms

	####################
	# - Packing Information
	####################
	@pyd.computed_field(alias='platforms')
	@property
	def packed_platforms(self) -> list[extyp.BLPlatform]:
		"""Sorted variant of `self.bl_platforms`."""
		return sorted(self.bl_platforms)

	@pyd.computed_field(alias='wheels')
	@property
	def packed_wheel_paths(self) -> tuple[str, ...]:
		"""Path to all shipped wheels within the packed `.zip` file."""
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
		"""Filename of the `.zip` file to build as a Blender extension."""
		# Deduce Zip Filename
		if self.is_universal:
			return f'{self.id}__{self.version}.zip'

		if len(self.bl_platforms) == 1:
			only_supported_os = next(iter(self.bl_platforms))
			return f'{self.id}__{self.version}_{only_supported_os}.zip'

		msg = f"Cannot deduce filename of non-universal Blender extension when more than one 'BLPlatform' is supported: {', '.join(self.bl_platforms)}"
		raise ValueError(msg)

	####################
	# - Exporters
	####################
	def export_init_settings(self, *, fmt: typ.Literal['json', 'toml']) -> str:
		"""Initialization settings, as a TOML string."""
		# Parse Model to JSON
		## - JSON is used like a Rosetta Stone, since it is best supported by pydantic.
		json_str = self.model_dump_json(
			include={
				'init_settings_schema_version',
				'use_log_file',
				'log_file_name',
				'log_file_level',
				'use_log_console',
				'log_console_level',
			},
			by_alias=True,
		)

		# Return String as Format
		if fmt == 'json':
			return json_str
		if fmt == 'toml':
			json_dict: dict[str, typ.Any] = json.loads(json_str)
			return tomli_w.dumps(json_dict)

		msg = (
			f'Cannot export initialization settings to the given unknown format: {fmt}'
		)
		raise ValueError(msg)

	def export_blender_manifest(self, *, fmt: typ.Literal['json', 'toml']) -> str:
		"""Blender extension manifest, as a TOML string."""
		# Parse Model to JSON
		## - JSON is used like a Rosetta Stone, since it is best supported by pydantic.
		json_str = self.model_dump_json(
			include={
				'manifest_schema_version',
				'id',
				'name',
				'version',
				'tagline',
				'maintainer',
				'type',
				'blender_version_min',
				'blender_version_max',
				'packed_platforms',
				'packed_wheel_paths',
				'permissions',
				'tags',
				'license',
				'copyright',
			}
			| ({'website'} if self.website is not None else set()),
			by_alias=True,
		)

		# Return String as Format
		if fmt == 'json':
			return json_str
		if fmt == 'toml':
			json_dict: dict[str, typ.Any] = json.loads(json_str)
			return tomli_w.dumps(json_dict)

		msg = (
			f'Cannot export initialization settings to the given unknown format: {fmt}'
		)
		raise ValueError(msg)

	####################
	# - Methods
	####################
	def constrain_to_bl_platform(
		self, bl_platform: frozenset[extyp.BLPlatform] | extyp.BLPlatform | None
	) -> typ.Self:
		"""Create a new `BLExtSpec`, which supports only one operating system.

		All PyPa platform tags associated with that operating system will be transferred.
		In all other respects, the created `BLExtSpec` will be identical.

		Parameters:
			bl_platform: The Blender platform to support exclusively.

		"""
		if bl_platform is None:
			bl_platforms = frozenset({extyp.BLPlatform})
		elif isinstance(bl_platform, set | frozenset):
			bl_platforms = bl_platform
		else:
			bl_platforms = frozenset({bl_platform})

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
	def from_proj_spec_dict(
		cls,
		proj_spec_dict: dict[str, typ.Any],
		*,
		path_proj_spec: Path,
		release_profile_id: extyp.StandardReleaseProfile | str,
	) -> typ.Self:
		"""Parse a `BLExtSpec` from a `pyproject.toml` dictionary.

		Args:
			proj_spec: The dictionary representation of a `pyproject.toml` file.

		Raises:
			ValueError: If the `pyproject.toml` file does not contain the required tables and/or fields.

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
				'- `[project]` table is not defined.',
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
				'- `[tool.blext]` table is not defined.',
			]
			raise ValueError(*msgs)

		# [tool.blext.profiles]
		release_profile: None | extyp.ReleaseProfile = None
		if blext_spec_dict.get('profiles') is not None:
			project_release_profiles: dict[str, typ.Any] = blext_spec_dict['profiles']
			if release_profile_id in project_release_profiles:
				release_profile = extyp.ReleaseProfile(
					**project_release_profiles[release_profile_id]
				)

		if release_profile is None and release_profile_id in typ.get_args(
			extyp.StandardReleaseProfile
		):
			release_profile = extyp.ReleaseProfile.default_spec(release_profile_id)  # pyright: ignore[reportArgumentType]

		else:
			msgs = [
				f'- The selected "release profile" `{release_profile_id}` is not a standard release profile...',
				'- ... but `[tool.blext.profiles]` does not define.',
				f'- Please either define `{release_profile_id}` in `[tool.blext.profiles]`, or select a standard release profile from `{set(typ.get_args(extyp.StandardReleaseProfile))}`',
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
				requires_python_field = project['requires-python']
			elif is_script_metadata:
				requires_python_field = proj_spec_dict['requires-python']
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
				+ ', '.join([f'"{el}"' for el in typ.get_args(ValidBLTags)])
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
		###: With guaranteed existance, do qualitative parsing w/pydantic.

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

		return cls(
			req_python_version=project_requires_python,
			wheels_graph=pydeps.BLExtWheelsGraph.from_uv_lock(
				pydeps.uv.parse_uv_lock(path_uv_lock),
				supported_bl_platforms=blext_spec_dict['supported_platforms'],
				min_glibc_version=blext_spec_dict.get('min_glibc_version', (2, 20)),
				min_macos_version=blext_spec_dict.get('min_macos_version', (11, 0)),
			),
			bl_platforms=blext_spec_dict['supported_platforms'],
			####################
			# - Init Settings
			####################
			# File Logging
			use_log_file=release_profile.use_log_file,
			log_file_name=release_profile.log_file_name,
			log_file_level=release_profile.log_file_level,
			# Console Logging
			use_log_console=release_profile.use_log_console,
			log_console_level=release_profile.log_console_level,
			####################
			# - Blender Manifest
			####################
			# Basics
			id=project['name'],
			name=blext_spec_dict['pretty_name'],
			version=project['version'],
			tagline=project['description'],
			maintainer=f'{first_maintainer["name"]} <{first_maintainer["email"]}>',
			# Blender Compatibility
			blender_version_min=blext_spec_dict['blender_version_min'],
			blender_version_max=blext_spec_dict['blender_version_max'],
			# Permissions
			permissions=blext_spec_dict.get('permissions', {}),
			# Addon Tags
			tags=blext_spec_dict['bl_tags'],
			license=(f'SPDX:{extension_license}',),
			copyright=blext_spec_dict['copyright'],
			website=homepage,  # pyright: ignore[reportArgumentType]
		)

	@classmethod
	def from_proj_spec_path(
		cls,
		path_proj_spec: Path,
		*,
		release_profile_id: extyp.StandardReleaseProfile | str,
	) -> typ.Self:
		"""Parse an extension specification from a compatible file.

		Args:
			path_proj_spec: Path to either a `pyproject.toml`, or `*.py` script with inline metadata.
			release_profile_id: The identifier for the release profile, which decides the initialization settings of the extension.

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
		)
