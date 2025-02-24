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

import typing as typ
from pathlib import Path

import hypothesis as hyp
from hypothesis import strategies as st

import blext
from blext import finders


####################
# - Tests: Parse Examples
####################
def test_find_uv() -> None:
	_ = finders.find_uv_exe()


def test_find_blender_exe() -> None:
	_ = finders.find_blender_exe()
