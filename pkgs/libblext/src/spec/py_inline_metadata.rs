use super::py_tool_metadata::PyToolMetadata;
use super::ty::BlextSpec;

//####################
//# - struct: Blext Speification in pyproject.toml
//####################
/// Blender extension specification contained in a `pyproject.toml` file.
pub struct PyInlineMetadata {
	tool_blext_metadata: PyToolMetadata,
}

impl From<PyInlineMetadata> for BlextSpec {
	fn from(value: PyInlineMetadata) -> Self {
		todo!()
	}
}
