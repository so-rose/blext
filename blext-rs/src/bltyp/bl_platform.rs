// Also includes BLPlatformSet

/// Identifies a particular operating system / architecture pair supported by Blender.
pub struct GlibcVersion(usize, usize, usize);
pub struct MacosVersion(usize, usize);

//####################
//# - enum: BLPlatform
//####################
/// A single Blender-supported OS and architecture.
pub enum BLPlatform {
    LinuxX64(GlibcVersion),
    LinuxArm64(GlibcVersion),
    MacosX64(MacosVersion),
    MacosArm64(MacosVersion),
    WindowsX64,
    WindowsArm64,
}

impl BLPlatform {
    //####################
    //# - Official Attributes
    //####################
    /// Official platform name understood by Blender.
    pub fn blender_name(&self) -> &'static str {
        match &self {
            BLPlatform::LinuxX64(_) => "linux-x64",
            BLPlatform::LinuxArm64(_) => "linux-arm64",
            BLPlatform::MacosX64(_) => "macos-x64",
            BLPlatform::MacosArm64(_) => "macos-arm64",
            BLPlatform::WindowsX64 => "windows-x64",
            BLPlatform::WindowsArm64 => "windows-arm64",
        }
    }

    /// The file extension of the official archive downloaded from download.blender.org.
    pub fn blender_archive_filename_ext(&self) -> &'static str {
        match &self {
            BLPlatform::LinuxX64(_) => "tar.xz",
            BLPlatform::LinuxArm64(_) => "tar.xz", // Doesn't exist (yet)
            BLPlatform::MacosX64(_) => "dmg",
            BLPlatform::MacosArm64(_) => "dmg",
            BLPlatform::WindowsX64 => "zip",
            BLPlatform::WindowsArm64 => "zip",
        }
    }

    //####################
    //# - Python: PyPi Attributes
    //####################
    //TODO

    //####################
    //# - Python: PyPA Attributes
    //####################
    //TODO: Includes ex. platform tag prefix, pymarker strings, etc. .
}

//####################
//# - struct: BLPlatformSet
//####################
/// A set of BLPlatforms.
pub struct BLPlatformSet {}
