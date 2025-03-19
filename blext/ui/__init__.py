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

"""UI elements for `blext`'s CLI interface."""

from .blext_info import LOCATION_GROUP, SPECIFICATION_GROUP, BLExtInfo
from .download_wheels import CallbacksDownloadWheel, ui_download_wheels
from .global_config import APPAUTHOR, APPNAME, GlobalConfig
from .prepack_extension import CallbacksPrepackExtension, ui_prepack_extension

__all__ = [
	'APPAUTHOR',
	'APPNAME',
	'LOCATION_GROUP',
	'SPECIFICATION_GROUP',
	'BLExtInfo',
	'CallbacksDownloadWheel',
	'CallbacksPrepackExtension',
	'GlobalConfig',
	'ui_download_wheels',
	'ui_prepack_extension',
]
