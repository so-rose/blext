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

from pathlib import Path

PATH_ROOT = Path(__file__).resolve().parent.parent

EXAMPLES_PROJ_FILES_VALID = [
	PATH_ROOT / 'examples' / 'simple' / 'pyproject.toml',
	PATH_ROOT / 'examples' / 'extension_file.py',
]

EXAMPLES_PROJ_FILES_INVALID = [
	PATH_ROOT,
	PATH_ROOT / 'examples' / 'simple',
	PATH_ROOT / 'examples' / 'simpl',
	PATH_ROOT / 'examples' / 'simple' / 'pyproject.json',
	PATH_ROOT / 'examples' / 'simple' / 'uv.lock',
	PATH_ROOT / 'extension_file.py.lock',
]
