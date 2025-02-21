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

from . import paths, spec

console = rich.console.Console()


####################
# - Pack Extension to ZIP
####################
def prepack_bl_extension(blext_spec: spec.BLExtSpec) -> None:
	"""Prepare a `.zip` file containing all wheels, but no code.

	Since the wheels tend to be the slowest part of packing an extension, a two-step process allows reusing a base `.zip` file that already contains required wheels.
	"""
	path_zip_prepack = paths.path_prepack(blext_spec) / blext_spec.packed_zip_filename

	# Overwrite
	if path_zip_prepack.is_file():
		path_zip_prepack.unlink()

	console.print()
	console.rule('[bold green]Pre-Packing Extension')
	with zipfile.ZipFile(path_zip_prepack, 'w', zipfile.ZIP_DEFLATED) as f_zip:
		####################
		# - INSTALL: Wheels => /wheels/*.whl
		####################
		total_wheel_size = sum(
			f.stat().st_size
			for f in paths.path_wheels(blext_spec).rglob('*')
			if f.is_file()
		)

		# Setup Progress Bar
		progress = rich.progress.Progress(
			rich.progress.TextColumn(
				'Writing Wheel: {task.description}...',
				table_column=rich.progress.Column(ratio=2),  # pyright: ignore[reportPrivateLocalImportUsage]
			),
			rich.progress.BarColumn(
				bar_width=None,
				table_column=rich.progress.Column(ratio=2),  # pyright: ignore[reportPrivateLocalImportUsage]
			),
			expand=True,
		)
		progress_task = progress.add_task('Writing Wheels...', total=total_wheel_size)

		# Write Wheels
		with rich.progress.Live(progress, console=console, transient=True) as live:
			for wheel_to_zip in paths.path_wheels(blext_spec).rglob('*.whl'):
				f_zip.write(wheel_to_zip, Path('wheels') / wheel_to_zip.name)
				progress.update(
					progress_task,
					description=wheel_to_zip.name,
					advance=wheel_to_zip.stat().st_size,
				)
				live.refresh()

		# Report Done
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
		blext_spec: The extension specification to pack the zip file base on.
		force_prepack: Force pre-packing all wheels into the zip file.
			When not set, the prepack step will always run.
		overwrite: If packing to a zip file that already exists, replace it.
	"""
	path_zip = paths.path_build(blext_spec) / blext_spec.packed_zip_filename
	path_zip_prepack = paths.path_prepack(blext_spec) / blext_spec.packed_zip_filename

	if force_prepack or not path_zip_prepack.is_file():
		prepack_bl_extension(blext_spec)
		## TODO: More robust mechanism for deducing whether to do a prepack?

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
		_ = shutil.copyfile(path_zip_prepack, path_zip)
	console.print('[✔] Copied Prepacked Extension ZIP')

	with zipfile.ZipFile(path_zip, 'a', zipfile.ZIP_DEFLATED) as f_zip:
		####################
		# - INSTALL: Blender Manifest => /blender_manifest.toml
		####################
		with console.status('Writing Extension Manifest...', spinner='dots'):
			f_zip.writestr(
				blext_spec.manifest_filename,
				blext_spec.export_blender_manifest(fmt='toml'),
			)
		console.print('[✔] Wrote Extension Manifest')

		####################
		# - INSTALL: Init Settings => /init_settings.toml
		####################
		with console.status('Writing Init Settings...', spinner='dots'):
			f_zip.writestr(
				blext_spec.init_settings_filename,
				blext_spec.export_init_settings(fmt='toml'),
			)
		console.print('[✔] Wrote Init Settings')

		####################
		# - INSTALL: Addon Files => /*
		####################
		with console.status('Writing Addon Files...', spinner='dots'):
			path_pypkg = paths.path_pypkg(blext_spec)
			path_pysrc = paths.path_pysrc(blext_spec)
			print(path_pysrc)

			# Project: Write Extension Python Package
			if path_pypkg is not None:
				for file_to_zip in path_pypkg.rglob('*'):
					f_zip.write(
						file_to_zip,
						file_to_zip.relative_to(path_pypkg),
					)

			# Script: Write Script String as __init__.py
			elif path_pysrc is not None:
				with path_pysrc.open('r') as f_pysrc:
					pysrc = f_pysrc.read()

				f_zip.writestr(
					'__init__.py',
					pysrc,
				)
			else:
				msg = 'Tried to pack an extension that is neither a project nor a script. Please report this bug.'
				raise RuntimeError(msg)

		console.print('[✔] Wrote Addon Files')

	console.print(f'[✔] Finished Writing: "{path_zip.name}"')


## TODO: Consider supporting a faster ZIP packer, ex. external 7-zip or a Rust module.
## - See https://nickb.dev/blog/deflate-yourself-for-faster-rust-zips/
## - Principle is doing everything in RAM, THEN writing out to disk.
## - This mainly only hurts when prepacking - by the way, aren't wheels already deflated?
