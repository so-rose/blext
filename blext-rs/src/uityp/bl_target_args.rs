use clap::Parser;

#[derive(Parser, Debug)]
#[clap(next_help_heading = "Target")]
pub struct BLTargetArg {
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
