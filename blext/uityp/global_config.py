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

"""Implements global configuration of `blext`."""

import functools
import json
import os
import tomllib
import typing as typ
from pathlib import Path

import cyclopts
import platformdirs
import pydantic as pyd
import tomli_w

from blext import blender, extyp

from . import detectors

APPNAME = 'blext'
APPAUTHOR = 'blext'
PATH_GLOBAL_CONFIG = (
	Path(
		platformdirs.user_config_dir(
			appname=APPNAME,
			appauthor=APPAUTHOR,
			ensure_exists=True,
		)
	)
	/ 'config.toml'
)


####################
# - Config
####################
class GlobalConfig(pyd.BaseModel, frozen=True):
	"""Static configuration impacting the runtime behavior of `blext`.

	Notes:
		`path_global_cache` can only be overridden in the user's global configuration file.

	Parameters:
		path_global_cache: Global cache directory of `blext`.
		path_blender_exe: Override path to `blender` executable.
		path_uv_exe: Override path to `uv` executable.
		use_log_file: Write `blext` logs to a file.
		log_file_path: Path to log-file, when enabled.
		log_file_level: Minimum log-level to write to the file.
		use_log_console: Write `blext` logs to the console.
			_Disables interactive output._
		console_file_level: Minimum log-level to write to the console.
	"""

	# Global Cache Path
	path_global_cache: typ.Annotated[
		Path,
		cyclopts.Parameter(
			env_var='BLEXT_PATH_GLOBAL_CACHE',
		),
	] = Path(
		platformdirs.user_cache_dir(
			APPNAME,
			APPAUTHOR,
			ensure_exists=False,
		)
	)

	# Local Information
	local_bl_platform: extyp.BLPlatform = pyd.Field(
		default_factory=detectors.detect_local_bl_platform
	)

	# External Binaries
	path_default_blender_exe: typ.Annotated[
		Path,
		cyclopts.Parameter(
			env_var='BLEXT_PATH_BLENDER_EXE',
		),
	] = pyd.Field(
		default_factory=lambda data: detectors.find_blender_exe(
			data['local_bl_platform']  # pyright: ignore[reportAny]
		),
	)
	path_uv_exe: typ.Annotated[
		Path,
		cyclopts.Parameter(
			env_var='BLEXT_PATH_UV_EXE',
		),
	] = pyd.Field(default_factory=detectors.find_uv_exe)

	####################
	# - Properties: Detect Blender Version
	####################
	@functools.cached_property
	def local_default_bl_version(self) -> extyp.BLVersion:
		"""Blender version derived from running `self.path_default_blender_exe` with `--version`."""
		return blender.detect_blender_version(self.path_default_blender_exe)

	####################
	# - Properties: Global Paths
	####################
	@functools.cached_property
	def path_global_project_cache(self) -> Path:
		"""Path containing root folders for script extensions.

		Notes:
			Each subfolder should be named by the hash of the path to the script it serves.
		"""
		path_global_project_cache = self.path_global_cache / 'project_cache'
		path_global_project_cache.mkdir(exist_ok=True)
		return path_global_project_cache

	@functools.cached_property
	def path_global_download_cache(self) -> Path:
		"""Path containing root folders for downloaded extensions, identified uniquely.

		Notes:
			Each subfolder should be named by the hash of the URL that was downloaded.
		"""
		path_global_download_cache = self.path_global_cache / 'download_cache'
		path_global_download_cache.mkdir(exist_ok=True)
		return path_global_download_cache

	####################
	# - Methods: Import / Export
	####################
	def export_config(self, fmt: typ.Literal['json', 'toml']) -> str:
		"""Global configuration of `blext` as a string.

		Parameters:
			fmt: String format to export global configuration to.

		Returns:
			Global configuration
		"""
		# Parse Model to JSON
		## - JSON is used like a Rosetta Stone, since it is best supported by pydantic.
		json_str = self.model_dump_json(
			include={
				'path_global_cache',
				'path_default_blender_exe',
				'path_uv_exe',
				'local_bl_platform',
			},
			by_alias=True,
		)

		# Return String as Format
		json_dict: dict[str, typ.Any] = json.loads(json_str)
		cfg_dict = {'cfg': json_dict}
		if fmt == 'json':
			return json.dumps(cfg_dict)
		if fmt == 'toml':
			return tomli_w.dumps(cfg_dict)

		msg = f'Cannot export init settings to the given unknown format: {fmt}'  # pyright: ignore[reportUnreachable]
		raise ValueError(msg)

	####################
	# - Creation
	####################
	@classmethod
	def from_config(
		cls, path_config: Path, *, environ: dict[str, str] | None = None
	) -> typ.Self:
		"""Load from config file and given environment variables."""
		# Load Environment Dictionary
		environ = {} if environ is None else environ

		# Load Config File
		try:
			with path_config.open('rb') as f:
				config = tomllib.load(f)
		except FileNotFoundError:
			config = {}

		# Extract Attribute Values
		attr_dict = {}
		for attr in [
			'path_global_cache',
			'local_bl_platform',
			'path_default_blender_exe',
			'path_uv_exe',
		]:
			attr_env_var = 'BLEXT_' + attr.upper()
			if attr_env_var in environ:
				attr_dict[attr] = environ[attr_env_var]
			elif attr in config:
				attr_dict[attr] = config[attr]

		# pydantic Handles the Rest
		return cls(**attr_dict)  # pyright: ignore[reportUnknownArgumentType]

	####################
	# - Validation[path_global_cache]: Ensure that it Exists
	####################
	@pyd.field_validator('path_global_cache', mode='after')
	@classmethod
	def mkdir_path_global_cache(cls, value: Path) -> Path:
		"""Ensure the global cache path exists."""
		# Doesn't Exist: Create Folder
		if not value.exists():
			value.mkdir(parents=True, exist_ok=True)

		# Exists, Not Folder: Error
		elif not value.is_dir():
			msg = f"The global cache path {value} is not a folder, yet it exists. Please remove this path, or adjust blext's global cache path."
			raise ValueError(msg)

		# Exists, Is Folder: Check Read/Write Permissions
		## - I know, I know, "forgiveness vs permission" and all that.
		## - I raise you "explicit is better than implicit".
		## - Why are you reading this? Because you care. Let's get a coffee or something.
		if os.access(value, os.R_OK):
			if os.access(value, os.W_OK):
				return value
			msg = f'The global cache path {value} exists, but is not writable. Please grant `blext` permission to write to this folder.'
			raise ValueError(msg)
		msg = f'The global cache path {value} exists, but is not readable. Please grant `blext` permission to read this folder.'
		raise ValueError(msg)
