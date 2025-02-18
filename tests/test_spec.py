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

import blext

EXAMPLES_PATH = Path(__file__).parent.parent / 'examples'


def test_mk_bl_ext_spec():
	spec = blext.BLExtSpec.from_proj_spec(
		EXAMPLES_PATH / 'simple' / 'pyproject.toml',
		release_profile=blext.ReleaseProfile.Release,
	)
