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
import typing as typ
import zipfile
from pathlib import Path

from . import spec


####################
# - Pack Extension to ZIP
####################
def prepack_extension(
	files_to_prepack: dict[Path, Path],
	*,
	path_zip_prepack: Path,
	cb_pre_file_write: typ.Callable[[Path, Path], typ.Any] = lambda *_: None,
	cb_post_file_write: typ.Callable[[Path, Path], typ.Any] = lambda *_: None,
) -> dict[Path, Path]:
	"""Prepare a `.zip` file containing all wheels, but no code.

	Notes:
		Since the wheels tend to be the slowest part of packing an extension, a two-step process allows reusing a base `.zip` file that already contains required wheels.

	Parameters:
		blext_spec: The Blender extension specification to pre-pack.
		vendor: Whether to pack all wheel dependencies.
			When false, `uv.lock` will be written to the `.zip` root.
		path_zip_prepack: Path to the prepacked `.zip` file.
			Defaults to `paths.path_zip_prepack(blext_spec) / blext_spec.packed_zip_filename`
		path_wheels: Path to downloaded wheels, when `vendor=True`.
			Defaults to `paths.path_zip_prepack(blext_spec) / blext_spec.packed_zip_filename`

	Raises:
		ValueError: When not all wheels required by `blext_spec` are found in `path_wheels`.
	"""
	file_sizes = {path: path.stat().st_size for path in files_to_prepack}

	if path_zip_prepack.is_file():
		with zipfile.ZipFile(path_zip_prepack, 'r') as f_zip:
			existing_prepacked_files = set({Path(name) for name in f_zip.namelist()})

		# Re-Pack to Delete Files
		## - Deleting a single file from a .zip archive is not always a good idea.
		## - See https://github.com/python/cpython/pull/103033
		## - Instead, when a file should be deleted, we repack the entire `.zip`.
		_files_to_prepack_values = frozenset(files_to_prepack.values())
		if any(
			existing_zipfile_path not in _files_to_prepack_values
			for existing_zipfile_path in existing_prepacked_files
		):
			path_zip_prepack.unlink()
			existing_prepacked_files.clear()
	else:
		existing_prepacked_files: set[Path] = set()

	# Create Zipfile
	with zipfile.ZipFile(path_zip_prepack, 'a', zipfile.ZIP_DEFLATED) as f_zip:
		####################
		# - INSTALL: Files => /wheels/*.whl
		####################
		remaining_files_to_prepack = {
			path: zipfile_path
			for path, zipfile_path in files_to_prepack.items()
			if zipfile_path not in existing_prepacked_files
		}

		for path, zipfile_path in sorted(
			remaining_files_to_prepack.items(), key=lambda el: file_sizes[el[0]]
		):
			cb_pre_file_write(path, zipfile_path)
			f_zip.write(path, zipfile_path)
			cb_post_file_write(path, zipfile_path)

	return remaining_files_to_prepack


def pack_bl_extension(
	blext_spec: spec.BLExtSpec,
	*,
	overwrite: bool = True,
	path_zip_prepack: Path,
	path_zip: Path,
	path_pypkg: Path | None,
	path_pysrc: Path | None,
	cb_update_status: typ.Callable[[str], list[None] | None] = lambda *_: None,
) -> None:
	"""Pack all files needed by a Blender extension, into an installable `.zip`.

	Configuration data is sourced from `paths`, which in turns sources much of its user-facing configuration from `pyproject.toml`.

	Parameters:
		blext_spec: The extension specification to pack the zip file base on.
		force_prepack: Force pre-packing all wheels into the zip file.
			When not set, the prepack step will always run.
		overwrite: If packing to a zip file that already exists, replace it.
	"""
	if not path_zip_prepack.is_file():
		msg = f'Cannot pack extension, since no pre-packed extension was found at {path_zip_prepack}.'
		raise RuntimeError(msg)

	# Overwrite Existing ZIP
	if path_zip.is_file():
		if not overwrite:
			msg = f'File already exists where extension ZIP is to be built: {path_zip}'
			raise ValueError(msg)
		path_zip.unlink()

	# Copy Pre-Packed ZIP
	cb_update_status('Copying Pre-Packed Extension ZIP')
	_ = shutil.copyfile(path_zip_prepack, path_zip)

	with zipfile.ZipFile(path_zip, 'a', zipfile.ZIP_DEFLATED) as f_zip:
		####################
		# - INSTALL: Blender Manifest => /blender_manifest.toml
		####################
		cb_update_status('Writing `blender_manifest.toml`')
		f_zip.writestr(
			blext_spec.manifest_filename,
			blext_spec.export_blender_manifest(fmt='toml'),
		)

		####################
		# - INSTALL: Init Settings => /init_settings.toml
		####################
		cb_update_status('Writing `init_settings.toml`')
		f_zip.writestr(
			blext_spec.init_settings_filename,
			blext_spec.export_init_settings(fmt='toml'),
		)

		####################
		# - INSTALL: Addon Files => /*
		####################
		# Project: Write Extension Python Package
		if path_pypkg is not None:
			cb_update_status('Writing Python Files')
			for file_to_zip in path_pypkg.rglob('*'):
				f_zip.write(
					file_to_zip,
					file_to_zip.relative_to(path_pypkg),
				)

		# Script: Write Script String as __init__.py
		elif path_pysrc is not None:
			cb_update_status('Writing Script as __init__.py')
			with path_pysrc.open('r') as f_pysrc:
				pysrc = f_pysrc.read()

			f_zip.writestr(
				'__init__.py',
				pysrc,
			)
		else:
			msg = 'Tried to pack an extension that is neither a project nor a script. This is most likely a bug in `blext`; consider reporting it.'
			raise ValueError(msg)


## TODO: Consider supporting a faster ZIP packer, ex. external 7-zip or a Rust module.
## - See https://nickb.dev/blog/deflate-yourself-for-faster-rust-zips/
## - Principle is doing everything in RAM, THEN writing out to disk.
## - This mainly only hurts when prepacking - by the way, aren't wheels already deflated?
