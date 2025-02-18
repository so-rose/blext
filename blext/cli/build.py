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
from pathlib import Path

import blext.exceptions as exc
from blext import finders, pack, supported, wheels

from ._context import APP, CONSOLE
from ._parse import parse_bl_platform, parse_blext_spec


@APP.command()
def build(
	proj_path: Path | None = None,
	bl_platform: supported.BLPlatform | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
) -> None:
	"""[Build] the extension to an installable `.zip` file.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Parse CLI
	blext_spec = parse_blext_spec(
		proj_path=proj_path,
		release_profile=release_profile,
	)
	bl_platform = parse_bl_platform(
		blext_spec,
		bl_platform_hint=bl_platform,
		detect=True,
	)
	blext_spec = blext_spec.constrain_to_bl_platform(bl_platform)

	# Download Wheels
	with exc.handle(exc.pretty, ValueError):
		wheels_changed = wheels.download_wheels(
			blext_spec.wheels,
			path_wheels=blext_spec.path_wheels,
			no_prompt=False,
		)
		if wheels_changed:
			pack.prepack_bl_extension(blext_spec)

	# Pack the Blender Extension
	with exc.handle(exc.pretty, ValueError):
		pack.pack_bl_extension(blext_spec, overwrite=True)

	# Validate the Blender Extension
	CONSOLE.print()
	CONSOLE.rule('[bold green]Extension Validation')
	CONSOLE.print('[italic]$ blender --factory-startup --command extension validate')
	CONSOLE.print()
	CONSOLE.rule(characters='--', style='gray')

	blender_exe = str(finders.find_blender_exe())
	bl_process = subprocess.Popen(
		[
			blender_exe,
			'--factory-startup',  ## Temporarily Disable All Addons
			'--command',  ## Validate an Extension
			'extension',
			'validate',
			str(blext_spec.path_zip),
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
