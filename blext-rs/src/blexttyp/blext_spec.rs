use super::blext_spec_pyproject::BLExtSpecPyProject;
use super::blext_spec_zip::BLExtSpecZip;

//####################
//# - struct: BLExtSpec
//####################
/// BLExtSpec is the central construction of blext.
pub struct BLExtSpec {}

//####################
//# - impl: Parsed pyproject.toml -> BLExtSpec
//####################
impl From<BLExtSpecPyProject> for BLExtSpec {
    fn from(value: BLExtSpecPyProject) -> Self {
        BLExtSpec {}
    }
}

//####################
//# - impl: Parsed extension.zip -> BLExtSpec
//####################
impl From<BLExtSpecZip> for BLExtSpec {
    fn from(value: BLExtSpecZip) -> Self {
        BLExtSpec {}
    }
}
