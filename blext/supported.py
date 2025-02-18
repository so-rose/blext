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

"""Constrained sets of strings denoting some supported set of values.

String enumerations are used to provide meaningful, editor-friendly choices that are enforced when appropriate ex. in the CLI interface.
"""

import enum
import functools
import logging


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


class ReleaseProfile(enum.StrEnum):
	"""Release profiles supported by Blender extensions managed by BLExt."""

	Test = 'test'
	Dev = 'dev'
	Release = 'release'
	ReleaseDebug = 'release-debug'


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
