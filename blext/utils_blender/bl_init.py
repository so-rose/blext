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


"""Startup script for Blender, which (re)installs and runs an extension locally."""

import os
import tomllib
import zipfile
from pathlib import Path

import addon_utils
import bpy

####################
# - Constants
####################
# Zip Path
if os.environ.get('BLEXT_ZIP_PATH') is not None:
	BLEXT_ZIP_PATH = Path(os.environ['BLEXT_ZIP_PATH'])
else:
	msg = "The env var 'BLEXT_ZIP_PATH' must be available, but it is not"
	raise ValueError(msg)

BLEXT_DEV_REPO_NAME = 'blext_dev_repo'


####################
# - main()
####################
if __name__ == '__main__':
	# Parse Blender Manifest
	with zipfile.ZipFile(BLEXT_ZIP_PATH) as f_zip:
		blender_manifest_str = f_zip.read('blender_manifest.toml').decode('utf-8')
		blender_manifest = tomllib.loads(blender_manifest_str)

	####################
	# - Set Preferences
	####################
	# Suppress Splash Screen
	## - It just gets in the way.
	bpy.context.preferences.view.show_splash = False

	####################
	# - Install Local Repository
	####################
	# Check for Local Dev Repo
	## - Create if non-existant.
	if BLEXT_DEV_REPO_NAME not in {
		repo.name for repo in bpy.context.preferences.extensions.repos
	}:
		bpy.ops.preferences.extension_repo_add(
			name=BLEXT_DEV_REPO_NAME,
			remote_url='',
			use_access_token=False,
			use_sync_on_startup=False,
			# use_custom_directory=True,
			# custom_directory=str(BLEXT_LOCAL_PATH),
			type='LOCAL',
		)

	# Get the Repository Index of Local Dev Repo
	dev_repo_idx = next(
		repo_idx
		for repo_idx, repo in enumerate(bpy.context.preferences.extensions.repos)
		if repo.name == BLEXT_DEV_REPO_NAME
	)
	dev_repo_module = next(
		repo.module
		for repo_idx, repo in enumerate(bpy.context.preferences.extensions.repos)
		if repo.name == BLEXT_DEV_REPO_NAME
	)

	####################
	# - Uninstall Existing Addon
	####################
	# Uninstall Existing Addon
	blext_pkg = f'bl_ext.{BLEXT_DEV_REPO_NAME}.{blender_manifest["id"]}'
	if blender_manifest['id'] in bpy.context.preferences.addons.keys() or blext_pkg in [  # noqa: SIM118
		addon_module.__name__ for addon_module in addon_utils.modules()
	]:
		bpy.ops.extensions.package_uninstall(
			repo_index=dev_repo_idx,
			pkg_id=blender_manifest['id'],
		)
		## sys.modules is vacuumed (though not for deps) as part of package_uninstall.

	# Install New Extension
	bpy.ops.extensions.package_install_files(
		#'INVOKE_DEFAULT',
		repo=dev_repo_module,
		filepath=str(BLEXT_ZIP_PATH),
		enable_on_install=True,
	)
