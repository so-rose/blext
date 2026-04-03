//####################
//# - enum: Blender Manifest Export Format
//####################
/// Specific version of a Blender manifest.
pub enum ManifestExportFormat {
	Json,
	Toml,
}

//####################
//# - trait: BLManifest
//####################
/// A Blender extension manifest.
pub enum Manifest {
	V1_0_0 {},
}

impl Manifest {
	// TODO: How to combine creation and validation w/convenience of fields?
	// - Do we have a version-specific 'Builder' object?

	//####################
	//# - Constants
	//####################
	pub const fn schema_version(&self) -> semver::Version {
		match self {
			Self::V1_0_0 { .. } => semver::Version::new(1, 0, 0),
		}
	}

	pub const fn filename(&self) -> &'static str {
		match self {
			Self::V1_0_0 {} => "blender_manifest.toml",
		}
	}

	//####################
	//# - Export
	//####################
	pub fn export(&self, fmt: ManifestExportFormat) -> String {
		// TODO: Should we just have the user provide a Writer or something, and avoid the whole
		// String game entirely?
		todo!()
	}

	pub fn export_json(&self) -> String {
		self.export(ManifestExportFormat::Json)
	}
	pub fn export_toml(&self) -> String {
		self.export(ManifestExportFormat::Toml)
	}
}
