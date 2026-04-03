use crate::arg;

//####################
//# - Arguments
//####################
#[derive(clap::Parser, Debug)]
pub struct AddArgs {
	#[command(flatten)]
	location: arg::SrcArg,

	#[command(flatten)]
	bl_target: arg::BlArg,

	#[command(flatten)]
	global_config: arg::GlobalConfigArg,
}

//####################
//# - Command
//####################
pub async fn add(add_args: AddArgs) -> Result<(), AddError> {
	println!("{add_args:#?}");

	Ok(())
}

//####################
//# - Errors
//####################
#[derive(Debug, thiserror::Error)]
pub enum AddError {
	#[error(transparent)]
	SrcTarget(#[from] arg::SrcArgError),

	#[error(transparent)]
	BlTarget(#[from] arg::BlArg),
}

impl AddError {
	pub fn exitcode(&self) -> exitcode::ExitCode {
		match self {
			AddError::SrcTarget(err) => err.exitcode(),
			AddError::BlTarget(err) => err.exitcode(),
		}
	}
}
