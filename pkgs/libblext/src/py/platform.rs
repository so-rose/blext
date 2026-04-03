//####################
//# - structs: OS Versions
//####################
/// Version of `glibc` on *nix platforms.
#[derive(Debug, Clone, Copy)]
pub struct GlibcVersion(usize, usize, usize);

/// Version of `macos` on MacOS platforms
#[derive(Debug, Clone, Copy)]
pub struct MacosVersion(usize, usize);

//####################
//# - trait: Python Platform
//####################
/// Particular Python platform.
pub trait Platform {
	//####################
	//# - Python: PyPi Attributes
	//####################
	//TODO

	//####################
	//# - Python: PyPA Attributes
	//####################
	//TODO: Includes ex. platform tag prefix, pymarker strings, etc. .

	// fn valid_python_wheel_tags(&self) -> HashSet<String>;
	// // TODO: Use a proper type instead of String.
	// fn valid_abi_wheel_tags(&self) -> HashSet<String>;
	// // TODO: Use a proper type instead of String.

	// // TODO: We need a way to get a unique 'extras' tag ex. 'bl4-2' for each BLVersion.
	// //
	// fn pymarker_implementation_name(&self) -> &'static str;
	// fn pymarker_platform_python_implementation(&self) -> &'static str;
	// // TODO: Do we have to give this so explicitly? Can't it be derived?

	// fn vendored_pydeps(&self) -> HashSet<String>;
	// // TODO: Use a PyDep type to describe what the Blender version ships with
}
