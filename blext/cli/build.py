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

"""Implements `blext build`."""

import typing as typ
from pathlib import Path

import cyclopts
import pydantic as pyd

import blext.exceptions as exc
from blext import pack, pydeps, ui

from ._context import (
	APP,
	CONSOLE,
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
	ParameterProj,
)
from .check import check


@APP.command()
def build(  # noqa: PLR0913
	proj: ParameterProj = None,
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	global_config: ParameterConfig = DEFAULT_CONFIG,
	output: typ.Annotated[
		Path | None,
		cyclopts.Parameter(name=['--output', '-o']),
	] = None,
	overwrite: bool = True,
	vendor: bool = True,
	check_output: bool = True,
) -> None:
	"""Build an extension project.

	Parameters:
		proj: Location specifier for `blext` projects.
		blext_info: Information used to find and load `blext` project.
		global_config: Loaded global configuration.
		output: Write built extension to this file / folder.
		overwrite: Allow overwriting `.zip`.
		vendor: Include dependencies as wheels in the `.zip`.
			When `False`, write `uv.lock` to the extension.
		check_output: Run `blext check` on the packed `.zip`.
	"""
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_info = blext_info.parse_proj(proj)
		blext_location = blext_info.blext_location(global_config)

	####################
	# - Parse Specification and Paths
	####################
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		blext_spec = blext_info.blext_spec(global_config)

	path_zip_prepack = (
		blext_location.path_prepack_cache / blext_spec.packed_zip_filename
	)
	path_zip = (
		blext_location.path_build_cache / blext_spec.packed_zip_filename
		if output is None
		else (output / blext_spec.packed_zip_filename if output.is_dir() else output)
	)

	####################
	# - Report Platform Detection
	####################
	match blext_info.platform:
		case ():
			CONSOLE.print(
				f'Selected [bold]all {len(blext_spec.bl_platforms)} extension-supported platform(s)[/bold]: [italic]{", ".join(sorted(blext_spec.bl_platforms))}[/italic]'
			)
		case ('detect',):
			CONSOLE.print(
				f'Selected [bold]only detected platform[/bold]: [italic]{next(iter(blext_spec.bl_platforms))}[/italic]'
			)
		case _:
			CONSOLE.print(
				f'Selected [bold]{len(blext_spec.bl_platforms)} platform(s)[/bold]: [italic]{", ".join(sorted(blext_spec.bl_platforms))}[/italic]'
			)

	####################
	# - Download Wheels
	####################
	with exc.handle(exc.pretty, ValueError, pyd.ValidationError):
		wheels_in_cache = blext_spec.wheels_graph.wheels_in_cache(
			blext_location.path_wheel_cache
		)
	if wheels_in_cache:
		CONSOLE.print(
			f'Found [bold]{len(wheels_in_cache)} wheel(s)[/bold] in download cache'
		)

	wheels_to_download = blext_spec.wheels_graph.wheels_to_download_to(
		blext_location.path_wheel_cache
	)
	with ui.ui_download_wheels(
		wheels_to_download,
		console=CONSOLE,
	) as ui_callbacks:
		pydeps.network.download_wheels(
			wheels_to_download,
			path_wheels=blext_location.path_wheel_cache,
			cb_start_wheel_download=ui_callbacks.cb_start_wheel_download,
			cb_update_wheel_download=ui_callbacks.cb_update_wheel_download,
			cb_finish_wheel_download=ui_callbacks.cb_finish_wheel_download,
		)

	if wheels_to_download:
		CONSOLE.print(f'Downloaded [bold]{len(wheels_to_download)} wheel(s)[/bold]')

	####################
	# - Pre-Pack Extension
	####################
	if vendor:
		files_to_prepack = blext_spec.wheels_graph.wheel_paths_to_prepack(
			blext_location.path_wheel_cache
		)
	else:
		raise NotImplementedError

	existing_prepacked_zipfiles = pack.existing_prepacked_files(
		files_to_prepack, path_zip_prepack=path_zip_prepack
	)
	if existing_prepacked_zipfiles:
		CONSOLE.print(
			f'Found [bold]{len(existing_prepacked_zipfiles)} file(s)[/bold] in pre-pack cache'
		)

	files_to_prepack = {
		path: zipfile_path
		for path, zipfile_path in files_to_prepack.items()
		if zipfile_path not in existing_prepacked_zipfiles
	}
	with ui.ui_prepack_extension(
		files_to_prepack,
		console=CONSOLE,
	) as ui_callbacks:
		pack.prepack_extension(
			files_to_prepack,
			path_zip_prepack=path_zip_prepack,
			cb_pre_file_write=ui_callbacks.cb_pre_file_write,  # pyright: ignore[reportArgumentType]
			cb_post_file_write=ui_callbacks.cb_post_file_write,  # pyright: ignore[reportArgumentType]
		)

	if files_to_prepack:
		CONSOLE.print(f'Pre-packed [bold]{len(files_to_prepack)} file(s)[/bold]')

	####################
	# - Pack Extension
	####################
	with exc.handle(exc.pretty, ValueError):
		pack.pack_bl_extension(
			blext_spec,
			overwrite=overwrite,
			path_zip_prepack=path_zip_prepack,
			path_zip=path_zip,
			path_pysrc=blext_location.path_pysrc(blext_spec.id),
		)

	####################
	# - Check Extension
	####################
	if check_output:
		check(blext_info=ui.BLExtInfo(path=path_zip), global_config=global_config)

	####################
	# - Report Success
	####################
	CONSOLE.print()
	CONSOLE.print(f'Built extension [bold]{blext_spec.id}[/bold]:', path_zip)
