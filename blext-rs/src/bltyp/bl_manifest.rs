// Includes enum BLManifestVersion
// Includes trait BLManifest
// Includes struct BLManifest1_0_0
// For now, also includes validators.

//####################
//# - enum: BLManifestVersion
//####################
pub enum BLManifestVersion {
    V1_0_0,
}

pub enum BLManifestFormat {
    Json,
    Toml,
}

//####################
//# - trait: BLManifest
//####################
pub trait BLManifest {
    fn schema_version(&self) -> BLManifestVersion;
    fn manifest_filename(&self) -> &'static str;
    fn export(&self, fmt: BLManifestFormat) -> String;
}

//####################
//# - struct: BLManifest1_0_0
//####################
pub struct BLManifest1_0_0 {}
impl BLManifest for BLManifest1_0_0 {
    fn schema_version(&self) -> BLManifestVersion {
        BLManifestVersion::V1_0_0
    }

    fn manifest_filename(&self) -> &'static str {
        "blender_manifest.toml"
    }

    fn export(&self, fmt: BLManifestFormat) -> String {
        String::from("TBD")
    }
}
