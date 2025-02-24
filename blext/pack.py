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

from . import paths, pydeps, spec


####################
# - Pack Extension to ZIP
####################
def prepack_extension_wheels(
	blext_spec: spec.BLExtSpec,
	*,
	path_zip_prepack: Path | None = None,
	path_wheels: Path | None = None,
	cb_pre_wheel_write: typ.Callable[
		[pydeps.BLExtWheel, Path], list[None] | None
	] = lambda *_: None,
	cb_post_wheel_write: typ.Callable[
		[pydeps.BLExtWheel, Path], list[None] | None
	] = lambda *_: None,
) -> None:
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
		path_uv_lock: Path to `uv.lock` file, used when `vendor=False`.

	Raises:
		ValueError: When not all wheels required by `blext_spec` are found in `path_wheels`.
	"""
	path_zip_prepack = (
		paths.path_prepack(blext_spec) / blext_spec.packed_zip_filename
		if path_zip_prepack is None
		else path_zip_prepack
	)
	path_wheels = paths.path_wheels(blext_spec) if path_wheels is None else path_wheels

	# Validate Wheels to Pack
	found_wheel_filenames = [
		path_wheel.name for path_wheel in path_wheels.rglob('*.whl')
	]
	if not all(
		wheel.filename in found_wheel_filenames
		for wheel in blext_spec.wheels_graph.wheels
	):
		msg = 'While pre-packing the extension, not all required extension wheels were available.'
		raise ValueError(msg)

	# TODO: Also check hashes.

	# Overwrite
	if path_zip_prepack.is_file():
		path_zip_prepack.unlink()

	with zipfile.ZipFile(path_zip_prepack, 'w', zipfile.ZIP_DEFLATED) as f_zip:
		####################
		# - INSTALL: Wheels => /wheels/*.whl
		####################
		for wheel in sorted(
			blext_spec.wheels_graph.wheels, key=lambda wheel: wheel.filename
		):
			path_wheel = path_wheels / wheel.filename
			path_wheel_zip = Path('wheels') / wheel.filename

			cb_pre_wheel_write(wheel, path_wheel)
			f_zip.write(path_wheel, path_wheel_zip)
			cb_post_wheel_write(wheel, path_wheel)


def pack_bl_extension(
	blext_spec: spec.BLExtSpec,
	*,
	force_prepack: bool = False,
	overwrite: bool = True,
	path_zip: Path | None = None,
	path_zip_prepack: Path | None = None,
	path_wheels: Path | None = None,
	path_uv_lock: Path | None = None,
	path_pypkg: Path | None = None,
	path_pysrc: Path | None = None,
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
	path_zip = (
		paths.path_build(blext_spec) / blext_spec.packed_zip_filename
		if path_zip is None
		else path_zip
	)
	path_zip_prepack = (
		paths.path_prepack(blext_spec) / blext_spec.packed_zip_filename
		if path_zip_prepack is None
		else path_zip_prepack
	)
	path_uv_lock = (
		paths.path_uv_lock(blext_spec) if path_uv_lock is None else path_uv_lock
	)

	is_path_py_given = path_pypkg is None and path_pysrc is None
	path_pypkg = paths.path_pypkg(blext_spec) if is_path_py_given else path_pypkg
	path_pysrc = paths.path_pysrc(blext_spec) if is_path_py_given else path_pysrc

	if force_prepack or not path_zip_prepack.is_file():
		prepack_extension_wheels(
			blext_spec,
			path_zip_prepack=path_zip_prepack,
			path_wheels=path_wheels,
		)

	# Overwrite Existing ZIP
	if path_zip.is_file():
		if not overwrite:
			msg = f"File already exists where extension ZIP would be generated  at '{path_zip}'"
			raise ValueError(msg)
		path_zip.unlink()

	# Pack Extension

	## Copy Prepacked ZIP and Finish Packing
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
		# - INSTALL: Lockfile => /uv.lock
		####################
		cb_update_status('Writing `uv.lock`')
		import time

		f_zip.write(
			path_uv_lock,
			'uv.lock',
		)

		####################
		# - INSTALL: Addon Files => /*
		####################
		path_pypkg = path_pypkg
		path_pysrc = path_pysrc

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
			msg = 'Tried to pack an extension that is neither a project nor a script. Please report this bug.'
			raise RuntimeError(msg)


## TODO: Consider supporting a faster ZIP packer, ex. external 7-zip or a Rust module.
## - See https://nickb.dev/blog/deflate-yourself-for-faster-rust-zips/
## - Principle is doing everything in RAM, THEN writing out to disk.
## - This mainly only hurts when prepacking - by the way, aren't wheels already deflated?
