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

import pydantic as pyd
import tomli_w

from . import supported


####################
# - Path Mangling
####################
def parse_spec_path(path_proj_root: Path, p_str: str) -> Path:
	"""Convert a project-root-relative '/'-delimited string path to an absolute, cross-platform path.

	This allows for cross-platform path specification, while retaining normalized use of '/' in configuration.

	Args:
		path_proj_root: The path to the project root directory.
		p_str: The '/'-delimited string denoting a path relative to the project root.

	Returns:
		The full absolute path to use when ex. packaging.
	"""
	return path_proj_root / Path(*p_str.split('/'))


####################
# - Types
####################
# class BLExtSpec(pyd.BaseModel, frozen=True):  ## TODO: FrozenDict
class BLExtSpec(pyd.BaseModel):
	"""Completely encapsulates information about the packaging of a Blender extension.

	This model allows `pyproject.toml` to be the single source of truth for a Blender extension project.
	Thus, this model is designed to be parsed entirely from a `pyproject.toml` file, and in turn is capable of generating the Blender extension manifest file and more.

	To the extent possible, appropriate standard `pyproject.toml` fields are scraped for information relevant to a Blender extension.
	This includes name, version, license, desired dependencies, homepage, and more.
	Naturally, many fields are _quite_ specific to Blender extensions, such as Blender version constraints, permissions, and extension tags.
	For such options, the `[tool.blext]` section is introduced.

	Attributes:
		init_settings_filename: Must be `init_settings.toml`.
		use_path_local: Whether to use a local path, instead of a global system path.
			Useful for debugging during development.
		use_log_file: Whether the extension should default to the use of file logging.
		log_file_path: The path to the file log (if enabled).
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

	# Base
	path_proj_root: Path
	req_python_version: str

	# Platform Support
	is_universal_blext: bool = True
	bl_platform_pypa_tags: dict[str, tuple[str, ...]]

	####################
	# - Packed Filenames
	####################
	init_settings_filename: typ.Literal['init_settings.toml'] = 'init_settings.toml'
	manifest_filename: typ.Literal['blender_manifest.toml'] = 'blender_manifest.toml'

	####################
	# - Init Settings
	####################
	init_schema_version: typ.Literal['0.1.0'] = pyd.Field(
		default='0.1.0', serialization_alias='schema_version'
	)
	## TODO: Conform to extension version?

	# Path Locality
	use_path_local: bool

	# File Logging
	use_log_file: bool
	log_file_path: Path
	log_file_level: supported.StrLogLevel

	# Console Logging
	use_log_console: bool
	log_console_level: supported.StrLogLevel

	####################
	# - Extension Manifest
	####################
	manifest_schema_version: typ.Literal['1.0.0'] = pyd.Field(
		default='1.0.0', serialization_alias='schema_version'
	)

	# Basics
	id: str
	name: str
	version: str
	tagline: str
	maintainer: str

	## TODO: Validator on tagline that prohibits ending with punctuation
	## - In fact, alpha-numeric suffix is required.

	# Blender Compatibility
	type: typ.Literal['add-on'] = 'add-on'
	blender_version_min: str
	blender_version_max: str

	# OS/Arch Compatibility

	# Permissions
	## - "files" (for access of any filesystem operations)
	## - "network" (for internet access)
	## - "clipboard" (to read and/or write the system clipboard)
	## - "camera" (to capture photos and videos)
	## - "microphone" (to capture audio)
	permissions: dict[
		typ.Literal['files', 'network', 'clipboard', 'camera', 'microphone'], str
	] = {}

	# Addon Tags
	tags: tuple[
		typ.Literal[
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
		],
		...,
	] = ()
	license: tuple[str, ...]
	copyright: tuple[str, ...]
	website: pyd.HttpUrl | None = None

	####################
	# - Extension Manifest: Computed Properties
	####################
	@pyd.computed_field(alias='platforms')  # type: ignore[prop-decorator]
	@property
	def bl_platforms(self) -> frozenset[supported.BLPlatform]:
		"""Operating systems supported by the extension."""
		return frozenset(self.bl_platform_pypa_tags.keys())  # type: ignore[arg-type]

	@pyd.computed_field  # type: ignore[prop-decorator]
	@property
	def wheels(self) -> tuple[Path, ...]:
		"""Path to all shipped wheels, relative to the root of the unpacked extension `.zip` file."""
		return tuple(
			[
				Path(f'./wheels/{wheel_path.name}')
				for wheel_path in self.path_wheels.iterdir()
			]
		)

	####################
	# - Path Properties
	####################
	@functools.cached_property
	def path_proj_spec(self) -> Path:
		"""Path to the project `pyproject.toml`."""
		return self.path_proj_root / 'pyproject.toml'

	@functools.cached_property
	def path_pkg(self) -> Path:
		"""Path to the Python package of the extension."""
		return self.path_proj_root / self.id

	@functools.cached_property
	def path_dev(self) -> Path:
		"""Path to the project `dev/` folder, which should not be checked in."""
		path_dev = self.path_proj_root / 'dev'
		path_dev.mkdir(exist_ok=True)
		return path_dev

	@functools.cached_property
	def path_wheels(self) -> Path:
		"""Path to the project's downloaded wheel cache."""
		path_wheels = self.path_dev / 'wheels'
		path_wheels.mkdir(exist_ok=True)
		return path_wheels

	@functools.cached_property
	def path_prepack(self) -> Path:
		"""Path to the project's prepack folder, where pre-packed `.zip`s are written to."""
		path_prepack = self.path_dev / 'prepack'
		path_prepack.mkdir(exist_ok=True)
		return path_prepack

	@functools.cached_property
	def path_build(self) -> Path:
		"""Path to the project's build folder, where extension `.zip`s are written to."""
		path_build = self.path_dev / 'build'
		path_build.mkdir(exist_ok=True)
		return path_build

	@functools.cached_property
	def path_local(self) -> Path:
		"""Path to the project's build folder, where extension `.zip`s are written to."""
		path_build = self.path_dev / 'build'
		path_build.mkdir(exist_ok=True)
		return path_build

	@functools.cached_property
	def filename_zip(self) -> str:
		"""Deduce the filename of the `.zip` extension file to build."""
		# Deduce Zip Filename
		if self.is_universal_blext:
			return f'{self.id}__{self.version}.zip'

		if len(self.bl_platforms) == 1:
			only_supported_os = next(iter(self.bl_platforms))
			return f'{self.id}__{self.version}_{only_supported_os}.zip'

		msg = "Cannot deduce filename of non-universal Blender extension when more than one 'BLPlatform' is supported."
		raise ValueError(msg)

	@functools.cached_property
	def path_zip(self) -> Path:
		"""Path to the Blender extension `.zip` to build."""
		return self.path_build / self.filename_zip

	@functools.cached_property
	def path_zip_prepack(self) -> Path:
		"""Path to the Blender extension `.zip` to build."""
		return self.path_prepack / self.filename_zip

	####################
	# - Exporters
	####################
	@functools.cached_property
	def init_settings_str(self) -> str:
		"""The Blender extension manifest TOML as a string."""
		return tomli_w.dumps(
			json.loads(
				self.model_dump_json(
					include={
						'init_schema_version',
						'use_path_local',
						'use_log_file',
						'log_file_path',
						'log_file_level',
						'use_log_console',
						'log_console_level',
					},
					by_alias=True,
				)
			)
		)

	@functools.cached_property
	def manifest_str(self) -> str:
		"""The Blender extension manifest TOML as a string."""
		return tomli_w.dumps(
			json.loads(
				self.model_dump_json(
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
						'bl_platforms',
						'wheels',
						'permissions',
						'tags',
						'license',
						'copyright',
					}
					| ({'website'} if self.website is not None else set()),
					by_alias=True,
				)
			)
		)

	####################
	# - Methods
	####################
	def constrain_to_bl_platform(self, bl_platform: supported.BLPlatform) -> typ.Self:
		"""Create a new `BLExtSpec`, which supports only one operating system.

		All PyPa platform tags associated with that operating system will be transferred.
		In all other respects, the created `BLExtSpec` will be identical.

		Parameters:
			bl_platform: The Blender platform to support exclusively.

		"""
		pypa_platform_tags = self.bl_platform_pypa_tags[bl_platform]
		return self.model_copy(
			update={
				'bl_platform_pypa_tags': {bl_platform: pypa_platform_tags},
				'is_universal_blext': False,
			},
			deep=True,
		)

	####################
	# - Creation
	####################
	@classmethod
	def from_proj_spec_dict(
		cls,
		proj_spec: dict[str, typ.Any],
		*,
		path_proj_root: Path,
		release_profile: supported.ReleaseProfile,
	) -> typ.Self:
		"""Parse a `BLExtSpec` from a `pyproject.toml` dictionary.

		Args:
			proj_spec: The dictionary representation of a `pyproject.toml` file.

		Raises:
			ValueError: If the `pyproject.toml` file does not contain the required tables and/or fields.

		"""
		# Parse Sections
		## Parse [project]
		if proj_spec.get('project') is not None:
			project = proj_spec['project']
		else:
			msg = "'pyproject.toml' MUST define '[project]' table"
			raise ValueError(msg)

		## Parse [tool.blext]
		if (
			proj_spec.get('tool') is not None
			or proj_spec['tool'].get('blext') is not None
		):
			blext_spec = proj_spec['tool']['blext']
		else:
			msg = "'pyproject.toml' MUST define '[tool.blext]' table"
			raise ValueError(msg)

		## Parse [tool.blext.profiles]
		if proj_spec['tool']['blext'].get('profiles') is not None:
			release_profiles = blext_spec['profiles']
			if release_profile in release_profiles:
				release_profile_spec = release_profiles[release_profile]
			else:
				msg = f"To parse the profile '{release_profile}' from 'pyproject.toml', it MUST be defined as a key in '[tool.blext.profiles]'"
				raise ValueError(msg)

		else:
			msg = "'pyproject.toml' MUST define '[tool.blext.profiles]'"
			raise ValueError(msg)

		# Parse Values
		## Parse project.requires-python
		if project.get('requires-python') is not None:
			project_requires_python = project['requires-python'].replace('~= ', '')
		else:
			msg = "'pyproject.toml' MUST define 'project.requires-python'"
			raise ValueError(msg)

		## Parse project.maintainers[0]
		if project.get('maintainers') is not None:
			first_maintainer = project.get('maintainers')[0]
		else:
			first_maintainer = {'name': None, 'email': None}

		## Parse project.license
		if (
			project.get('license') is not None
			and project['license'].get('text') is not None
		):
			_license = project['license']['text']
		else:
			msg = "'pyproject.toml' MUST define 'project.license.text'"
			raise ValueError(msg)

		## Parse project.urls.homepage
		if (
			project.get('urls') is not None
			and project['urls'].get('Homepage') is not None
		):
			homepage = project['urls']['Homepage']
		else:
			homepage = None

		# Conform to BLExt Specification
		return cls(
			path_proj_root=path_proj_root,
			req_python_version=project_requires_python,
			bl_platform_pypa_tags=blext_spec.get('platforms'),
			# Path Locality
			use_path_local=release_profile_spec.get('use_path_local'),
			# File Logging
			use_log_file=release_profile_spec.get('use_log_file', False),
			log_file_path=release_profile_spec.get('log_file_path', 'addon.log'),
			log_file_level=release_profile_spec.get('log_file_level', 'DEBUG'),
			# Console Logging
			use_log_console=release_profile_spec.get('use_log_console', True),
			log_console_level=release_profile_spec.get('log_console_level', 'DEBUG'),
			# Basics
			id=project.get('name'),
			name=blext_spec.get('pretty_name'),
			version=project.get('version'),
			tagline=project.get('description'),
			maintainer=f'{first_maintainer["name"]} <{first_maintainer["email"]}>',
			# Blender Compatibility
			blender_version_min=blext_spec.get('blender_version_min'),
			blender_version_max=blext_spec.get('blender_version_max'),
			# Permissions
			permissions=blext_spec.get('permissions', {}),
			# Addon Tags
			tags=blext_spec.get('bl_tags'),
			license=(f'SPDX:{_license}',),
			copyright=blext_spec.get('copyright'),
			website=homepage,
		)

	@classmethod
	def from_proj_spec(
		cls,
		path_proj_spec: Path,
		*,
		release_profile: supported.ReleaseProfile,
	) -> typ.Self:
		"""Parse a `BLExtSpec` from a `pyproject.toml` file.

		Args:
			path_proj_spec: The path to an appropriately utilized `pyproject.toml` file.
			release_profile: The profile to load initial settings for.

		Raises:
			ValueError: If the `pyproject.toml` file does not contain the required tables and/or fields.
		"""
		# Load File
		if path_proj_spec.is_file():
			with path_proj_spec.open('rb') as f:
				proj_spec = tomllib.load(f)
		else:
			msg = f"Could not load 'pyproject.toml' at '{path_proj_spec}"
			raise ValueError(msg)

		# Parse Extension Specification
		return cls.from_proj_spec_dict(
			proj_spec,
			path_proj_root=path_proj_spec.parent,
			release_profile=release_profile,
		)
