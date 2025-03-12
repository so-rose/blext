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

"""Execute the command-line interface of `blext."""

import os
import subprocess
import sys

from blext import finders

if __name__ == '__main__':
	from blext.cli import APP

	####################
	# - Alias: blext blender
	####################
	if len(sys.argv) > 1 and sys.argv[1] == 'blender':
		# TODO: Find via GlobalConfig
		blender_exe = finders.find_blender_exe()

		bl_process = subprocess.Popen(
			[blender_exe, *sys.argv[2:]],
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
		# TODO: Find via GlobalConfig
		uv_exe = finders.find_uv_exe()

		uv_process = subprocess.Popen(
			[uv_exe, *sys.argv[2:]],
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

	APP()
