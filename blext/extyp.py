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

"""Abstrctions useful for working with Blender extension types.

String enumerations are used to provide meaningful, editor-friendly choices that are enforced when appropriate ex. in the CLI interface.
"""

import enum
import functools
import logging
import typing as typ

import pydantic as pyd

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


class BLPlatform(enum.StrEnum):
	"""Operating systems supported by Blender extensions managed by BLExt.

	Corresponds perfectly to the platforms defined in the Blender Extension Manifest.
	"""

	linux_x64 = 'linux-x64'
	linux_arm64 = 'linux-arm64'
	macos_x64 = 'macos-x64'
	macos_arm64 = 'macos-arm64'
	windows_x64 = 'windows-x64'
	windows_arm64 = 'windows-arm64'

	@functools.cached_property
	def pypi_arches(self) -> frozenset[str]:
		"""Set of matching architecture string in PyPi platform tags."""
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


class StrLogLevel(enum.StrEnum):
	"""String log-levels corresponding to log-levels in the `logging` stdlib module."""

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


StandardReleaseProfile: typ.TypeAlias = typ.Literal[
	'test', 'dev', 'release', 'release-debug'
]


class ReleaseProfile(pyd.BaseModel):
	use_log_file: bool
	log_file_name: str
	log_file_level: StrLogLevel
	use_log_console: bool
	log_console_level: StrLogLevel

	@classmethod
	def default_spec(cls, release_profile_id: StandardReleaseProfile) -> typ.Self:
		"""A default, sensible release profile specification."""
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
