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
import typing as typ
from pathlib import Path

import cyclopts
import rich

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


####################
# - Command: Build
####################
@app.command()
def build(
	bl_platform: supported.BLPlatform | None = None,
	proj_path: Path | None = None,
	release_profile: supported.ReleaseProfile = supported.ReleaseProfile.Release,
	_return_blext_spec: typ.Annotated[bool, cyclopts.Parameter(show=False)] = False,
) -> spec.BLExtSpec | None:
	"""[Build] the extension to an installable `.zip` file.

	Parameters:
		bl_platform: The Blender platform to build the extension for.
		proj_path: Path to a `pyproject.toml` or a folder containing a `pyproject.toml`, which specifies the Blender extension.
		release_profile: The release profile to bake into the extension.
	"""
	# Parse CLI
	if bl_platform is None:
		bl_platform = finders.detect_local_blplatform()
	path_proj_spec = finders.find_proj_spec(proj_path)

	# Parse Blender Extension Specification
	blext_spec = spec.BLExtSpec.from_proj_spec(
		path_proj_spec=path_proj_spec,
		release_profile=release_profile,
	).constrain_to_bl_platform(bl_platform)

	# Download Wheels
	wheels.download_wheels(
		blext_spec,
		bl_platform=bl_platform,
		no_prompt=False,
	)

	# Pack the Blender Extension
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
		msg = 'Packed extension did not validate'
		raise ValueError(msg)

	if _return_blext_spec:
		return blext_spec
	return None


####################
# - Command: Dev
####################
@app.command()
def dev(
	proj_path: Path | None = None,
) -> None:
	"""Launch the local [dev] extension w/Blender."""
	# Build the Extension
	blext_spec = build(
		bl_platform=None,
		proj_path=proj_path,
		release_profile=supported.ReleaseProfile.Dev,
		_return_blext_spec=True,
	)

	# Find Blender
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
	# Parse BLExtSpec
	path_proj_spec = finders.find_proj_spec(proj_path)
	blext_spec = spec.BLExtSpec.from_proj_spec(
		path_proj_spec=path_proj_spec,
		release_profile=release_profile,
	)

	# Constrain BLExtSpec to BLPlatform
	if bl_platform is not None:
		blext_spec = blext_spec.constrain_to_bl_platform(bl_platform)

	# Show BLExtSpec
	rich.print(blext_spec)


####################
# - Command: Show Manifest
####################
@app_show.command(name='bl_manifest', group='Information')
def show_bl_manifest(
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
	if bl_platform is None:
		bl_platform = finders.detect_local_blplatform()
	path_proj_spec = finders.find_proj_spec(proj_path)

	# Parse Blender Extension Specification
	blext_spec = spec.BLExtSpec.from_proj_spec(
		path_proj_spec=path_proj_spec,
		release_profile=release_profile,
	)

	# [Maybe] Constrain BLExtSpec to BLPlatform
	if bl_platform is not None:
		blext_spec = blext_spec.constrain_to_bl_platform(bl_platform)

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
	if bl_platform is None:
		bl_platform = finders.detect_local_blplatform()
	path_proj_spec = finders.find_proj_spec(proj_path)

	# Parse Blender Extension Specification
	blext_spec = spec.BLExtSpec.from_proj_spec(
		path_proj_spec=path_proj_spec,
		release_profile=release_profile,
	)

	# [Maybe] Constrain BLExtSpec to BLPlatform
	if bl_platform is not None:
		blext_spec = blext_spec.constrain_to_bl_platform(bl_platform)

	# Show BLExtSpec
	rich.print(blext_spec.init_settings_str)


####################
# - Command: Show Path to Blender
####################
@app_show.command(name='path_blender', group='Paths')
def show_path_blender() -> None:
	"""Display the found path to the Blender executable."""
	blender_exe = finders.find_blender_exe()

	rich.print(blender_exe)


####################
# - Command: Help and Version
####################
app['--help'].group = 'Debug'
app['--version'].group = 'Debug'

app_show['--help'].group = 'Debug'
app_show['--version'].group = 'Debug'
