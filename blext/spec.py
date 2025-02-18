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
import rich
import tomli_w

from . import supported, wheels

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

	# Project Path
	path_proj_root: Path

	# Platform Support
	## - For building a platform-specific extension, just copy the model w/this field altered.
	bl_platforms: frozenset[supported.BLPlatform]

	# Versions
	req_python_version: str
	min_glibc_version: tuple[int, int] = (2, 20)
	min_macos_version: tuple[int, int] = (11, 0)
	## TODO: Constrained integers for both

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
		ValidBLTags,
		...,
	] = ()
	license: tuple[str, ...]
	copyright: tuple[str, ...]
	website: pyd.HttpUrl | None = None

	@property
	def is_universal_blext(self) -> bool:
		"""Whether this extension supports all Blender platforms.

		This will generally be the case for pure-Python extensions.
		"""
		return frozenset(supported.BLPlatform) == self.bl_platforms

	####################
	# - Extension Manifest: Computed Properties
	####################
	@pyd.computed_field
	@property
	def platforms(self) -> list[supported.BLPlatform]:
		"""Operating systems supported by the extension."""
		return sorted(self.bl_platforms)

	@pyd.computed_field(alias='wheels')
	@property
	def wheel_paths(self) -> tuple[Path, ...]:
		"""Path to all shipped wheels, relative to the root of the unpacked extension `.zip` file."""
		return tuple(
			[
				Path(f'./wheels/{wheel.filename}')
				for wheel in sorted(self.wheels, key=lambda el: el.project)
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
		"""Path to the project `.dev/` folder, which should not be checked in."""
		path_dev = self.path_proj_root / '.dev'
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

		msg = f"Cannot deduce filename of non-universal Blender extension when more than one 'BLPlatform' is supported: {', '.join(self.bl_platforms)}"
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
						'wheel_paths',
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
	def constrain_to_bl_platform(
		self, bl_platform: frozenset[supported.BLPlatform] | supported.BLPlatform | None
	) -> typ.Self:
		"""Create a new `BLExtSpec`, which supports only one operating system.

		All PyPa platform tags associated with that operating system will be transferred.
		In all other respects, the created `BLExtSpec` will be identical.

		Parameters:
			bl_platform: The Blender platform to support exclusively.

		"""
		if bl_platform is None:
			bl_platforms = frozenset({supported.BLPlatform})
		elif isinstance(bl_platform, set | frozenset):
			bl_platforms = bl_platform
		else:
			bl_platforms = frozenset({bl_platform})

		return self.model_copy(
			update={
				'bl_platforms': bl_platforms,
			},
			deep=True,
		)

	####################
	# - Wheel Management
	####################
	@functools.cached_property
	def wheels(self) -> frozenset[wheels.BLExtWheel]:
		"""All wheels needed by this Blender extension."""
		all_wheels = {
			wheel: wheel.get_compatible_bl_platforms(
				valid_python_tags=frozenset(
					{
						'py3',
						'cp36',
						'cp37',
						'cp38',
						'cp39',
						'cp310',
						'cp311',
					}
				),
				valid_abi_tags=frozenset(
					{
						'none',
						'abi3',
						#'cp36',
						#'cp37',
						#'cp38',
						#'cp39',
						#'cp310',
						'cp311',
					}
				),
				min_glibc_version=self.min_glibc_version,
				min_macos_version=self.min_macos_version,
			)
			for wheel in wheels.parse_all_possible_wheels(self.path_proj_root)
		}

		####################
		# - Build the Wheel Graph
		####################
		wheels_graph: dict[str, dict[supported.BLPlatform, list[wheels.BLExtWheel]]] = {
			package_name: {bl_platform: [] for bl_platform in self.bl_platforms}
			for package_name in wheels.parse_all_package_names(self.path_proj_root)
		}
		for wheel, wheel_bl_platforms in all_wheels.items():
			for wheel_bl_platform in wheel_bl_platforms:
				if wheel_bl_platform in self.bl_platforms:
					wheels_graph[wheel.project][wheel_bl_platform].append(wheel)

		####################
		# - Deduplicate: Select ONE Wheel Per-Dependency Per-Platform
		####################
		for package_name, wheels_by_project in wheels_graph.items():
			for bl_platform, wheels_by_platform in wheels_by_project.items():
				if len(wheels_by_platform) > 1:
					# Windows: Pick win_amd64 over win32.
					if bl_platform is supported.BLPlatform.windows_x64:
						wheels_graph[package_name][bl_platform] = sorted(
							wheels_by_platform,
							key=lambda el: sum(
								{'any': 2, 'win32': 1, 'win_amd64': 0}[platform_tag]
								for platform_tag in el.platform_tags
							),
						)[:1]
					## TODO: Perhaps sort such that highest version gets picked first?

					# Linux: Sort by GLIBC version and pick the highest valid version.
					elif bl_platform in [
						supported.BLPlatform.linux_x64,
						supported.BLPlatform.linux_arm64,
					]:

						def glibc_versions(
							wheel: wheels.BLExtWheel,
							bl_platform: supported.BLPlatform,
						) -> list[tuple[int, int]]:
							glibc_versions = [
								wheel.glibc_version(platform_tag)
								for platform_tag in wheel.platform_tags
								if any(
									platform_tag.endswith(pypi_arch)
									for pypi_arch in bl_platform.pypi_arches
								)
							]

							return [
								glibc_version
								for glibc_version in glibc_versions
								if glibc_version is not None
							]

						wheels_graph[package_name][bl_platform] = list(
							sorted(
								wheels_by_platform,
								key=lambda el: -int(el.size) if el.size else 0,
							)[:1]
							## TODO: Perhaps sort such that highest version gets picked first?
						)

					# MacOS: Sort by OS version and pick the highest valid version.
					elif bl_platform in [
						supported.BLPlatform.macos_x64,
						supported.BLPlatform.macos_arm64,
					]:

						def macos_versions(
							wheel: wheels.BLExtWheel,
							bl_platform: supported.BLPlatform,
						) -> list[tuple[int, int]]:
							macos_versions = [
								wheel.macos_version(platform_tag)
								for platform_tag in wheel.platform_tags
								if any(
									platform_tag.endswith(pypi_arch)
									for pypi_arch in bl_platform.pypi_arches
								)
							]

							return [
								macos_version
								for macos_version in macos_versions
								if macos_version is not None
							]

						wheels_graph[package_name][bl_platform] = list(
							sorted(
								wheels_by_platform,
								key=lambda el: -int(el.size) if el.size else 0,
								## TODO: Perhaps sort such that highest version gets picked first?
							)[:1]
						)

		####################
		# - Validate: Ensure All Deps + Platforms Have ==1 Wheel
		####################
		num_missing_deps = 0
		missing_dep_msgs: list[str] = []
		for package_name, wheels_by_project in wheels_graph.items():
			for bl_platform, wheels_by_platform in wheels_by_project.items():
				if len(wheels_by_platform) == 0:
					num_missing_deps += 1
					all_candidate_wheels = sorted(
						[
							wheel
							for wheel in wheels.parse_all_possible_wheels(
								self.path_proj_root
							)
							if wheel.project == package_name
						],
						key=lambda el: el.filename,
					)

					min_glibc_str = '.'.join(str(i) for i in self.min_glibc_version)
					min_macos_str = '.'.join(str(i) for i in self.min_macos_version)
					msgs = [
						f'**{package_name}** not found for `{bl_platform}`.',
						*(
							[
								'|  **Possible Causes**:',
								'|  - `...manylinux_M_m_<arch>.whl` wheels require `glibc >= M.m`.',
								f'|  - This extension is set to require `glibc >= {min_glibc_str}`.',
								f'|  - Therefore, only wheels with `macos <= {min_glibc_str}` can be included.',
								'|  ',
								'|  **Suggestions**:',
								'|  - Try raising `min_glibc_version = [M, m]` in `[tool.blext]`.',
								'|  - _This may make the extension incompatible with older machines_.',
							]
							if bl_platform.startswith('linux')
							else []
						),
						*(
							[
								'|  **Possible Causes**:',
								'|  - `...macosx_M_m_<arch>.whl` wheels require `macos >= M.m`.',
								f'|  - This extension is set to require `macos >= {min_macos_str}`.',
								f'|  - Therefore, only wheels with `macos <= {min_macos_str}` can be included.',
								'|  ',
								'|  **Suggestions**:',
								'|  - Try raising `min_macos_version = [M, m]` in `[tool.blext]`.',
								'|  - _This may make the extension incompatible with older machines_.',
							]
							if bl_platform.startswith('macos')
							else []
						),
						*(
							[
								'|  ',
								'|  **Rejected Wheels**:',
							]
							+ [
								f'|  - {candidate_wheel.filename}'
								for candidate_wheel in all_candidate_wheels
							]
						),
						'|',
					]
					for msg in msgs:
						missing_dep_msgs.append(msg)

				if len(wheels_by_platform) > 1:
					msg = f">1 valid wheel is set to be downloaded for '{package_name}:{bl_platform}', which indicates a bug in 'blext'. Please report this bug!"
					raise RuntimeError(msg)

		if missing_dep_msgs:
			missing_dep_msgs.append(f'**Missing Dependencies**: {num_missing_deps}')
			raise ValueError(*missing_dep_msgs)

		####################
		# - Flatten Wheel Graph and Return
		####################
		return frozenset(
			{
				wheel
				for package_name, wheels_by_package in wheels_graph.items()
				for bl_platform, wheels_by_platform in wheels_by_package.items()
				for wheel in wheels_by_platform
			}
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
		####################
		# - Parsing: Stage 1
		####################
		###: Determine whether all fields are accessible.

		# Parse [project]
		if proj_spec.get('project') is not None:
			project = proj_spec['project']
		else:
			msgs = [
				f'In `{path_proj_root / "pyproject.toml"}`:',
				'- `[project]` table is not defined.',
			]
			raise ValueError(*msgs)

		# Parse [tool.blext]
		if (
			proj_spec.get('tool') is not None
			and proj_spec['tool'].get('blext') is not None
		):
			blext_spec = proj_spec['tool']['blext']
		else:
			msgs = [
				f'In `{path_proj_root / "pyproject.toml"}`:',
				'- `[tool.blext]` table is not defined.',
			]
			raise ValueError(*msgs)

		# Parse [tool.blext.profiles]
		if proj_spec['tool']['blext'].get('profiles') is not None:
			release_profiles = blext_spec['profiles']
			if release_profile in release_profiles:
				release_profile_spec = release_profiles[release_profile]
			else:
				msgs = [
					f'In `{path_proj_root / "pyproject.toml"}`:',
					f'- `[tool.blext.profiles.{release_profile}]` table is not defined, yet `{release_profile}` is requested.',
				]
				raise ValueError(*msgs)

		else:
			msgs = [
				f'In `{path_proj_root / "pyproject.toml"}`:',
				'- `[tool.blext.profiles]` table is not defined.',
			]
			raise ValueError(*msgs)

		####################
		# - Parsing: Stage 2
		####################
		###: Parse values that require transformations.

		field_parse_errs = []

		# Parse project.requires-python
		if project.get('requires-python') is not None:
			project_requires_python = project['requires-python'].replace('~= ', '')
		else:
			project_requires_python = ''
			field_parse_errs.append('- `project.requires-python` is not defined.')

		# Parse project.maintainers[0]
		if project.get('maintainers') is not None and len(project['maintainers']) > 0:
			first_maintainer = project.get('maintainers')[0]
		else:
			first_maintainer = {'name': None, 'email': None}

		# Parse project.license
		if (
			project.get('license') is not None
			and project['license'].get('text') is not None
		):
			_license = project['license']['text']
		else:
			_license = None
			field_parse_errs.append('- `project.license.text` is not defined.')
			field_parse_errs.append(
				'- Please note that all Blender addons MUST have a GPL-compatible license: <https://docs.blender.org/manual/en/latest/advanced/extensions/licenses.html>'
			)

		## Parse project.urls.homepage
		if (
			project.get('urls') is not None
			and project['urls'].get('Homepage') is not None
		):
			homepage = project['urls']['Homepage']
		else:
			homepage = None

		####################
		# - Parsing: Stage 3
		####################
		###: Parse field availability and provide for descriptive errors

		if blext_spec.get('supported_platforms') is None:
			field_parse_errs += ['- `tool.blext.supported_platforms` is not defined.']
		if project.get('name') is None:
			field_parse_errs += ['- `project.name` is not defined.']
		if blext_spec.get('pretty_name') is None:
			field_parse_errs += ['- `tool.blext.pretty_name` is not defined.']
		if project.get('version') is None:
			field_parse_errs += ['- `project.version` is not defined.']
		if project.get('description') is None:
			field_parse_errs += ['- `project.description` is not defined.']
		if blext_spec.get('blender_version_min') is None:
			field_parse_errs += ['- `tool.blext.blender_version_min` is not defined.']
		if blext_spec.get('blender_version_max') is None:
			field_parse_errs += ['- `tool.blext.blender_version_max` is not defined.']
		if blext_spec.get('bl_tags') is None:
			field_parse_errs += ['- `tool.blext.bl_tags` is not defined.']
			field_parse_errs += [
				'- Valid `bl_tags` values are: '
				+ ', '.join([f'"{el}"' for el in typ.get_args(ValidBLTags)])
			]
		if blext_spec.get('copyright') is None:
			field_parse_errs += ['- `tool.blext.copyright` is not defined.']
			field_parse_errs += [
				'- Example: `copyright = ["<current_year> <proj_name> Contributors`'
			]

		if field_parse_errs:
			msgs = [
				f'In `{path_proj_root / "pyproject.toml"}`:',
				*field_parse_errs,
			]
			raise ValueError(*msgs)

		####################
		# - Parsing: Stage 4
		####################
		###: With guaranteed existance, do qualitative parsing w/pydantic.
		return cls(
			path_proj_root=path_proj_root,
			req_python_version=project_requires_python,
			min_glibc_version=blext_spec.get('min_glibc_version', (2, 20)),
			min_macos_version=blext_spec.get('min_macos_version', (11, 0)),
			bl_platforms=blext_spec['supported_platforms'],
			# File Logging
			use_log_file=release_profile_spec.get('use_log_file', False),
			log_file_path=release_profile_spec.get('log_file_path', 'addon.log'),
			log_file_level=release_profile_spec.get('log_file_level', 'debug'),
			# Console Logging
			use_log_console=release_profile_spec.get('use_log_console', True),
			log_console_level=release_profile_spec.get('log_console_level', 'debug'),
			# Basics
			id=project['name'],
			name=blext_spec['pretty_name'],
			version=project['version'],
			tagline=project['description'],
			maintainer=f'{first_maintainer["name"]} <{first_maintainer["email"]}>',
			# Blender Compatibility
			blender_version_min=blext_spec['blender_version_min'],
			blender_version_max=blext_spec['blender_version_max'],
			# Permissions
			permissions=blext_spec.get('permissions', {}),
			# Addon Tags
			tags=blext_spec['bl_tags'],
			license=(f'SPDX:{_license}',),
			copyright=blext_spec['copyright'],
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
			ValueError: If the `pyproject.toml` file cannot be loaded, or it does not contain the required tables and/or fields.
		"""
		# Load File
		if path_proj_spec.is_file():
			with path_proj_spec.open('rb') as f:
				proj_spec = tomllib.load(f)
		else:
			msg = f'Could not load file: `{path_proj_spec}`'
			raise ValueError(msg)

		# Parse Extension Specification
		return cls.from_proj_spec_dict(
			proj_spec,
			path_proj_root=path_proj_spec.parent,
			release_profile=release_profile,
		)
