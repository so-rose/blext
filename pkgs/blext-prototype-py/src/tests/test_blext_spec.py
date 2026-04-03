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

"""Tests `blext.blext_spec`."""

##import json
##import tomllib
##import typing as typ
##from pathlib import Path
##
##import hypothesis as hyp
##import pytest
##from frozendict import frozendict
##from hypothesis import strategies as st
##
##from blext import extyp, pydeps
##from blext.blext_spec import REGEX, BLExtSpec
##
##from ._context import (
##	EXAMPLES_PROJ_FILES_INVALID,
##	EXAMPLES_PROJ_FILES_VALID,
##	SEMVER_REGEX,
##	get_pattern,
##	powerset,
##)
##
##ST_BLEXT_SPEC = st.builds(
##	BLExtSpec,
##	granular_bl_platforms=st.frozensets(
##		st.sampled_from(extyp.BLPlatform),
##		min_size=1,
##	),
##	deps=st.just(pydeps.BLExtDeps()),
##	release_profile=st.just(None),
##	version=st.from_regex(SEMVER_REGEX),
##	# permissions=st.fixed_dictionaries(
##	# {},
##	# optional={
##	# perm: st.from_regex(REGEX['permissions.get'])
##	# for perm in ['files', 'network', 'clipboard', 'camera', 'microphone']
##	# },
##	# ),
##	# copyright=st.from_regex(REGEX['copyright']),
##	# maintainer=st.from_regex(REGEX['maintainer']),
##	## tags works out of the box
##	## website works out of the box
##)


