use crate::uityp::{BLTargetArg, GlobalConfigArgs, LocationArg};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct PublishArgs {
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
pub fn publish(publish_args: PublishArgs) {
    // TODO: PARSING EXTENSION SPECIFICATION
    // TODO: Get blext_location from arguments.
    // TODO: Parse to get either blext_spec_pyproject, or blext_spec_zip.
    // TODO: Then, from those, get blext_spec (already good validation).

    // TODO: (optional) BUILD EXTENSION
    // TODO: If the extension is not already a zip, then it is first built.
    // TODO: With 'blext build', of course - maybe we can even just create a `BuildArgs` struct and call `build` with that directly. Or something like that.
	
    // TODO: RUN CHECKS
	// TODO: Perhaps we can hardcode (in a TOML?) which checks that must pass when uploading to a particular platform.

    // TODO: UPLOAD
    // TODO: As I understand it, it's a simple matter.
    println!("{publish_args:#?}");
}
