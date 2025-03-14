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

"""Extension types serving as meaningful abstractions for managing Blender extensions.

Attributes:
	ValidBLExtPerms: Hardcoded list of valid extension permissions.
		- `files`: Access to any filesystem operations.
		- `network`: Access to the internet.
		- `clipboard`: Permission to read and/or write the system clipboard.
		- `camera`: Permission to capture photos or videos from system sources.
		- `microphone`: Permission to capture audio from system sources.

	ValidBLTags: Hardcoded list of valid extension tags.
	StandardReleaseProfile: Strings identifying standardized release profiles, for which a default `ReleaseProfile` object is available.
"""

import enum
import functools
import json
import logging
import typing as typ

import pydantic as pyd
import tomli_w
from frozendict import frozendict

from blext.utils.pydantic_frozen_dict import FrozenDict

####################
# - Blender Tags
####################
ValidBLExtPerms: typ.TypeAlias = typ.Literal[
	'files',
	'network',
	'clipboard',
	'camera',
	'microphone',
]

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
# - Blender Platform
####################
class BLPlatform(enum.StrEnum):
	"""Identifier for a particular kind of OS/Architecture supported by Blender.

	Notes:
		Values correspond perfectly to the platforms defined in the official Blender extension manifest specification.

		**However**, note that there are many nuances and conventions when it comes to cross-platform identification of architectures.
		When interacting with other systems, ensure this is taken into account.

	Corresponds perfectly to the platforms defined in the Blender Extension Manifest.

	See Also:
		- `blext.finders`: Tools for detecting `BLPlatform`s.
	"""

	linux_x64 = 'linux-x64'
	linux_arm64 = 'linux-arm64'
	macos_x64 = 'macos-x64'
	macos_arm64 = 'macos-arm64'
	windows_x64 = 'windows-x64'
	windows_arm64 = 'windows-arm64'

	@functools.cached_property
	def pypi_arches(self) -> frozenset[str]:
		"""Set of PyPi CPU-architecture tags supported by this BLPlatform.

		Notes:
			PyPi is the official platform for distributing Python dependencies as ex. wheels.
			For example, it is the default source for `pip install *`.

			PyPi has its own conventions for tagging CPU architectures, including the `universal*` tags for MacOS.
			Therefore, a bridge must be built, by asking the following question:

				- Each `BLPlatform` **implicitly** supports a number of CPU architectures.
				- Each Python dependency wheel **implicitly** supports a number of CPU architectures.
				- _What's the overlap?_

			This property answers that question using a hard-coded mapping from each BLPlatform,
			to the set of all PyPi CPU architecture tags that should be considered identical.
		"""
		BLP = BLPlatform
		return {
			BLP.linux_x64: frozenset({'x86_64'}),
			BLP.linux_arm64: frozenset({'aarch64', 'armv7l', 'arm64'}),
			BLP.macos_x64: frozenset(
				{'x86_64', 'universal', 'universal2', 'intel', 'fat3', 'fat64'}
			),
			BLP.macos_arm64: frozenset({'arm64', 'universal2'}),
			BLP.windows_x64: frozenset({'', 'amd64'}),
			BLP.windows_arm64: frozenset({'arm64'}),
		}[self]


####################
# - Log Levels
####################
class StrLogLevel(enum.StrEnum):
	"""Enumeration mapping strings to `logging.*` log levels from the standard library."""

	Debug = 'debug'
	Info = 'info'
	Warning = 'warning'
	Error = 'error'
	Critical = 'critical'

	@property
	def log_level(self) -> int:
		"""The integer corresponding to each string log-level.

		Derived from the `logging` module of the standard library.
		"""
		SLL = self.__class__
		return {
			SLL.Debug: logging.DEBUG,
			SLL.Info: logging.INFO,
			SLL.Warning: logging.WARNING,
			SLL.Error: logging.ERROR,
			SLL.Critical: logging.CRITICAL,
		}[self]


####################
# - Release Profiles
####################
StandardReleaseProfile: typ.TypeAlias = typ.Literal[
	'test', 'dev', 'release', 'release-debug'
]


class ReleaseProfile(pyd.BaseModel, frozen=True):
	"""Settings baked into an extension, available from before `register()` is called.

	"Release Profiles" give extension developers a way to make a "release" and/or "debug" version of an extension, in order to do things like:

	- Preconfigure file-based logging in a "debug-release" version, making it easy to gather information from users.
	- Run a "dev" version of the addon for development, ex. to include a web-server that hot-reloads the addon.
	- Run a "test" version of the addon for development, ex. to include a web-server that hot-reloads the addon.

	Notes:
		For now, release profiles are quite limited:

		- Possible options are hard-coded into `blext`; currently, this only includes the ability to set logging fields.
		- Options cannot change an extension specification, beyond hard-coded options.
		- Extensions must explicitly load `init_settings.toml` and use the fields within.
	"""

	init_settings_filename: typ.Literal['init_settings.toml'] = 'init_settings.toml'

	use_log_file: bool
	log_file_name: str
	log_file_level: StrLogLevel
	use_log_console: bool
	log_console_level: StrLogLevel

	overrides: FrozenDict[str, typ.Any] = frozendict()

	@classmethod
	def default_spec(cls, release_profile_id: StandardReleaseProfile) -> typ.Self:
		"""A sensible default for common release profiles."""
		log_file_name = 'addon.log'
		return {
			'test': cls(
				use_log_file=True,
				log_file_name=log_file_name,
				log_file_level=StrLogLevel.Debug,
				use_log_console=True,
				log_console_level=StrLogLevel.Info,
			),
			'dev': cls(
				use_log_file=True,
				log_file_name=log_file_name,
				log_file_level=StrLogLevel.Debug,
				use_log_console=True,
				log_console_level=StrLogLevel.Info,
			),
			'release': cls(
				use_log_file=False,
				log_file_name=log_file_name,
				log_file_level=StrLogLevel.Debug,
				use_log_console=True,
				log_console_level=StrLogLevel.Warning,
			),
			'release-debug': cls(
				use_log_file=True,
				log_file_name=log_file_name,
				log_file_level=StrLogLevel.Debug,
				use_log_console=True,
				log_console_level=StrLogLevel.Info,
			),
		}[release_profile_id]

	def export_init_settings(self, *, fmt: typ.Literal['json', 'toml']) -> str:
		"""Initialization settings for this release profile, as a string.

		Parameters:
			fmt: String format to export initialization settings to.

		Returns:
			Initialization settings as a formatted string.
		"""
		# Parse Model to JSON
		## - JSON is used like a Rosetta Stone, since it is best supported by pydantic.
		json_str = self.model_dump_json(
			include={
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

		msg = f'Cannot export init settings to the given unknown format: {fmt}'  # pyright: ignore[reportUnreachable]
		raise ValueError(msg)
