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

"""Implements strictly validated Blender manifest schemas.

Attributes:
	_RE_MANIFEST_SEMVER: Lifted directly from the [source code of Blender `4.2.0`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L102).
"""

import typing as typ

import annotated_types as atyp
import pydantic as pyd

from blext.utils.pydantic_frozendict import FrozenDict

from . import validators
from .spdx_license import SPDXLicense


####################
# - Manifest Protocol
####################
class BLManifest(typ.Protocol):
	"""Protocol defining behavior that all Blender manifests must exhibit."""

	@property
	def schema_version(self) -> str:
		"""SemVer version of the Blender manifest schema."""
		...

	@property
	def manifest_filename(self) -> str:
		"""Name of the manifest file to write."""
		...


####################
# - Manifest 1.0.0
####################
class BLManifest_1_0_0(pyd.BaseModel, frozen=True):  # noqa: N801
	"""Strict representation of the `1.0.0` version of the Blender extension manifest.

	Notes:
		The validation routines performed on these fields should **flawlessly** match that done by `blender --command extension validate`, for Blender version `4.2.0`.

		The validation of this class is derived from the following `4.2.0` source-code permalinks (presuming `struct=True`):
		- **Source of Validation Information**: [`addons_core.bl_pkg.cli.blender_ext`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1781).
		- `id`: Matches validation in [`pkg_idname_is_valid_or_error`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1358).
		- `schema_version`: Matches validation in [`pkg_manifest_validate_field_any_version`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1533).
		- `name`: Matches validation in [`pkg_manifest_validate_field_any_non_empty_string_stripped_no_control_chars`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1498).
		- `tagline`: Matches validation in [`pkg_manifest_validate_field_tagline`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1581).
		- `version`: Matches validation in [`pkg_manifest_validate_field_any_version`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1533).
		- `type`: Very simple; either `add-on` or `theme`.
		- `maintainer`: Matches validation in [`pkg_manifest_validate_field_any_non_empty_string_stripped_no_control_chars`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1498).
		- `license`: The official specification requires SPDX, therefore `blext.extyp.SPDXLicense` is preferred to Blender's `pkg_manifest_validate_field_any_non_empty_list_of_non_empty_strings`.
		- `blender_version_min`: Matches validation in [`pkg_manifest_validate_field_any_version_primitive`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1543). Manifest specification additionally requires that the minimum Blender version is greater than `4.2`.
		- `blender_version_max`: Matches validation in [`pkg_manifest_validate_field_any_version_primitive_or_empty`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1555), which simply calls `pkg_manifest_validate_field_any_version_primitive` after `None`-check.
		- `blender_version_max`: The official specification requires SPDX, therefore `blext.extyp.SPDXLicense` is preferred to Blender's `pkg_manifest_validate_field_any_non_empty_list_of_non_empty_strings`.
		- `website`: Matches validation in [`pkg_manifest_validate_field_any_non_empty_string_stripped_no_control_chars`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1498).
		- `copyright`: Matches validation in [`pkg_manifest_validate_field_copyright`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1591).
		- `permissions`: Matches validation in [`pkg_manifest_validate_field_permissions`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1618). The values use `pkg_manifest_validate_terse_description_or_error`, like `tagline`.
		- `tags`: Matches validation in [`pkg_manifest_validate_field_any_list_of_non_empty_strings`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1513). On the manifest level, there is no valid tag set defined; instead, this is defined by `BLVersion`, and therefore the validation cannot be simply expressed in the first (only in a dedicated `pydantic` validator).
		- `platforms`: Manifest specification defines a very specific list of valid strings.
		- `wheels`: Matches validation in [`pkg_manifest_validate_field_wheels`](https://projects.blender.org/blender/blender/src/commit/a51f293548adba0dda086f5771401e8d8ab66227/scripts/addons_core/bl_pkg/cli/blender_ext.py#L1715).

		_Why `4.2.0`? This was the first version to support the `1.0.0` manifest schema._

	Warnings:
		`blext` enforces strict adherance to the `1.0.0` manifest specification and/or `4.2.0` behavior to support **ecosystem integrity**: An extension with a manifest that parses correctly in one version of Blender, must parse correctly in all future versions of Blender that support this same schema.
		**No exceptions**.

		Thus, any `blext` deviation in manifest parsing from the `4.2.0` behavior of `blender --command extension validate`, or from the original manifest `1.0.0` specification, should be considered (**and reported**) as a bug in `blext`.
		_If they conflict, prefer the original manifest `1.0.0` specification._

		Conversely, unless the **original** manifest `1.0.0` specification explicitly states otherwise, all Blender versions that support manifest `1.0.0` must do so with **identical semantics / edge cases** to `4.2.0`.
		_If a Blender version's `1.0.0` manifest parsing differs from the specification, or from `4.2.0`'s behavior, then this is a bug in that version of Blender, which should be reported upstream ASAP._


	Attributes:
		id: The short name of the extension.

	"""

	manifest_filename: typ.Literal['blender_manifest.toml'] = pyd.Field(
		default='blender_manifest.toml', exclude=True
	)

	####################
	# - Required Fields
	####################
	schema_version: typ.Annotated[
		str,
		atyp.Predicate(validators.is_valid_bl_semver),
	] = '1.0.0'

	type: typ.Literal['add-on', 'theme'] = 'add-on'
	id: typ.Annotated[
		str,
		atyp.Predicate(str.isidentifier),
		atyp.Predicate(validators.no_dunder_in_string),
		atyp.Predicate(validators.no_str_startswith_underscore),
		atyp.Predicate(validators.no_str_endswith_underscore),
	]
	name: typ.Annotated[
		str,
		atyp.Predicate(validators.is_str_strip_not_empty),
		atyp.Predicate(validators.is_str_strip_a_noop),
		atyp.Predicate(validators.str_has_no_bl_control_chars),
	]
	tagline: typ.Annotated[
		str,
		atyp.MaxLen(64),
		atyp.Predicate(str.isidentifier),
		atyp.Predicate(validators.no_dunder_in_string),
		atyp.Predicate(validators.no_str_startswith_underscore),
		atyp.Predicate(validators.no_str_endswith_underscore),
		atyp.Predicate(validators.last_char_is_alphanum_or_closes_bracket),
	]
	version: typ.Annotated[
		str,
		atyp.Predicate(validators.is_valid_bl_semver),
	]
	blender_version_min: typ.Annotated[
		str,
		atyp.Predicate(validators.all_version_numbers_are_digits),
		atyp.Predicate(validators.blender_version_is_gt_4_2),
	]

	####################
	# - Optional Fields
	####################
	blender_version_max: (
		typ.Annotated[
			str,
			atyp.Predicate(validators.all_version_numbers_are_digits),
			atyp.Predicate(validators.blender_version_is_gt_4_2),
		]
		| None
	) = None
	platforms: (
		tuple[
			typ.Literal[
				'windows-x64', 'windows-arm64', 'macos-x64', 'macos-arm64', 'linux-x64'
			],
			...,
		]
		| None
	) = None
	permissions: (
		FrozenDict[
			typ.Literal['files', 'network', 'clipboard', 'camera', 'microphone'],
			typ.Annotated[
				str,
				atyp.MaxLen(64),
				atyp.Predicate(str.isidentifier),
				atyp.Predicate(validators.no_dunder_in_string),
				atyp.Predicate(validators.no_str_startswith_underscore),
				atyp.Predicate(validators.no_str_endswith_underscore),
				atyp.Predicate(validators.last_char_is_alphanum_or_closes_bracket),
			],
		]
		| None
	) = None
	copyright: (
		tuple[
			typ.Annotated[
				str,
				atyp.Predicate(validators.is_copyright_year_valid),
				atyp.Predicate(validators.is_copyright_name_valid),
			],
			...,
		]
		| None
	) = None
	maintainer: (
		typ.Annotated[
			str,
			atyp.Predicate(validators.is_str_strip_not_empty),
			atyp.Predicate(validators.is_str_strip_a_noop),
			atyp.Predicate(validators.str_has_no_bl_control_chars),
		]
		| None
	) = None
	tags: tuple[str, ...] | None = None
	wheels: (
		tuple[
			typ.Annotated[
				str,
				atyp.Predicate(validators.wheel_filename_has_no_double_quotes),
				atyp.Predicate(validators.wheel_filename_has_no_backward_slashes),
				atyp.Predicate(validators.is_str_strip_not_empty),
				atyp.Predicate(validators.is_str_strip_not_empty),
				atyp.Predicate(validators.is_str_strip_a_noop),
				atyp.Predicate(validators.str_has_no_bl_control_chars),
				atyp.Predicate(validators.lowercase_wheel_filename_endswith_whl),
				atyp.Predicate(validators.wheel_filename_has_valid_number_of_dashes),
			],
			...,
		]
		| None
	) = None
	website: (
		typ.Annotated[
			str,
			atyp.Predicate(validators.is_str_strip_not_empty),
			atyp.Predicate(validators.is_str_strip_a_noop),
			atyp.Predicate(validators.str_has_no_bl_control_chars),
		]
		| None
	) = None

	license: tuple[SPDXLicense, ...] | None = None
