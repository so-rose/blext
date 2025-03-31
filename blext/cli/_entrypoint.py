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

import os
import subprocess
import sys

from blext import uityp
from blext.utils import pretty_exceptions


def entrypoint():
	from . import APP

	####################
	# - Alias: blext blender
	####################
	if len(sys.argv) > 1 and sys.argv[1] == 'blender':
		global_config = uityp.GlobalConfig.from_local(
			environ=dict(os.environ),
		)

		bl_process = subprocess.Popen(
			[str(global_config.path_blender_exe), *sys.argv[2:]],
			bufsize=0,
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
		global_config = uityp.GlobalConfig.from_local(
			environ=dict(os.environ),
		)

		uv_process = subprocess.Popen(
			[str(global_config.path_uv_exe), *sys.argv[2:]],
			bufsize=0,
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

	# TODO: Override global exception handling here.
	## - Instead of all the exception handler 'with' statements.

	####################
	# - Install Exception Hook
	####################
	sys.excepthook = pretty_exceptions.exception_hook

	####################
	# - Run CLI
	####################
	APP()
