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

import typing as typ
from pathlib import Path

import pydantic as pyd

import blext.exceptions as exc
from blext import extyp, loaders, pack, paths, pydeps, ui

from ._context import APP, CONSOLE


@APP.command()
def build(
	proj: Path | None = None,
	*,
	platform: extyp.BLPlatform | typ.Literal['detect'] | None = None,
	profile: extyp.StandardReleaseProfile | str = 'release',
	output: Path | None = None,
	overwrite: bool = True,
	vendor: bool = True,
) -> None:
	"""[Build] the extension to an installable `.zip` file.

	Parameters:
		proj: Path to the Blender extension project.
		bl_platform: Blender platform(s) to constrain the extension to.
			Use "detect" to constrain to detect the current platform.
		profile: The release profile ID to apply to the extension.
		output: Path to the extension zip that will be built.
			Specifying a folder will build the zip within that folder, using the default name.
		overwrite: Whether to overwrite any existing extension `.zip`.
			When `False`, an error will be thrown instead of overwriting an existing extension.
		vendor: Whether to include Python wheel in the extension `.zip`.
			When `False`, a `uv.lock` file will be written to the root of the `.zip` instead.
	"""
	####################
	# - Parse Specification and Paths
	####################
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = loaders.load_bl_platform_into_spec(
			loaders.load_blext_spec(
				proj_uri=proj,
				release_profile_id=profile,
			),
			bl_platform_ref=platform,
		)
	CONSOLE.print(
		f'Selected [bold]{len(blext_spec.bl_platforms)} platform(s)[/bold]: [italic]{", ".join(sorted(blext_spec.bl_platforms))}[/italic]'
	)

	path_wheels = paths.path_wheels(blext_spec)
	path_zip_prepack = paths.path_prepack(blext_spec) / blext_spec.packed_zip_filename
	path_zip = (
		paths.path_build(blext_spec) / blext_spec.packed_zip_filename
		if output is None
		else (output / blext_spec.packed_zip_filename if output.is_dir() else output)
	)
	path_pypkg = paths.path_pypkg(blext_spec)
	path_pysrc = paths.path_pysrc(blext_spec)

	####################
	# - Download Wheels
	####################
	wheels_from_cache = blext_spec.wheels_graph.wheels_from_cache(path_wheels)
	wheels_to_download = blext_spec.wheels_graph.wheels_to_download_to(path_wheels)

	if wheels_from_cache:
		CONSOLE.print(f'Found [bold]{len(wheels_from_cache)} wheel(s)[/bold] in cache')

	with ui.ui_download_wheels(
		wheels_to_download,
		console=CONSOLE,
	) as ui_callbacks:
		pydeps.network.download_wheels(
			wheels_to_download,
			path_wheels=path_wheels,
			cb_start_wheel_download=ui_callbacks.cb_start_wheel_download,
			cb_update_wheel_download=ui_callbacks.cb_update_wheel_download,
			cb_finish_wheel_download=ui_callbacks.cb_finish_wheel_download,
		)

	if wheels_to_download:
		CONSOLE.print(f'Downloaded [bold]{len(wheels_to_download)} wheel(s)[/bold]')

	####################
	# - Pre-Pack the Blender Extension
	####################
	if vendor:
		files_to_prepack = blext_spec.wheels_graph.wheel_paths_to_prepack(path_wheels)
	else:
		files_to_prepack = {paths.path_uv_lock(blext_spec): Path('uv.lock')}

	with ui.ui_prepack_extension(
		files_to_prepack,
		console=CONSOLE,
	) as ui_callbacks:
		prepacked_files = pack.prepack_extension(
			files_to_prepack,
			path_zip_prepack=path_zip_prepack,
			cb_pre_file_write=ui_callbacks.cb_pre_file_write,
			cb_post_file_write=ui_callbacks.cb_post_file_write,
		)

	if prepacked_files:
		CONSOLE.print(f'Pre-packed [bold]{len(prepacked_files)} file(s)[/bold]')

	####################
	# - Pack the Blender Extension
	####################
	with exc.handle(exc.pretty, ValueError):
		pack.pack_bl_extension(
			blext_spec,
			overwrite=overwrite,
			path_zip_prepack=path_zip_prepack,
			path_zip=path_zip,
			path_pypkg=path_pypkg,
			path_pysrc=path_pysrc,
		)

	CONSOLE.print()
	CONSOLE.print(f'Built extension [bold]{blext_spec.id}[/bold]:', path_zip)

	####################
	# - Validate Extension
	####################
	# with exc.handle(exc.pretty, ValueError):
	# blender_exe = finders.find_blender_exe()

	### TODO: Dedicated functions so we can reuse this thing
	# CONSOLE.print()
	# CONSOLE.rule('[bold green]Extension Validation')
	# CONSOLE.print('[italic]$ blender --factory-startup --command extension validate')
	# CONSOLE.print()
	# CONSOLE.rule(characters='--', style='gray')

	# path_zip = paths.path_build(blext_spec) / blext_spec.packed_zip_filename
	# bl_process = subprocess.Popen(
	# [
	# blender_exe,
	# '--factory-startup',  ## Temporarily Disable All Addons
	# '--command',  ## Validate an Extension
	# 'extension',
	# 'validate',
	# str(path_zip),
	# ],
	# bufsize=0,  ## TODO: Check if -1 is OK
	# env=os.environ,
	# stdout=sys.stdout,
	# stderr=sys.stderr,
	# )
	# return_code = bl_process.wait()

	# CONSOLE.rule(characters='--', style='gray')
	# CONSOLE.print()
	# if return_code == 0:
	# CONSOLE.print('[✔] Blender Extension Validation Succeeded')
	# else:
	# with exc.handle(exc.pretty, ValueError):
	# msgs = [
	# 'Blender failed to validate the packed extension. For more information, see the validation logs (above).',
	# ]
	# raise ValueError(*msgs)
