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

"""Implements `blext check`."""

import sys
from pathlib import Path

import pydantic as pyd

import blext.exceptions as exc
from blext import blender, finders

from ._context import (
	APP,
	CONSOLE,
	DEFAULT_BLEXT_INFO,
	DEFAULT_CONFIG,
	ParameterBLExtInfo,
	ParameterConfig,
)


@APP.command()
def check(
	*,
	blext_info: ParameterBLExtInfo = DEFAULT_BLEXT_INFO,
	config: ParameterConfig = DEFAULT_CONFIG,
) -> None:
	"""Check an extension project for problems.

	Parameters:
		path: Path to an extension project, or an already-built `.zip`.
		platform: Blender platform(s) to constrain validation.
			Use "detect" to constrain to detect the current platform.
	"""
	check_target_name = str(blext_info.proj_uri)

	with exc.handle(exc.pretty, ValueError):
		blender_exe = finders.find_blender_exe(
			override_path_blender_exe=config.path_blender_exe
		)

	checks: dict[str, bool] = {}

	####################
	# - Check ZIP
	####################
	if isinstance(blext_info.proj_uri, Path) and blext_info.proj_uri.name.endswith(
		'.zip'
	):
		check_target_name = blext_info.proj_uri.name
		path_zip = blext_info.proj_uri

		####################
		# - Check: Validate w/Blender
		####################
		checks['blender --command extension validate'] = True
		try:
			blender.validate_extension(blender_exe, path_zip=path_zip)
		except ValueError:
			checks['$ blender --command extension validate'] = False

	####################
	# - Check Project
	####################
	else:
		####################
		# - Check: Load and Validate Specification
		####################
		checks['Find Extension Specification'] = True
		try:
			blext_location = blext_info.blext_location(config)
			check_target_name = blext_location.path_spec
		except ValueError:
			checks['Find Extension Specification'] = False

		checks['Load Extension Specification'] = True
		checks['Validate Extension Specification'] = True
		try:
			blext_spec = blext_info.blext_spec(config)
			check_target_name = blext_spec.id

		except (ValueError, pyd.ValidationError) as ex:
			if isinstance(ex, pyd.ValidationError):
				checks['Validate Extension Specification'] = False
			else:
				checks['Load Extension Specification'] = False

	####################
	# - Report
	####################
	if all(checks.values()):
		all_pass_str = r'\[[green]✓[/green]]'
	elif not any(checks.values()):
		all_pass_str = r'\[[red]X[/red]]'
	else:
		all_pass_str = r'\[[yellow]-[/yellow]]'

	checks_passed = len(
		[check_status for check_status in checks.values() if check_status]
	)
	checks_passed_str = f'{checks_passed}/{len(checks)}'

	CONSOLE.print()
	CONSOLE.print(
		all_pass_str + f' [bold]{check_target_name}[/bold] ({checks_passed_str})'
	)
	for check_text, check_status in checks.items():
		CONSOLE.print(
			'   ',
			r'\[[green]✓[/green]]' if check_status else r'\[[red]X[/red]]',
			' ',
			check_text,
			sep='',
		)

	####################
	# - Exit Code
	####################
	if not all(checks.values()):
		sys.exit(1)
