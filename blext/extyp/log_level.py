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
"""

import enum
import logging


####################
# - Log Levels
####################
class BLExtLogLevel(enum.StrEnum):
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
