use crate::py;

//####################
//# - trait: Blender Platform
//####################
/// Computer platform supported by Blender.
///
/// Any Blender platform also represents a particular Python platform.
pub trait Platform: py::Platform {
	fn blender_name(&self) -> &'static str;

	/// Minimum supported version of `glibc` on this platform.
	///
	/// `None` if this platform is not a *nix platform.
	fn min_glibc_version(&self) -> Option<py::GlibcVersion>;

	/// Minimum supported version of `macos` on this platform.
	///
	/// `None` if this platform is not a MacOS platform.
	fn min_macos_version(&self) -> Option<py::MacosVersion>;
	//pub fn blender_archive_filename_ext(&self) -> &'static str;
	// TODO: Where to put this? After all, we need it for a download link.
}
