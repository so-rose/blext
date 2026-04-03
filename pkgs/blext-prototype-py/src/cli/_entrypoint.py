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

import importlib.metadata
import os
import subprocess
import sys
from pathlib import Path

import rich

from blext.utils import pretty_exceptions
from blext.utils.search_in_parents import search_in_parents


def entrypoint():
	####################
	# - Install Exception Hook
	####################
	sys.excepthook = pretty_exceptions.exception_hook

	####################
	# - Proxy Global -> Project-Local
	####################
	path_pyproject_toml = search_in_parents(Path().resolve(), 'pyproject.toml')
	if path_pyproject_toml is not None:
		# Find currently available 'blext' executable.
		## This feels more robust than other methods.
		blext_files = importlib.metadata.files('blext')
		if blext_files is None:
			msgs = [
				'Could not locate a `uv` executable path on the filesystem.',
				'> This can happen if `blext` was installed in an unsupported manner, such that the files of its dependencies are not plain filesystem paths (user error).',
			]
			raise ValueError(*msgs)

		current_blext_exe = Path(
			next(
				iter(
					package_path
					for package_path in blext_files
					if package_path.name == 'blext'
					and package_path.parent.name == 'bin'
				)
			).locate()
		).resolve()

		# Check if current 'blext' executable is a subdirectory of the project's `.venv`.
		## If so, then the project-local 'blext' is in use, and no proxying should occur.
		## If not, we should check whether `blext` is available, and if so, proxy to it.
		project_local_blext_path = (
			path_pyproject_toml.parent / '.venv' / 'bin' / 'blext'
		)
		if (
			current_blext_exe != project_local_blext_path
			and project_local_blext_path.is_file()
		):
			rich.print('Using [bold]project-local[/bold] [italic]blext[/italic]')
			rich.print()

			blext_proxy_process = subprocess.Popen(
				[
					str(project_local_blext_path),
					*sys.argv[1:],
				],
				bufsize=0,
				env=os.environ,
				stdin=sys.stdin,
				stdout=sys.stdout,
				stderr=sys.stderr,
				text=True,
			)

			try:
				return_code = blext_proxy_process.wait()
			except KeyboardInterrupt:
				blext_proxy_process.terminate()
				sys.exit(1)

			sys.exit(return_code)

	####################
	# - Alias: blext blender
	####################
	if len(sys.argv) > 1 and sys.argv[1] == 'blender':
		from blext.uityp.global_config import PATH_GLOBAL_CONFIG, GlobalConfig

		global_config = GlobalConfig.from_config(
			PATH_GLOBAL_CONFIG,
			environ=dict(os.environ),
		)

		bl_process = subprocess.Popen(
			[str(global_config.path_default_blender_exe), *sys.argv[2:]],
			env=os.environ,
			stdin=sys.stdin,
			stdout=sys.stdout,
			stderr=sys.stderr,
			text=True,
		)

		try:
			return_code = bl_process.wait()
		except KeyboardInterrupt:
			bl_process.terminate()
			sys.exit(1)

		sys.exit(return_code)

	####################
	# - Alias: blext uv
	####################
	if len(sys.argv) > 1 and sys.argv[1] == 'uv':
		from blext.uityp.global_config import PATH_GLOBAL_CONFIG, GlobalConfig

		global_config = GlobalConfig.from_config(
			PATH_GLOBAL_CONFIG,
			environ=dict(os.environ),
		)

		uv_process = subprocess.Popen(
			[str(global_config.path_uv_exe), *sys.argv[2:]],
			env=os.environ,
			stdin=sys.stdin,
			stdout=sys.stdout,
			stderr=sys.stderr,
			text=True,
		)

		try:
			return_code = uv_process.wait()
		except KeyboardInterrupt:
			uv_process.terminate()
			sys.exit(1)

		sys.exit(return_code)

	####################
	# - Run CLI
	####################
	from . import (  # noqa: F401
		blender,  # pyright: ignore[reportUnusedImport]
		build,  # pyright: ignore[reportUnusedImport]
		check,  # pyright: ignore[reportUnusedImport]
		run,  # pyright: ignore[reportUnusedImport]
		show_blender_manifest,  # pyright: ignore[reportUnusedImport]
		show_deps,  # pyright: ignore[reportUnusedImport]
		show_global_config,  # pyright: ignore[reportUnusedImport]
		show_path_blender,  # pyright: ignore[reportUnusedImport]
		show_path_global_config,  # pyright: ignore[reportUnusedImport]
		show_path_uv,  # pyright: ignore[reportUnusedImport]
		show_profile,  # pyright: ignore[reportUnusedImport]
		uv,  # pyright: ignore[reportUnusedImport]
	)
	from ._context import APP

	APP()
