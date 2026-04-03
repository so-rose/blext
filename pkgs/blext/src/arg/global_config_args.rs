use clap::Parser;
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[clap(next_help_heading = "Global Config")]
pub struct GlobalConfigArg {
	// TODO: Instead of Option<>, use default values from https://lib.rs/crates/directories
	#[arg(long, env = "BLEXT_GLOBAL_CACHE_PATH")]
	global_cache_path: Option<PathBuf>,

	// TODO: Instead of Option<>, use default values from https://lib.rs/crates/directories
	#[arg(long, env = "BLEXT_LOCAL_BL_PLATFORM")]
	local_bl_platform: Option<String>,

	// TODO: Instead of Option<>, search using a 'detector'.
	#[arg(long, env = "BLEXT_DEFUALT_BLENDER_EXE")]
	default_blender_exe: Option<PathBuf>,

	// TODO: Instead of Option<>, search using a 'detector'.
	#[arg(long, env = "BLEXT_UV_EXE")]
	uv_exe: Option<PathBuf>,
}
