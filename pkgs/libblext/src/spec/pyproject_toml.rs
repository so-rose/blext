use super::py_tool_metadata::PyToolMetadata;
use super::ty::BlextSpec;

//####################
//# - struct: Blext Speification in pyproject.toml
//####################
/// Blender extension specification contained in a `pyproject.toml` file.
pub struct PyprojectToml {
	tool_blext_metadata: PyToolMetadata,
}

impl From<PyprojectToml> for BlextSpec {
	fn from(value: PyprojectToml) -> Self {
		todo!()
	}
}
