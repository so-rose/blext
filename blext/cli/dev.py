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

import blext.exceptions as exc
from blext import finders, supported

from ._context import APP, CONSOLE, PATH_BL_INIT_PY
from ._parse import parse_bl_platform, parse_blext_spec
from .build import build


@APP.command()
def dev(
	proj_path: Path | None = None,
) -> None:
	"""Launch the local [dev] extension w/Blender."""
	# Parse CLI
	blext_spec = parse_blext_spec(
		proj_path=proj_path,
		release_profile=supported.ReleaseProfile.Dev,
	)
	bl_platform = parse_bl_platform(blext_spec, detect=True)
	blext_spec = blext_spec.constrain_to_bl_platform(bl_platform)

	# Build the Extension
	build(
		bl_platform=bl_platform,
		proj_path=proj_path,
		release_profile=supported.ReleaseProfile.Dev,
	)

	# Find Blender
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	# Launch Blender
	## - Same as running 'blender --python ./blender_scripts/bl_init.py'
	CONSOLE.print()
	CONSOLE.rule('[bold green]Running Blender')
	CONSOLE.print('[italic]$ blender --factory-startup --python .../bl_init.py')
	CONSOLE.print()
	CONSOLE.rule(characters='--', style='gray')

	bl_process = subprocess.Popen(
		[
			blender_exe,
			'--python',
			str(PATH_BL_INIT_PY),
			'--factory-startup',  ## Temporarily Disable All Addons
		],
		bufsize=0,  ## TODO: Check if -1 is OK
		env=os.environ
		| {
			'BLEXT_ADDON_NAME': blext_spec.id,
			'BLEXT_ZIP_PATH': str(blext_spec.path_zip),
			'BLEXT_LOCAL_PATH': str(blext_spec.path_local),
		},
		stdout=sys.stdout,
		stderr=sys.stderr,
	)
	_ = bl_process.wait()
