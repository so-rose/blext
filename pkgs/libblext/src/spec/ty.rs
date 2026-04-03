use crate::{bl, py};

use super::field;

const DEFAULT_LICENSE: &str = "GPL-3.0-or-later";

//####################
//# - trait: Blender Extension Specification
//####################
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
/// Complete specification of a Blender extension.
pub struct BlextSpec {
	//####################
	//# - Project Info
	//####################
	/// Globally unique identifier of this extension.
	id: field::BlextId,

	/// Display name of this extension.
	display_name: field::BlextId,

	/// Tagline for this extension.
	tagline: field::BlextTagline,

	/// Version of this extension.
	version: semver::Version,

	/// License of this extension.
	//license: spdx::LicenseId,
	// TODO[upstream]: PR to `spdx` crate that implements `core::hash::Hash` on `LicenseId`.
	// TODO[upstream]: Also, PR to `spdx` crate for a `name` method on `LicenseId`...
	license: compact_str::CompactString,

	/// Copyright of this extension.
	copyright: Option<field::BlextCopyright>,

	/// Maintainer of this extension.
	maintainer: Option<field::BlextMaintainer>,

	/// Website of this extension project.
	website: Option<url::Url>,

	//####################
	//# - Compatibility Info
	//####################
	/// Permission keys requested by this extension.
	permissions: alloc::collections::BTreeSet<field::BlextPermission>,

	/// Tags of this extension, for publication>
	tags: alloc::collections::BTreeSet<field::BlextTag>,
	// /// Python dependencies of this extension.
	//fn pydeps(&self) -> &PyDeps;
	// TODO: How to model Python dependencies?
}

impl BlextSpec {
	/// All Blender versions / platforms supported by this extension.
	pub fn bl_support_matrix(&self) -> &bl::SupportMatrix {
		todo!()
	}

	/// Take out an [`bl::SupportMatrix`] by dissolving `self`.
	///
	/// Variant of [`Self::bl_support_matrix`].
	pub fn take_bl_support_matrix(self) -> bl::SupportMatrix {
		todo!()
	}

	// All Blender versions supported by this extension.
	pub fn bl_versions(&self) -> &semver::Version {
		// TODO: Do we use a trait object for BLVersion? Or what's best?
		todo!()
	}

	//####################
	//# - Coherency
	//####################
	/// Split this [`BlextSpec`] into several [`CoherentBlextSpec`]s,
	/// which unlike [`BlextSpec`], are guaranteed to build to a single `.zip`.
	pub fn coherent_iter(&self) -> impl Iterator<Item = CoherentBlextSpec> {
		// TODO: Should we:
		// - Take an argument here? Feels superfluous / smelly.
		// - Have a "target_bl_matrix: Option<...>" on the struct? No, too magic.
		// - Filter after? Too much work for the pydeps resolved. Unless it's lazy.
		todo!()
	}
}

impl Default for BlextSpec {
	fn default() -> Self {
		Self {
			id: Default::default(),
			display_name: Default::default(),
			tagline: Default::default(),
			version: semver::Version::new(0, 0, 1),
			license: DEFAULT_LICENSE.into(),
			//license: spdx::license_id(DEFAULT_LICENSE).expect(
			//	constcat::concat!(
			//		"hard-coded SPDX license, '",
			//		DEFAULT_LICENSE,
			//		"', was not found in this binary's SPDX database",
			//	),
			//),
			copyright: None,
			maintainer: None,
			website: None,
			permissions: Default::default(),
			tags: Default::default(),
		}
	}
}

/// Specification of a Blender specification for exactly one "coherent" set of Blender versions / platforms.
///
/// # Coherency
/// A "coherent" extension specification can be built into a single `.zip` file.
///
/// Extensions that *don't* use pydeps generally have this property.
/// However, the moment pydeps come into play, this is not at all obvious:
/// - Does the extension require any of Blender's bundled pydeps?
/// - How many times did Blender alter its pydeps over the extension's
///   supported versions?
/// - Does the extension have a platform-specific dependency graph?
/// - Does the extension's platform-specific dependency graph change across
///   Blender versions due to Blender altering its bundled pydep versions?
///
/// Luckily, all extension specs may be split into a finite number of "coherent"
/// extension specs.
/// Each of the coherent specs can then be built into one zip file, such that all
/// supported Blender versions and platforms are covered by one of the built zips.
///
/// Examples:
/// - BL 4.2-4.5, no deps: Safe to build one zip.
/// - BL 4.2-4.5, independent win-specific dep: Since the dep doesn't care about
///   Blender's bundled dep versions, just build one for win and one for mac/linux.
/// - BL 4.2-4.5, bundled dep after 4.4: A dep was bundled into
///   Blender after 4.4. Thus, build least two zips: One for 4.2-4.3, another for
///   4.4-4.5. Possibly more, if behavior depends on bundled pydeps.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct CoherentBlextSpec<'a> {
	incoherent_blext_spec: &'a BlextSpec,
	// TODO: We need a reference to the coherent bl_support_matrix.
	// TODO: We need a reference to the coherent subgraph of pydeps.
	// TODO: We need a reference to the coherent subset of bl_versions.
}

impl<'a> CoherentBlextSpec<'a> {
	/// All Blender versions / platforms supported by this coherent extension.
	pub fn bl_support_matrix(&self) -> &bl::SupportMatrix {
		todo!()
	}

	// TODO: Reproduce manifest generator.
	pub fn manifest(&self) -> bl::Manifest {
		// TODO: A few things:
		// - Each Blender version supports one or more manifest versions.
		// - Any CoherentBlextSpec MUST have at least one common manifest version
		//   supported by the Blender versions.
		todo!()
	}

	//pub fn wheels(&self) -> hashbrown::HashSet<py::Wheel> {
	pub fn wheels(&self) -> hashbrown::HashSet<&String> {
		todo!()
	}
}
