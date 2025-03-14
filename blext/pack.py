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

"""Packing and pre-packing of Blender extension zipfiles from a specification and raw files."""

import shutil
import typing as typ
import zipfile
from pathlib import Path

from . import spec


####################
# - Pack Extension to ZIP
####################
def existing_prepacked_files(
	all_files_to_prepack: dict[Path, Path],
	*,
	path_zip_prepack: Path,
) -> frozenset[Path]:
	"""Determine which files do not need to be pre-packed again, since they already exist in a pre-packed zipfile.

	Parameters:
		all_files_to_prepack: Mapping from host files to files in the zip.
			All files specified here should be available in the final pre-packed zip.
		path_zip_prepack: Path to an existing pre-packed zipfile.
			If no file exists, then all files are assumed to need pre-packing.

	Returns:
		Set of files that need to be pre-packed.

	See Also:
		`blext.pack.prepack_extension`: The output should be passed to this function, to perform the actual pre-packing.
	"""
	if path_zip_prepack.is_file():
		with zipfile.ZipFile(path_zip_prepack, 'r') as f_zip:
			existing_prepacked_files = set({Path(name) for name in f_zip.namelist()})

		# Re-Pack to Delete Files
		## - Deleting a single file from a .zip archive is not always a good idea.
		## - See https://github.com/python/cpython/pull/103033
		## - Instead, when a file should be deleted, we repack the entire `.zip`.
		_files_to_prepack_values = frozenset(all_files_to_prepack.values())
		if any(
			existing_zipfile_path not in _files_to_prepack_values
			for existing_zipfile_path in existing_prepacked_files
		):
			path_zip_prepack.unlink()
			existing_prepacked_files.clear()

		return frozenset(existing_prepacked_files)
	return frozenset()


def prepack_extension(
	files_to_prepack: dict[Path, Path],
	*,
	path_zip_prepack: Path,
	cb_pre_file_write: typ.Callable[[Path, Path], typ.Any] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
	cb_post_file_write: typ.Callable[[Path, Path], typ.Any] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
) -> None:
	"""Pre-pack zipfile containing large files, but not the extension code.

	Notes:
		Writing extension source code to a zipfile is very fast.
		However, when working with ex. wheel dependencies, large files can quickly dominate the build time.

		Therefore, `blext` first generates "pre-packed" zipfile extensions.
		This takes awhile, but is only done once (and/or when a big file changes).
		Then, `blext` copies the pre-packed zip and adds the extension source code.

		Since **changing source code doesn't re-pack large files**, iteration speed is preserved.

	Parameters:
		files_to_prepack: Mapping from host files to files in the zip.
			All files specified here will be packed.
		path_zip_prepack: The zip file to pre-pack.
		cb_pre_file_write: Called before each file is written to the zip.
			Defaults is no-op.
		cb_post_file_write: Called after each file is written to the zip.
			Defaults is no-op.

	Raises:
		ValueError: When not all wheels required by `blext_spec` are found in `path_wheels`.

	See Also:
		- `blext.pack.existing_prepacked_files`: Use to pre-filter `files_to_prepack`,
		in order to only pack files that aren't already present.
	"""
	file_sizes = {path: path.stat().st_size for path in files_to_prepack}

	# Create Zipfile
	with zipfile.ZipFile(path_zip_prepack, 'a', zipfile.ZIP_DEFLATED) as f_zip:
		####################
		# - INSTALL: Files => /wheels/*.whl
		####################
		remaining_files_to_prepack = files_to_prepack.copy()

		for path, zipfile_path in sorted(
			remaining_files_to_prepack.items(), key=lambda el: file_sizes[el[0]]
		):
			cb_pre_file_write(path, zipfile_path)
			f_zip.write(path, zipfile_path)
			cb_post_file_write(path, zipfile_path)


def pack_bl_extension(
	blext_spec: spec.BLExtSpec,
	*,
	overwrite: bool = True,
	path_zip_prepack: Path,
	path_zip: Path,
	path_pysrc: Path,
	cb_update_status: typ.Callable[[str], list[None] | None] = lambda *_: None,  # pyright: ignore[reportUnknownLambdaType]
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
	_ = cb_update_status('Copying Pre-Packed Extension ZIP')
	_ = shutil.copyfile(path_zip_prepack, path_zip)

	with zipfile.ZipFile(path_zip, 'a', zipfile.ZIP_DEFLATED) as f_zip:
		####################
		# - INSTALL: Blender Manifest => /blender_manifest.toml
		####################
		_ = cb_update_status('Writing `blender_manifest.toml`')
		f_zip.writestr(
			blext_spec.manifest_filename,
			blext_spec.export_blender_manifest(fmt='toml'),
		)

		####################
		# - INSTALL: Init Settings => /init_settings.toml
		####################
		if blext_spec.release_profile is not None:
			_ = cb_update_status('Writing Release Profile to `init_settings.toml`')
			f_zip.writestr(
				blext_spec.release_profile.init_settings_filename,
				blext_spec.export_init_settings(fmt='toml'),
			)

		####################
		# - INSTALL: Addon Files => /*
		####################
		# Project: Write Extension Python Package
		if path_pysrc.is_dir():
			_ = cb_update_status('Writing Python Files')
			for file_to_zip in path_pysrc.rglob('*'):
				f_zip.write(
					file_to_zip,
					file_to_zip.relative_to(path_pysrc),
				)

		# Script: Write Script String as __init__.py
		elif path_pysrc.is_file():
			_ = cb_update_status('Writing Extension Script to __init__.py')
			with path_pysrc.open('r') as f_pysrc:
				pysrc = f_pysrc.read()

			f_zip.writestr(
				'__init__.py',
				pysrc,
			)
		else:
			msg = "Tried to pack an extension that is neither a project nor a script. This shouldn't happen."
			raise ValueError(msg)
