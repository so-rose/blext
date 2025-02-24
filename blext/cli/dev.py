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

"""Implements the `dev` command."""

import os
import subprocess
import sys
from pathlib import Path

import pydantic as pyd

import blext.exceptions as exc
from blext import finders, loaders, pack, paths

from ._context import APP, CONSOLE, PATH_BL_INIT_PY


@APP.command()
def dev(
	proj: Path | None = None,
	*,
	headless: bool = False,
) -> None:
	"""Launch the extension locally, using Blender.

	Parameters:
		proj: Path to the Blender extension project.
		bl_platform: Blender platform(s) to constrain the extension to.
			Use "detect" to constrain to detect the current platform.
		release_profile: The release profile to apply to the extension.
		format: The text format to show the Blender manifest as.
	"""
	####################
	# - Build Extension
	####################
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = loaders.load_bl_platform_into_spec(
			loaders.load_blext_spec(
				proj_uri=proj,
				release_profile_id='dev',
			),
			bl_platform_ref='detect',
		)

		# Download Wheels
		wheels_changed = blext_spec.wheels_graph.download_wheels(
			path_wheels=paths.path_wheels(blext_spec),
			no_prompt=False,
		)

		# Pack the Blender Extension
		if wheels_changed:
			pack.prepack_bl_extension(blext_spec)
		pack.pack_bl_extension(blext_spec, overwrite=True)

	####################
	# - Run Blender
	####################
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	# Launch Blender
	## - Same as running 'blender --python ./blender_scripts/bl_init.py'
	CONSOLE.print()
	CONSOLE.rule('[bold green]Running Blender')
	CONSOLE.print('[italic]$ blender --factory-startup --python .../bl_init.py')
	CONSOLE.print()
	CONSOLE.rule(characters='--', style='gray')

	path_zip = paths.path_build(blext_spec) / blext_spec.packed_zip_filename
	bl_process = subprocess.Popen(
		[
			blender_exe,
			'--python',
			str(PATH_BL_INIT_PY),
			'--factory-startup',  ## Temporarily Disable All Addons
			*(['--headless'] if headless else []),
		],
		bufsize=0,  ## TODO: Check if -1 is OK
		env=os.environ
		| {
			'BLEXT_ADDON_NAME': blext_spec.id,
			'BLEXT_ZIP_PATH': str(path_zip),
			'BLEXT_LOCAL_PATH': str(paths.path_local(blext_spec)),
		},
		stdout=sys.stdout,
		stderr=sys.stderr,
	)
	_ = bl_process.wait()

	## TODO: A lot of QOL; for instance, CTRL+C really should quit Blender as well.
