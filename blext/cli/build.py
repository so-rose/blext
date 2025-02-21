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

"""Implements the `build` command."""

import os
import subprocess
import sys
import typing as typ
from pathlib import Path

import pydantic as pyd

import blext.exceptions as exc
from blext import extyp, finders, loaders, pack, paths

from ._context import APP, CONSOLE


@APP.command()
def build(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
) -> None:
	"""[Build] the extension to an installable `.zip` file.

	Parameters:
		proj: Path to the Blender extension project.
		bl_platform: Blender platform(s) to constrain the extension to.
			Use "detect" to constrain to detect the current platform.
		profile: The release profile ID to apply to the extension.
	"""
	####################
	# - Build Extension
	####################
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = loaders.load_bl_platform_into_spec(
			loaders.load_blext_spec(
				proj_uri=proj,
				release_profile_id=profile,
			),
			bl_platform_ref=platform,
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
	# - Validate Extension
	####################
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	## TODO: Dedicated functions so we can reuse this thing
	CONSOLE.print()
	CONSOLE.rule('[bold green]Extension Validation')
	CONSOLE.print('[italic]$ blender --factory-startup --command extension validate')
	CONSOLE.print()
	CONSOLE.rule(characters='--', style='gray')

	path_zip = paths.path_build(blext_spec) / blext_spec.packed_zip_filename
	bl_process = subprocess.Popen(
		[
			blender_exe,
			'--factory-startup',  ## Temporarily Disable All Addons
			'--command',  ## Validate an Extension
			'extension',
			'validate',
			str(path_zip),
		],
		bufsize=0,  ## TODO: Check if -1 is OK
		env=os.environ,
		stdout=sys.stdout,
		stderr=sys.stderr,
	)
	return_code = bl_process.wait()

	CONSOLE.rule(characters='--', style='gray')
	CONSOLE.print()
	if return_code == 0:
		CONSOLE.print('[✔] Blender Extension Validation Succeeded')
	else:
		with exc.handle(exc.pretty, ValueError):
			msgs = [
				'Blender failed to validate the packed extension. For more information, see the validation logs (above).',
			]
			raise ValueError(*msgs)