####################
# - Tests: Parse Examples
####################
##@hyp.given(
##	st.sampled_from(EXAMPLES_PROJ_FILES_INVALID),
##	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
##)
##def test_fail_to_create_blext_spec_from_invalid_path(
##	proj_file_path: Path, release_profile_id: blext.BLPlatform
##) -> None:
##	with pytest.raises(ValueError):
##		_ = BLExtSpec.from_proj_spec_path(
##			proj_file_path,
##			release_profile_id=release_profile_id,
##		)
##
##
##@hyp.given(
##	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
##	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
##)
##def test_create_blext_spec_from_proj_file_path(
##	proj_file_path: Path, release_profile_id: blext.BLPlatform
##) -> None:
##	blext_spec = BLExtSpec.from_proj_spec_path(
##		proj_file_path,
##		release_profile_id=release_profile_id,
##	)
##	assert isinstance(blext_spec, BLExtSpec)
##
##
##@hyp.given(
##	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
##	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
##)
##def test_packed_wheel_paths(
##	proj_file_path: Path, release_profile_id: blext.BLPlatform
##) -> None:
##	blext_spec = BLExtSpec.from_proj_spec_path(
##		proj_file_path,
##		release_profile_id=release_profile_id,
##	)
##	_ = blext_spec.manifest_wheels
##
##
##@hyp.settings(max_examples=10)
##@hyp.given(
##	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
##	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
##)
##def test_export_blender_manifest_to_json(
##	proj_file_path: Path, release_profile_id: blext.BLPlatform
##) -> None:
##	blext_spec = BLExtSpec.from_proj_spec_path(
##		proj_file_path,
##		release_profile_id=release_profile_id,
##	)
##
##	blender_manifest_str = blext_spec.export_blender_manifest(fmt='json')
##	blender_manifest = json.loads(blender_manifest_str)
##
##	assert 'schema_version' in blender_manifest
##	if blender_manifest['schema_version'] == '1.0.0':
##		assert 'id' in blender_manifest
##		assert 'name' in blender_manifest
##		assert 'version' in blender_manifest
##		assert 'tagline' in blender_manifest
##		assert 'maintainer' in blender_manifest
##		assert 'type' in blender_manifest
##		assert 'blender_version_min' in blender_manifest
##		assert 'blender_version_max' in blender_manifest
##		assert 'platforms' in blender_manifest
##		assert 'wheels' in blender_manifest
##		assert 'permissions' in blender_manifest
##		assert 'tags' in blender_manifest
##		assert 'license' in blender_manifest
##		assert 'copyright' in blender_manifest
##	else:
##		assert False
##
##
##@hyp.settings(max_examples=10)
##@hyp.given(
##	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
##	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
##)
##def test_export_blender_manifest_to_toml(
##	proj_file_path: Path, release_profile_id: blext.BLPlatform
##) -> None:
##	blext_spec = BLExtSpec.from_proj_spec_path(
##		proj_file_path,
##		release_profile_id=release_profile_id,
##	)
##
##	blender_manifest_str = blext_spec.export_blender_manifest(fmt='toml')
##	blender_manifest = tomllib.loads(blender_manifest_str)
##
##	assert 'schema_version' in blender_manifest
##	if blender_manifest['schema_version'] == '1.0.0':
##		assert 'id' in blender_manifest
##		assert 'name' in blender_manifest
##		assert 'version' in blender_manifest
##		assert 'tagline' in blender_manifest
##		assert 'maintainer' in blender_manifest
##		assert 'type' in blender_manifest
##		assert 'blender_version_min' in blender_manifest
##		assert 'blender_version_max' in blender_manifest
##		assert 'platforms' in blender_manifest
##		assert 'wheels' in blender_manifest
##		assert 'permissions' in blender_manifest
##		assert 'tags' in blender_manifest
##		assert 'license' in blender_manifest
##		assert 'copyright' in blender_manifest
##	else:
##		assert False
##
##
##@hyp.given(
##	st.sampled_from(EXAMPLES_PROJ_FILES_VALID),
##	st.sampled_from(typ.get_args(blext.StandardReleaseProfile)),
##	st.sampled_from(['json', 'toml']),
##)
##def test_export_init_settings(
##	proj_file_path: Path,
##	release_profile_id: blext.StandardReleaseProfile,
##	fmt: typ.Literal['json', 'toml'],
##) -> None:
##	blext_spec = BLExtSpec.from_proj_spec_path(
##		proj_file_path,
##		release_profile_id=release_profile_id,
##	)
##
##	blext_spec.export_init_settings(fmt=fmt)
##
##
######################
### - Test BLExtSpec
######################
##@hyp.settings(max_examples=10)
##@hyp.given(
##	ST_BLEXT_SPEC,
##)
##def test_universality(
##	blext_spec: BLExtSpec,
##) -> None:
##	assert blext_spec.is_universal == (
##		frozenset(blext.BLPlatform) == blext_spec.bl_platforms
##	)
##
##
##@hyp.settings(max_examples=10)
##@hyp.given(
##	ST_BLEXT_SPEC,
##)
##def test_packed_platforms(
##	blext_spec: BLExtSpec,
##) -> None:
##	assert all(
##		bl_platform in blext.BLPlatform for bl_platform in blext_spec.manifest_platforms
##	)
##
##
### @hyp.given(
### ST_BLEXT_SPEC,
### )
### def test_packed_wheel_paths(
### blext_spec: spec.BLExtSpec,
### ) -> None:
### _ = blext_spec.packed_wheel_paths
##
##
##@hyp.settings(max_examples=10)
##@hyp.given(
##	ST_BLEXT_SPEC,
##)
##def test_packed_zip_filename(
##	blext_spec: BLExtSpec,
##) -> None:
##	if not blext_spec.is_universal and len(blext_spec.bl_platforms) > 1:
##		with pytest.raises(ValueError):
##			_ = blext_spec.zip_filename
##	else:
##		assert blext_spec.zip_filename.endswith('.zip')
##
##
##@hyp.settings(max_examples=10)
##@hyp.given(
##	ST_BLEXT_SPEC,
##)
##def test_export_init_settings_to_json(blext_spec: BLExtSpec) -> None:
##	init_settings_str = blext_spec.export_init_settings(fmt='json')
##	init_settings = json.loads(init_settings_str)
##
##	assert 'schema_version' in init_settings
##	if init_settings['schema_version'] == '0.1.0':
##		assert 'use_log_file' in init_settings
##		assert 'log_file_name' in init_settings
##		assert 'log_file_level' in init_settings
##		assert 'use_log_console' in init_settings
##		assert 'log_console_level' in init_settings
##	else:
##		assert False


##@hyp.settings(max_examples=10)
##@hyp.given(
##	ST_BLEXT_SPEC,
##)
##def test_export_init_settings_to_toml(blext_spec: BLExtSpec) -> None:
##	bl_manifest_strs = blext_spec.bl_manifest_strs(extyp.BLManifestVersion.V1_0_0)
