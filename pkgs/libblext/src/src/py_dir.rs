use super::ty::{BlextSrc, BlextSrcError};
use crate::BlextSpec;

#[derive(Debug)]
/// A Blender extension as a Python package (folder), w/`pyproject.toml` metadata.
pub struct PyDir {}

#[async_trait::async_trait]
impl BlextSrc for PyDir {
	async fn parse_blext_spec(
		&self,
	) -> Result<BlextSpec, Box<dyn BlextSrcError>> {
		todo!();
	}
}
