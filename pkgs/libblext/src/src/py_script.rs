use super::ty::{BlextSrc, BlextSrcError};
use crate::BlextSpec;
use alloc::boxed::Box;

#[derive(Debug)]
/// A Blender extension as a single Python script, w/PEP 723 metadata.
pub struct PyScript {}

#[async_trait::async_trait]
impl BlextSrc for PyScript {
	async fn parse_blext_spec(
		&self,
	) -> Result<BlextSpec, Box<dyn BlextSrcError>> {
		todo!();
	}
}
