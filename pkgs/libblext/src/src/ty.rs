use crate::BlextSpec;
use alloc::boxed::Box;

#[async_trait::async_trait]
/// Source code for a Blender extension.
pub trait BlextSrc: Sync + core::fmt::Debug {
	/// Parse a Blender extension specification from the source code.
	async fn parse_blext_spec(
		&self,
	) -> Result<BlextSpec, Box<dyn BlextSrcError>>;
}

/// Error encountered while handling the source code of a Blender extension.
pub trait BlextSrcError: core::fmt::Debug + core::error::Error + Send {}
impl core::error::Error for Box<dyn BlextSrcError> {}
