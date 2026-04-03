//####################
//# - struct: Blender Version/Platform Support Matrix
//####################
#[derive(Debug, Clone)]
/// Matrix of specific Blender versions and platforms (OS and CPU architecture).
pub struct SupportMatrix;

impl SupportMatrix {
	pub fn intersection(&self, rhs: &Self) -> Self {
		todo!()
	}
	pub fn subseteq(&self, rhs: &Self) -> bool {
		todo!()
	}

	/// Detect a support matrix from the current program environment.
	///
	/// This process should be considered best-effort, as it searches for:
	/// - The current platform aka. operating system, CPU architecture, etc. .
	/// - All installed versions of Blender.
	pub fn detect_from_environment() -> Result<Self, SupportMatrixError> {
		todo!()
	}
}

impl core::ops::Sub for &SupportMatrix {
	type Output = Option<SupportMatrix>;

	fn sub(self, rhs: Self) -> Self::Output {
		todo!()
	}
}

//####################
//# - Errors
//####################
#[derive(Debug, thiserror::Error)]
pub enum SupportMatrixError {}
