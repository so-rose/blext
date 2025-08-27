use crate::uityp::{BLTargetArg, GlobalConfigArgs, LocationArg};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct BuildArgs {
    /// Overwrite any existing '.zip' file.
    #[arg(long, default_value_t = true)]
    overwrite: bool,

    /// Include wheel dependencies in the '.zip'.
    #[arg(long, default_value_t = true)]
    vendor: bool,

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
pub fn build(build_args: BuildArgs) {
    // TODO: PARSING EXTENSION SPECIFICATION
    // TODO: Get blext_location from arguments.
    // TODO: Parse to get either blext_spec_pyproject, or blext_spec_zip.
    // TODO: Then, from those, get blext_spec.

    // TODO: INFORMING USER OF SELECTIONS
    // TODO: Inform the user which (and how) Blender versions were selected, including any deviations (ex. larger min supported MacOS), but in simple terms overall.
    // TODO: Inform the user which (and how) Blender platforms were selected, in simple terms overall.
    // TODO: Inform the user how many extension zips will be built.

    // TODO: DOWNLOAD AND PACK FILES
    // TODO: Determine missing wheels.
    // TODO: Download missing wheels.
    // TODO: Pre-pack one extension zip per platform.
    // TODO: Pack one extension zip per platform (from pre-pack).

    // TODO: DOWNLOAD AND PACK FILES
    // TODO: Inform the user what was built, and to where.
    // TODO: Perform queued (lazy) cache management.
    println!("{build_args:#?}");
}
