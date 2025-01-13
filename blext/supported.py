"""Constrained sets of strings denoting some supported set of values.

String enumerations are used to provide meaningful, editor-friendly choices that are enforced when appropriate ex. in the CLI interface.
"""

import enum
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


class ReleaseProfile(enum.StrEnum):
	"""Release profiles supported by Blender extensions managed by BLExt."""

	Test = 'test'
	Dev = 'dev'
	Release = 'release'
	ReleaseDebug = 'release-debug'


class StrLogLevel(enum.StrEnum):
	"""String log-levels corresponding to log-levels in the `logging` stdlib module."""

	Debug = 'DEBUG'
	Info = 'INFO'
	Warning = 'WARNING'
	Error = 'ERROR'
	Critical = 'CRITICAL'

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
