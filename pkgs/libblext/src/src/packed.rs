use super::ty::{BlextSrc, BlextSrcError};
use crate::BlextSpec;

#[derive(Debug)]
/// A Blender extension bundled into a packed `.zip` archive.
pub struct Packed {}

#[async_trait::async_trait]
impl BlextSrc for Packed {
	async fn parse_blext_spec(
		&self,
	) -> Result<BlextSpec, Box<dyn BlextSrcError>> {
		todo!();
	}
}
