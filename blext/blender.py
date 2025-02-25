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

import os
import subprocess
import sys
from pathlib import Path

from frozendict import frozendict

PATH_BLENDER_PYTHON_SCRIPTS: Path = Path(__file__).resolve().parent / 'blender_python'


####################
# - Env Variable Getter
####################
def forward_env(*env_vars: str) -> dict[str, str]:
	return {
		env_var: os.environ[env_var] for env_var in env_vars if env_var in os.environ
	}


####################
# - Blender Runner
####################
def run_blender(
	blender_exe: Path,
	startup_script: Path | None = None,
	factory_startup: bool = True,
	headless: bool = False,
	args: tuple[str, ...] = (),
	env: frozendict[str, str] = frozendict(),
	capture: bool = True,
	block: bool = True,
) -> subprocess.Popen:
	"""Run the Blender executable in various ways.

	Parameters:
		factory_startup: Start a totally "clean" Blender, without any addons / preferences.
	"""
	blender_command = [
		str(blender_exe),
		*(['--python', str(startup_script)] if startup_script is not None else []),
		*(['--factory-startup'] if factory_startup else []),
		*(['--background'] if headless else []),
		*args,
	]
	bl_process = subprocess.Popen(
		blender_command,
		bufsize=0,  ## TODO: Check if -1 is OK
		env=dict(env),
		**(
			{
				'stdout': subprocess.PIPE,
				'stderr': subprocess.STDOUT,
				'text': True,
			}
			if capture
			else {
				'stdin': sys.stdin,
				'stdout': sys.stdout,
				'stderr': sys.stdout,
			}
		),
	)
	if block:
		try:
			bl_process.wait()
		except KeyboardInterrupt:
			bl_process.terminate()
	return bl_process


####################
# - Validate Extension
####################
def validate_extension(blender_exe: Path, *, path_zip: Path) -> None:
	process = run_blender(
		blender_exe,
		headless=True,
		args=('--command', 'extension', 'validate', str(path_zip)),
		capture=True,
	)
	if process.returncode != 0:
		if process.stdout is not None:
			msgs = [
				'Blender failed to validate the packed extension with the following messages:',
				*[f'> {line}' for line in process.stdout.read().split('\n')],
			]
			raise ValueError(*msgs)
		msgs = [
			'Blender failed to validate the packed extension.',
		]
		raise ValueError(*msgs)


####################
# - Run Extension
####################
def run_extension(
	blender_exe: Path,
	*,
	path_zip: Path,
	path_blend: Path | None = None,
	headless: bool = False,
	factory_startup: bool = True,
) -> None:
	"""Run an extension inside of Blender.

	Warnings:
	"""
	bl_process = run_blender(
		blender_exe,
		startup_script=PATH_BLENDER_PYTHON_SCRIPTS / 'bl_init.py',
		factory_startup=factory_startup,
		headless=headless,
		args=(str(path_blend),) if path_blend is not None else (),
		env=frozendict(
			{
				'BLEXT_ADDON_NAME': 'blext_dev',
				'BLEXT_ZIP_PATH': path_zip,
			}
			| os.environ
		),
		capture=False,
	)

	## TODO: CTRL+C really should quit Blender as well.
