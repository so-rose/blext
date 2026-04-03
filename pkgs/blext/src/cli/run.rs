use crate::uityp::{BLTargetArg, GlobalConfigArgs, LocationArg};
use clap::Parser;
use std::path::PathBuf;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct RunArgs {
    #[arg(long)]
    blend: Option<PathBuf>,

    #[arg(long, default_value_t = false)]
    headless: bool,

    #[arg(long, default_value_t = true)]
    factory_startup: bool,

    #[command(flatten)]
    location: LocationArg,

    #[command(flatten)]
    bl_target: BLTargetArg,

    #[command(flatten)]
    global_config: GlobalConfigArgs,
}

//####################
//# - Command
//####################
pub fn run(run_args: RunArgs) {
    // TODO: PARSING EXTENSION SPECIFICATION
    // TODO: Get blext_location from arguments.
    // TODO: Parse to get either blext_spec_pyproject, or blext_spec_zip.
    // TODO: Then, from those, get blext_spec (already good validation).

    // TODO: (optional) BUILD EXTENSION
    // TODO: If the extension is not already a zip, then it is first built.
    // TODO: With 'blext build', of course - maybe we can even just create a `BuildArgs` struct and call `build` with that directly. Or something like that.

    // TODO: RUN IN BLENDER
    // TODO: Run in the found Blender!
    println!("{run_args:#?}");
}
