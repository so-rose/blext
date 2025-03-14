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

"""Run the Blender command in various useful ways.

Attributes:
	PATH_BLENDER_PYTHON_SCRIPTS: Python source code to be executed inside of Blender.
		This is shipped with `blext`.

"""

import os
import subprocess
import sys
from pathlib import Path

from frozendict import frozendict

PATH_BLENDER_PYTHON_SCRIPTS: Path = Path(__file__).resolve().parent / 'utils_blender'


####################
# - Blender Runner
####################
_EMPTY_FROZENDICT: frozendict[str, str] = frozendict()


def run_blender(  # noqa: PLR0913
	blender_exe: Path,
	startup_script: Path | None = None,
	factory_startup: bool = True,
	headless: bool = False,
	args: tuple[str, ...] = (),
	env: frozendict[str, str] = _EMPTY_FROZENDICT,
	capture: bool = True,
	block: bool = True,
	bufsize: int = 0,
) -> subprocess.Popen[str] | subprocess.Popen[bytes]:
	"""Run the Blender executable in various ways.

	Notes:
		When `block=True`, `CTRL+C` will also exit the underlying Blender process.
		When `block=False`, `CTRL+C` must be manually handled.

		This function does not register signal handlers.

	Warnings:
		For security reasons, it may be desirable to use a minimal `env`.

		Note, however, that when starting the Blender UI with `headless=False`, there are many important env vars at work.
		For instance, window initialization, audio, and more may all depend on appropriately env vars.

		Therefore, it is strongly advised to pass `os.environ` as-is.
		The security properties of doing so are not generally lesser than simply launching Blender regularly.

	Parameters:
		blender_exe: Path to a valid Blender executable.
		startup_script: Path to a Python script to run as Blender starts.
		factory_startup: Temporarily reset Blender to factory settings.
			In particular, this disables other addons/extensions and/or non-standard preferences.
		headless: Run Blender without a user interface.
		args: Extra CLI arguments to pass to the Blender command invocation.
		env: Environment variables to set.
			**When using
		capture: Whether to capture `stderr` and `stdout` to a string.
			When `False`, Blender's I/O will passthrough completely.
		block: Wait for `blender` to exit before returning from this function.
		bufsize: Passthrough to `subprocess.Popen(..., bufsize=bufsize)`.
			_If you don't know what this is, don't touch it!_
	"""
	blender_command = [
		str(blender_exe),
		*(['--python', str(startup_script)] if startup_script is not None else []),
		*(['--factory-startup'] if factory_startup else []),
		*(['--background'] if headless else []),
		*args,
	]

	if capture:
		bl_process = subprocess.Popen(
			blender_command,
			bufsize=bufsize,
			env=dict(env),
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			text=True,
		)
	else:
		bl_process = subprocess.Popen(
			blender_command,
			bufsize=bufsize,
			env=dict(env),
			stdin=sys.stdin,
			stdout=sys.stdout,
			stderr=sys.stdout,
		)

	if block:
		try:
			_ = bl_process.wait()
		except KeyboardInterrupt:
			bl_process.terminate()

	return bl_process


####################
# - Validate Extension
####################
def validate_extension(blender_exe: Path, *, path_zip: Path) -> None:
	"""Run Blender's builtin validation procedure on a built extension zipfile.

	Parameters:
		blender_exe: Path to a valid Blender executable.
		path_zip: Path to the extension zipfile to check.

	Raises:
		ValueError: If an invalid zipfile path was given, or the extension failed to validate.
	"""
	bl_process = run_blender(
		blender_exe,
		headless=True,
		args=('--command', 'extension', 'validate', str(path_zip)),
		capture=True,
	)
	if bl_process.returncode != 0:
		if bl_process.stdout is not None:
			# Parse Output
			messages = bl_process.stdout.read()
			if isinstance(messages, bytes):
				messages = messages.decode('utf-8')

			# Report Failed Validation
			msgs = [
				'Blender failed to validate the packed extension with the following messages:',
				*[f'> {line}' for line in messages.split('\n')],
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
	"""Run a Blender extension inside of Blender.

	Notes:
		Data is passed to the startup script via env vars:
			- `BLEXT_ZIP_PATH`: Path to the extension zipfile to install and run.

	Parameters:
		blender_exe: Path to a valid Blender executable.
		path_zip: Extension zipfile to check.
		path_blend: Optional `.blend` file to open, after the extension is installed.
		headless: Whether to run Blender without a UI.
		factory_startup: Temporarily reset Blender to factory settings.

	Raises:
		ValueError: If an invalid zipfile path was given, or the extension failed to validate.
	"""
	_ = run_blender(
		blender_exe,
		startup_script=PATH_BLENDER_PYTHON_SCRIPTS / 'bl_init.py',
		factory_startup=factory_startup,
		headless=headless,
		args=(str(path_blend),) if path_blend is not None else (),
		env=frozendict(
			{
				'BLEXT_ZIP_PATH': str(path_zip),
			}
			| os.environ
		),
		capture=False,
	)
