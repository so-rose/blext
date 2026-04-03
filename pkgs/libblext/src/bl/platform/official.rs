use super::ty::Platform;
use crate::py;

//####################
//# - enum: Officially-Supported Blender Platform
//####################
/// A single Blender-supported OS and architecture.
pub enum PlatformOfficial {
	LinuxX64(py::GlibcVersion),
	LinuxArm64(py::GlibcVersion),
	MacosX64(py::MacosVersion),
	MacosArm64(py::MacosVersion),
	WindowsX64,
	WindowsArm64,
}

//impl {
//	/// The file extension of the official archive downloaded from download.blender.org.
//	pub fn blender_archive_filename_ext(&self) -> &'static str {
//		match &self {
//			Self::LinuxX64(_) => "tar.xz",
//			Self::LinuxArm64(_) => "tar.xz", // Doesn't exist (yet)
//			Self::MacosX64(_) => "dmg",
//			Self::MacosArm64(_) => "dmg",
//			Self::WindowsX64 => "zip",
//			Self::WindowsArm64 => "zip",
//		}
//	}
//}
impl py::Platform for PlatformOfficial {}

impl Platform for PlatformOfficial {
	//####################
	//# - Official Attributes
	//####################
	/// Official platform name understood by Blender.
	fn blender_name(&self) -> &'static str {
		match self {
			Self::LinuxX64(_) => "linux-x64",
			Self::LinuxArm64(_) => "linux-arm64",
			Self::MacosX64(_) => "macos-x64",
			Self::MacosArm64(_) => "macos-arm64",
			Self::WindowsX64 => "windows-x64",
			Self::WindowsArm64 => "windows-arm64",
		}
	}

	fn min_glibc_version(&self) -> Option<py::GlibcVersion> {
		match self {
			Self::LinuxX64(version) => Some(*version),
			Self::LinuxArm64(version) => Some(*version),
			_ => None,
		}
	}

	fn min_macos_version(&self) -> Option<py::MacosVersion> {
		match self {
			Self::MacosX64(version) => Some(*version),
			Self::MacosArm64(version) => Some(*version),
			_ => None,
		}
	}
}
