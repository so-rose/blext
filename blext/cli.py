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

"""A `typer`-based command line interface for the `blext` project manager."""

import os
import subprocess
import sys
from pathlib import Path

import cyclopts
import pydantic as pyd
import rich

from . import exceptions as exc
from . import finders, pack, spec, supported, wheels

console = rich.console.Console()
app = cyclopts.App(
	name='blext',
	help='blext simplifies the development and management of Blender extensions.',
	help_format='markdown',
)

####################
# - Constants
####################
PATH_BL_INIT_PY: Path = (
	Path(__file__).resolve().parent / 'blender_python' / 'bl_init.py'
)


def _parse(
	*,
	bl_platform: supported.BLPlatform | None = None,
	proj_path: Path | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
	detect_bl_platform: bool = True,
) -> tuple[supported.BLPlatform | None, spec.BLExtSpec]:
	# Parse CLI
	with exc.handle(exc.pretty, ValueError):
		path_proj_spec = finders.find_proj_spec(proj_path)

	# Parse Blender Extension Specification
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		universal_blext_spec = spec.BLExtSpec.from_proj_spec(
			path_proj_spec=path_proj_spec,
			release_profile=release_profile,
		)

	# Deduce BLPlatform
	if bl_platform is not None:
		_bl_platform = bl_platform
	elif bl_platform is None and detect_bl_platform:
		with exc.handle(exc.pretty, ValueError):
			_bl_platform = finders.detect_local_blplatform()
	else:
		return (None, universal_blext_spec)

	return (
		_bl_platform,
		universal_blext_spec.constrain_to_bl_platform(_bl_platform),
	)


####################
# - Command: Build
####################
@app.command()
def build(
	bl_platform: supported.BLPlatform | None = None,
	proj_path: Path | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
) -> None:
	"""[Build] the extension to an installable `.zip` file.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Parse CLI
	bl_platform, blext_spec = _parse(
		bl_platform=bl_platform,
		proj_path=proj_path,
		release_profile=release_profile,
	)

	# Download Wheels
	with exc.handle(exc.pretty, ValueError):
		wheels.download_wheels(
			blext_spec,
			bl_platform=bl_platform,
			no_prompt=False,
		)

	# Pack the Blender Extension
	with exc.handle(exc.pretty, ValueError):
		pack.pack_bl_extension(blext_spec, overwrite=True)

	# Validate the Blender Extension
	console.print()
	console.rule('[bold green]Extension Validation')

	console.print('[italic]$ blender --factory-startup --command extension validate')
	console.print()
	console.rule(characters='--', style='gray')

	blender_exe = finders.find_blender_exe()
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

	console.rule(characters='--', style='gray')
	console.print()
	if return_code == 0:
		console.print('[✔] Blender Extension Validation Succeeded')
	else:
		with exc.handle(exc.pretty, ValueError):
			msgs = [
				'Blender failed to validate the packed extension. For more information, see the validation logs (above).',
			]
			raise ValueError(*msgs)


####################
# - Command: Dev
####################
@app.command()
def dev(
	proj_path: Path | None = None,
) -> None:
	"""Launch the local [dev] extension w/Blender."""
	# Parse CLI
	release_profile = supported.ReleaseProfile.Dev
	bl_platform, blext_spec = _parse(
		bl_platform=None,
		proj_path=proj_path,
		release_profile=release_profile,
	)

	# Build the Extension
	build(
		bl_platform=None,
		proj_path=proj_path,
		release_profile=supported.ReleaseProfile.Dev,
	)

	# Find Blender
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	# Launch Blender
	## - Same as running 'blender --python ./blender_scripts/bl_init.py'
	console.print()
	console.rule('[bold green]Running Blender')
	console.print('[italic]$ blender --factory-startup --python .../bl_init.py')
	console.print()
	console.rule(characters='--', style='gray')

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
	bl_process.wait()


####################
# - Command: Show
####################
app_show = cyclopts.App(name='show', help='[Show] information about the extension.')
app.command(app_show)


####################
# - Command: Show Spec
####################
@app_show.command(name='spec', group='Information')
def show_spec(
	bl_platform: supported.BLPlatform | None = None,
	proj_path: Path | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
) -> None:
	"""Print the complete extension specification.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Parse CLI
	_, blext_spec = _parse(
		bl_platform=bl_platform,
		proj_path=proj_path,
		release_profile=release_profile,
		detect_bl_platform=False,
	)

	# Show BLExtSpec
	rich.print(blext_spec)


####################
# - Command: Show Manifest
####################
@app_show.command(name='manifest', group='Information')
def show_manifest(
	bl_platform: supported.BLPlatform | None = None,
	proj_path: Path | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
) -> None:
	"""Print the generated Blender extension manifest.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Parse CLI
	_, blext_spec = _parse(
		bl_platform=bl_platform,
		proj_path=proj_path,
		release_profile=release_profile,
		detect_bl_platform=False,
	)

	# Show BLExtSpec
	rich.print(blext_spec.manifest_str)


@app_show.command(name='init_settings', group='Information')
def show_init_settings(
	bl_platform: supported.BLPlatform | None = None,
	proj_path: Path | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
) -> None:
	"""Print the generated initial settings for the release profile.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Parse CLI
	_, blext_spec = _parse(
		bl_platform=bl_platform,
		proj_path=proj_path,
		release_profile=release_profile,
		detect_bl_platform=False,
	)

	# Show BLExtSpec
	rich.print(blext_spec.init_settings_str)


####################
# - Command: Show Path to Blender
####################
@app_show.command(name='path_blender', group='Paths')
def show_path_blender() -> None:
	"""Display the found path to the Blender executable."""
	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe()

	rich.print(blender_exe)


####################
# - Command: Help and Version
####################
app['--help'].group = 'Debug'
app['--version'].group = 'Debug'

app_show['--help'].group = 'Debug'
app_show['--version'].group = 'Debug'
