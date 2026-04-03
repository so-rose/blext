use crate::{BlextSpec, src};

#[async_trait::async_trait]
/// Stateful object used to build a `blext` extension from source.
pub trait BlextBuilder {
	/// Specification of the Blender extension to build.
	fn blext_spec(&self) -> &BlextSpec;

	/// Build extension to one or more specified `zip` files.
	async fn build_zip_files(
		self,
	) -> Result<src::Packed, Box<dyn BlextBuilderError>>;
}

/// Error encountered while handling the source code of a Blender extension.
pub trait BlextBuilderError:
	core::fmt::Debug + core::error::Error + Send
{
}
impl core::error::Error for Box<dyn BlextBuilderError> {}
