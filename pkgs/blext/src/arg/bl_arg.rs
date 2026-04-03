use libblext as blext;

#[derive(clap::Parser, Debug)]
#[clap(next_help_heading = "Target")]
/// Argument used to target a particular release of Blender.
pub struct BlArg {
	#[arg(short, long)]
	bl_version: Option<String>,
	// TODO: Different ways of specifying a Blender version.
	#[arg(short, long)]
	platform: Option<String>,
	// TODO: Different ways of specifying a Blender platform.
	#[arg(long)]
	profile: Option<String>,
	// TODO: Different ways of specifying a release profile.
}

impl BlArg {
	pub async fn bl_support_matrix(&self) -> blext::bl::SupportMatrix {
		todo!()
	}
}

//####################
//# - Errors
//####################
#[derive(Debug, thiserror::Error)]
pub enum BlArgError {}

impl BlArgError {
	pub fn exitcode(&self) -> exitcode::ExitCode {
		todo!()
	}
}
