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

"""Implements the concept of "extension location" via the `BLExtLocation` object."""

import base64
import functools
import hashlib
import os
from pathlib import Path

import pydantic as pyd

BLEXT_PROJ_CACHE_DIRNAME = '.blext_cache'
HASH_ALGO_SCRIPTPATH = 'sha256'


####################
# - Blender Extension Location
####################
class BLExtLocation(pyd.BaseModel, frozen=True):
	"""An abstraction of "extension location".

	Extension projects can be found in all kinds of locations:
		- Paths: An extension contained within a script or project path.
		- HTTP URL: A script extension available on the internet.
		- Git Ref: A particular commit on some git repository.

	This object handles the particulars of retrieving extension projects, and in turn,
	exposes standardied information such as:
		- Where can the extension specification be loaded from?
		- Which path can wheels be cached to?

	Notes:
		The following methods must be overridden:
			- `path_spec`

	Parameters:
		path_global_project_cache: Folder where extension data can be placed.
			- Script extensions **must** have their data placed here, since they have no folder to write to.
			- Project extensions **can** have data cached here, if their directory can't/shouldn't be written to.
		path_global_download_cache: Folder where downloaded files can be placed.
		force_global_project_cache: Force the use of the global project cache, even when a local project cache can be used.
	"""

	path_global_project_cache: Path
	path_global_download_cache: Path

	force_global_project_cache: bool = False

	####################
	# - Overrides
	####################
	@functools.cached_property
	def path_spec(self) -> Path:
		"""Path to a file from which the extension specification can be loaded.

		Notes:
			It is up to the implementation to define how this file comes about.
			For instance, the file might be searched for, downloaded, or even generated just in time.

			The resulting file is only guaranteed to be _theoretically capable_ of containing an extension specification.
			No guarantee is made here to whether the _contents_ of this file can actually produce a valid extension specification.

		See Also:
			- See `blext.spec.BLExtSpec` for more on how a valid specification path is parsed.
		"""
		raise NotImplementedError

	####################
	# - Classification
	####################
	@functools.cached_property
	def is_script_extension(self) -> bool:
		"""Whether the specified extension is a single-file script extension."""
		return self.path_spec.name.endswith('.py')

	@functools.cached_property
	def is_project_extension(self) -> bool:
		"""Whether the specified extension is a project extension."""
		return self.path_spec.name == 'pyproject.toml'

	####################
	# - Extension Source Code Path
	####################
	@functools.cached_property
	def path_uv_lock(self) -> Path:
		"""Path to the `blext` project's `uv.lock` file."""
		if self.is_project_extension:
			return self.path_spec.parent / 'uv.lock'

		if self.is_script_extension:
			return self.path_spec.parent / (self.path_spec.name + '.lock')

		msg = f"Extension project path ({self.path_spec}) is neither a script extension or a project extension. This shouldn't happen."
		raise RuntimeError(msg)

	def path_pysrc(self, pkg_name: str) -> Path:
		"""Path to the extension source code.

		Parameters:
			pkg_name: Name of the Blender extension.
				Only used when `self.is_project_extension` is `True`.

		Returns:
			- Project Extension: Path to a Python package directory.
			- Script Extension: Path to a Python script.
		"""
		if self.is_project_extension:
			package_path = self.path_spec.parent / pkg_name
			if package_path.is_dir():
				return self.path_spec.parent / pkg_name

			msg = f'The extension project name, {pkg_name}, does not have a Python package with the same name at: {self.path_spec.parent / pkg_name}'
			raise ValueError(msg)

		if self.is_script_extension:
			return self.path_spec

		msg = f"Extension project path ({self.path_spec}) is neither a script extension or a project extension. This shouldn't happen."
		raise RuntimeError(msg)

	####################
	# - Extension Data Path
	####################
	@functools.cached_property
	def path_project_cache(self) -> Path:
		"""The project cache to use when building and/or managing this specification.

		Notes:
			This folder is guaranteed to exist, and to be writable.
			_No guarantees are made about the folder's contents, ex. source code or lockfiles_.
		"""
		force_global_proj_cache = self.force_global_project_cache

		####################
		# - Local Project Cache
		####################
		if self.is_project_extension and not force_global_proj_cache:
			path_proj_root = self.path_spec.parent

			# Check Permissions
			## - READ: Local project root must be readable - no fallback.
			## - WRITE: Local project root must be writable - fallback to global project cache.
			if os.access(path_proj_root, os.R_OK):
				# WRITE|T: Return Project Cache
				if os.access(path_proj_root, os.W_OK):
					path_proj_cache = path_proj_root / BLEXT_PROJ_CACHE_DIRNAME
					path_proj_cache.mkdir(exist_ok=True)
					return path_proj_cache

				# WRITE|F: Fallback to global project cache.
				force_global_proj_cache = True
			else:
				msg = f'Tried to register root path {path_proj_root}, but is not readable. Please grant `blext` permission to read this folder.'
				raise ValueError(msg)

		####################
		# - Global Project Cache
		####################
		if self.is_script_extension or force_global_proj_cache:
			# Generate Hash of Project Spec Path
			## - The hash is not portable between platforms - but it doesn't need to be!
			hasher = hashlib.new(HASH_ALGO_SCRIPTPATH)
			hasher.update(str(self.path_spec.resolve()).encode())
			unique_script_id = base64.b64encode(hasher.digest(), altchars=b'+-').decode(
				'utf-8'
			)[:-1]  ## Chop off the = suffix

			# Generate Global Project Cache Path
			## - What to hash as global project cache key was chosen carefully.
			##     - Hashing script contents would provoke too many rebuilds, but allow renaming.
			##     - Hashing script path allows in-place changes, with rebuild on rename.
			path_proj_root = self.path_global_project_cache / unique_script_id
			path_proj_root.mkdir(exist_ok=True)

			return path_proj_root

		msg = f"Could not generate extension project path for ({self.path_spec}). This shouldn't happen."
		raise ValueError(msg)

	####################
	# - Cache Paths
	####################
	@functools.cached_property
	def path_wheel_cache(self) -> Path:
		"""Wheel cache folder for this extension project.

		Notes:
			When pre-packing extension zips, the pre-packed result is written to this folder.
		"""
		path_wheel_cache = self.path_project_cache / 'wheel_cache'
		path_wheel_cache.mkdir(exist_ok=True)
		return path_wheel_cache

	@functools.cached_property
	def path_prepack_cache(self) -> Path:
		"""Pre-pack cache folder for this extension project.

		Notes:
			When pre-packing extension zips, the pre-packed result is written to this folder.
		"""
		path_prepack_cache = self.path_project_cache / 'prepack_cache'
		path_prepack_cache.mkdir(exist_ok=True)
		return path_prepack_cache

	@functools.cached_property
	def path_build_cache(self) -> Path:
		"""Pre-pack cache folder for this extension project.

		Notes:
			When pre-packing extension zips, the pre-packed result is written to this folder.
		"""
		# Script Parent Writable: Use as Build Cache
		if self.is_script_extension and os.access(self.path_spec.parent, os.W_OK):
			return self.path_spec.parent

		## When the script parent is not writable, fallback to building in the global cache.

		path_prepack_cache = self.path_project_cache / 'build_cache'
		path_prepack_cache.mkdir(exist_ok=True)
		return path_prepack_cache
