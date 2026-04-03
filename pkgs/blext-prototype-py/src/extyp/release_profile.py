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
import functools
import json
import typing as typ

import pydantic as pyd
import tomli_w
from frozendict import frozendict

from blext.utils.pydantic_frozendict import FrozenDict


####################
# - Release Profiles
####################
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

	init_settings_filename: typ.Literal['release_config.toml'] = 'release_config.toml'

	config: FrozenDict[str, typ.Any] | None = None
	overrides: FrozenDict[str, typ.Any] | None = None

	def export(self, *, fmt: typ.Literal['json', 'toml']) -> str:
		"""Initialization settings for this release profile, as a string.

		Parameters:
			fmt: String format to export initialization settings to.

		Returns:
			Initialization settings as a formatted string.
		"""
		manifest_export: dict[str, typ.Any] = self.model_dump(
			mode='json', exclude_none=True
		)
		match fmt:
			case 'json':
				return json.dumps(manifest_export)
			case 'toml':
				return tomli_w.dumps(manifest_export)


####################
# - Standard Release Profiles
####################
class StandardReleaseProfile(enum.StrEnum):
	"""Strings identifying standardized release profiles, for which a default `ReleaseProfile` object is available."""

	Test = enum.auto()
	Dev = enum.auto()
	Release = enum.auto()
	ReleaseDebug = enum.auto()

	@functools.cached_property
	def release_profile(self) -> ReleaseProfile:
		"""Sensible default fields for common release profiles."""
		log_file_name = 'addon.log'

		SRP = StandardReleaseProfile
		return {
			SRP.Test: ReleaseProfile(
				config=frozendict({
					'use_log_file': True,
					'log_file_name': log_file_name,
					'log_file_level': 'debug',
					'use_log_console': True,
					'log_console_level': 'info',
				})
			),
			SRP.Dev: ReleaseProfile(
				config=frozendict({
					'use_log_file': True,
					'log_file_name': log_file_name,
					'log_file_level': 'debug',
					'use_log_console': True,
					'log_console_level': 'info',
				})
			),
			SRP.Release: ReleaseProfile(
				config=frozendict({
					'use_log_file': False,
					'log_file_level': 'debug',
					'use_log_console': True,
					'log_console_level': 'warning',
				})
			),
			SRP.ReleaseDebug: ReleaseProfile(
				config=frozendict({
					'use_log_file': True,
					'log_file_name': log_file_name,
					'log_file_level': 'debug',
					'use_log_console': True,
					'log_console_level': 'info',
				})
			),
		}[self]
