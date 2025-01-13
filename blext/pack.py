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

"""Contains tools and procedures that deterministically and reliably packages the Blender extension.

This involves parsing and validating the plugin configuration from `pyproject.toml`, generating the extension manifest, downloading the correct platform-specific binary wheels for distribution, and zipping it all up together.
"""

import shutil
import zipfile
from pathlib import Path

import rich
import rich.progress
import rich.prompt

from blext import spec

console = rich.console.Console()


####################
# - Pack Extension to ZIP
####################
def prepack_bl_extension(blext_spec: spec.BLExtSpec) -> None:
	"""Prepare a `.zip` file containing all wheels, but no code.

	Since the wheels tend to be the slowest part of packing an extension, a two-step process allows reusing a base `.zip` file that already contains required wheels.
	"""
	# Overwrite
	if blext_spec.path_zip_prepack.is_file():
		blext_spec.path_zip_prepack.unlink()

	console.print()
	console.rule('[bold green]Pre-Packing Extension')
	with zipfile.ZipFile(
		blext_spec.path_zip_prepack, 'w', zipfile.ZIP_DEFLATED
	) as f_zip:
		# Install Wheels @ /wheels/*
		## Setup UI
		total_wheel_size = sum(
			f.stat().st_size for f in blext_spec.path_wheels.rglob('*') if f.is_file()
		)
		progress = rich.progress.Progress(
			rich.progress.TextColumn(
				'Writing Wheel: {task.description}...',
				table_column=rich.progress.Column(ratio=2),
			),
			rich.progress.BarColumn(
				bar_width=None,
				table_column=rich.progress.Column(ratio=2),
			),
			expand=True,
		)
		progress_task = progress.add_task('Writing Wheels...', total=total_wheel_size)

		## Write Wheels
		with rich.progress.Live(progress, console=console, transient=True) as live:
			for wheel_to_zip in blext_spec.path_wheels.rglob('*.whl'):
				f_zip.write(wheel_to_zip, Path('wheels') / wheel_to_zip.name)
				progress.update(
					progress_task,
					description=wheel_to_zip.name,
					advance=wheel_to_zip.stat().st_size,
				)
				live.refresh()

		console.print('[✔] Wrote Wheels')


def pack_bl_extension(
	blext_spec: spec.BLExtSpec,
	*,
	force_prepack: bool = False,
	overwrite: bool = False,
) -> None:
	"""Pack all files needed by a Blender extension, into an installable `.zip`.

	Configuration data is sourced from `paths`, which in turns sources much of its user-facing configuration from `pyproject.toml`.

	Parameters:
		profile: Selects a predefined set of initial extension settings from a `[tool.bl_ext.profiles]` table in `pyproject.toml`.
		os: The operating system to pack the extension for.
		force_prepack: Force pre-packing all wheels into the zip file.
		overwrite: Replace the zip file if it already exists.
	"""
	path_zip = blext_spec.path_zip
	if force_prepack or not blext_spec.path_zip_prepack.is_file():
		prepack_bl_extension(blext_spec)

	# Overwrite Existing ZIP
	if path_zip.is_file():
		if not overwrite:
			msg = f"File already exists where extension ZIP would be generated  at '{path_zip}'"
			raise ValueError(msg)
		path_zip.unlink()

	# Pack Extension
	console.print()
	console.rule('[bold green]Packing Extension')
	console.print(f'[italic]Writing to: {path_zip.parent}')
	console.print()

	## Copy Prepacked ZIP and Finish Packing
	with console.status('Copying Prepacked ZIP...', spinner='dots'):
		shutil.copyfile(blext_spec.path_zip_prepack, path_zip)
	console.print('[✔] Copied Prepacked Extension ZIP')

	with zipfile.ZipFile(path_zip, 'a', zipfile.ZIP_DEFLATED) as f_zip:
		# Write Blender Extension Manifest @ /blender_manifest.toml
		with console.status('Writing Extension Manifest...', spinner='dots'):
			f_zip.writestr(
				blext_spec.manifest_filename,
				blext_spec.manifest_str,
			)
		console.print('[✔] Wrote Extension Manifest')

		# Write Init Settings @ /init_settings.toml
		with console.status('Writing Init Settings...', spinner='dots'):
			f_zip.writestr(
				blext_spec.init_settings_filename,
				blext_spec.init_settings_str,
			)
		console.print('[✔] Wrote Init Settings')

		# Install Addon Files @ /*
		with console.status('Writing Addon Files...', spinner='dots'):
			for file_to_zip in blext_spec.path_pkg.rglob('*'):
				f_zip.write(
					file_to_zip,
					file_to_zip.relative_to(blext_spec.path_pkg),
				)
		console.print('[✔] Wrote Addon Files')

	console.print(f'[✔] Finished Writing: "{path_zip.name}"')
