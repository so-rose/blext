use crate::py::{GlibcVersion, MacosVersion};

//####################
//# - structs: Blender Extension Types
//####################
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
/// Unique identifier for a Blender extension.
pub struct BlextId(compact_str::CompactString);

impl From<&str> for BlextId {
	fn from(value: &str) -> Self {
		Self(value.into())
	}
}

impl Default for BlextId {
	fn default() -> Self {
		"default-blext-extension".into()
	}
}

/// Display name of a Blender extension.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BlextDisplayName(compact_str::CompactString);

impl From<&str> for BlextDisplayName {
	fn from(value: &str) -> Self {
		Self(value.into())
	}
}

impl Default for BlextDisplayName {
	fn default() -> Self {
		"Default blext Extension".into()
	}
}

/// Tagline describing a Blender extension.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BlextTagline(compact_str::CompactString);

impl From<&str> for BlextTagline {
	fn from(value: &str) -> Self {
		Self(value.into())
	}
}

impl Default for BlextTagline {
	fn default() -> Self {
		"A default description for a blext based Blender extension".into()
	}
}

/// Copyright assigned to a Blender extension.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BlextCopyright(compact_str::CompactString);

/// Maintainer responsible for a Blender extension.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BlextMaintainer {
	name: compact_str::CompactString,
	email: email_address::EmailAddress,
}

/// Permissions requested by a Blender extension.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BlextPermission {
	permission_string: compact_str::CompactString,
}
// TODO: The new() function should take a Blender manifest version, which should be used to check that the given permission string is valid for that manifest version.

/// Permissions requested by a Blender extension.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct BlextTag {
	tag_string: compact_str::CompactString,
}
// TODO: The new() function should take a Blender manifest version, which should be used to check that the given permission string is valid for that manifest version.

/// Python dependencies.
pub struct BlextPyDeps {
	//requested: py::Deps,
	//all_deps: py::Deps,
	min_glibc_version: Option<GlibcVersion>,
	min_macos_version: Option<MacosVersion>,
	//valid_
	//valid_python_tags: frozenset[str] | None = None
	//valid_abi_tags: frozenset[str] | None = None
}
