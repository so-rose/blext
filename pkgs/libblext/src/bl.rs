mod manifest;
mod platform;
mod support_matrix;
mod version;

pub use manifest::{Manifest, ManifestExportFormat};
pub use platform::{Platform, PlatformOfficial};
pub use support_matrix::{SupportMatrix, SupportMatrixError};
pub use version::Version;
