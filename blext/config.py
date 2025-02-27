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
import logging
import os
import typing as typ
from pathlib import Path

import platformdirs
import pydantic as pyd

from . import extyp

APPNAME = 'blext'
APPAUTHOR = 'blext'


####################
# - Config
####################
class Config(pyd.BaseModel, frozen=True):
	"""Static configuration impacting the runtime behavior of `blext`."""

	####################
	# - Global Cache Path
	####################
	path_global_cache: Path = Path(
		platformdirs.user_cache_dir(
			APPNAME,
			APPAUTHOR,
		)
	)

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

	####################
	# - Global Paths
	####################
	@functools.cached_property
	def path_global_script_cache(self) -> Path:
		"""Path containing root folders for script extensions identified uniquely."""
		path_global_script_cache = self.path_global_cache / 'script_cache'
		path_global_script_cache.mkdir(exist_ok=True)
		return path_global_script_cache

	####################
	# - Finder Overrides
	####################
	## TODO: 'finders' should use / prefer these, but only if they are non-None.
	path_blender_exe: Path | None = None
	path_uv_exe: Path | None = None
	local_bl_platform: extyp.BLPlatform | None = None

	####################
	# - Logging
	####################
	## TODO: Implement 'blext' logging (to be clear: for blext, not for extensions)
	use_log_file: bool = False
	log_file_level: int = logging.DEBUG
	log_file_path: Path = Path(
		platformdirs.user_log_dir(
			APPNAME,
			APPAUTHOR,
		)
	)
	use_log_console: bool = False
	console_file_level: int = logging.INFO

	####################
	# - Build Process
	####################
	## TODO: Implement glob ignores.
	## - Glob from the project root path (for scripts, this is the parent dir of the script path)
	## - A file may not be included in the zip if it matches a path in ignore_globs.
	## - Found items should always be injected at the same relative path in the zip as outside the zip.
	## - Ideally, these could be (configurably) mined from a `.gitignores` file.
	## - Also ideally, certain specific folders ex. .venv could be ignored by default.
	## - **There's also a blender_manifest.toml entry for this**. Maybe that's where to start.
	ignore_globs: frozenset[str] = frozenset({'**/__pycache__/**/*'})

	## TODO: Implement glob prepacking.
	## - Glob from the project root path (for scripts, this is the parent dir of the script path)
	## - Set items are the glob patterns to use as `Path(...).glob(pattern)`
	## - Found items should always be injected at the same relative path in the zip as outside the zip.
	## - Ideally, these could be (configurably) mined from a `.gitattributes` file.
	prepack_globs: frozenset[str] = frozenset()


####################
# - Find Config
####################
# TODO: Load config from various sources.
## - CLI Argument
## - Environment Variables
## - pyproject.toml / script metadata: Of the project itself.
##     - Perhaps a [tool.blext.config] table?
## - Global Config
##
## CyclOpts seems to have what we need.
## - CyclOpts allows altering the default CLI argument dynamically.
## - For instance, an env var / pyproject.toml field can, with precedence, set defaults.
## - One can also define custom functions for ex. parsing script metadata in this way.
## - > https://cyclopts.readthedocs.io/en/stable/config_file.html
## - So a problem remains - how do we alter this global CONFIG?
## - Namespace flattening allows dumping pydantic model as CLI commands.
## - Alternatively, --config.<option> is also allowed.
## - So, one simply dumps "Config" in this way, for every single command.
## - > https://cyclopts.readthedocs.io/en/stable/user_classes.html#namespace-flattening
## - Now, there's a CLI option available for every single Config entity.
## - With this, use 'config.update()' to overwrite the CONFIG that was loaded by default.
##
## ORRR... We discipline ourselves.
## - Fully CLI-based config thing. Let Cyclopts handle everything.
## - Pass "config" as a Parameter(*) to flatten it, and include it in every command.
## - Every command would then be the source of a Config instance...
## - ...allowing easy integration with env vars and pyproject.toml...
## - ...and we could thus stop playing the globals game.
## - We could also use a glass to reuse "proj_uri", "platform" and "profile".
##     - This class could even call out to "loaders" for us.
##     - Thus, we could completely vacuum special blext_spec loading logic in CLI commands.

CONFIG = Config()
