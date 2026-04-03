use crate::uityp::{BLTargetArg, GlobalConfigArgs, LocationArg};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct CheckArgs {
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
pub fn check(check_args: CheckArgs) {
    // TODO: PARSING EXTENSION SPECIFICATION
    // TODO: Get blext_location from arguments.
    // TODO: Parse to get either blext_spec_pyproject, or blext_spec_zip.
    // TODO: Then, from those, get blext_spec (already good validation).

    // TODO: (optional) BUILD EXTENSION
    // TODO: If the extension is not already a zip, then it is first built.
    // TODO: With 'blext build', of course - maybe we can even just create a `BuildArgs` struct and call `build` with that directly. Or something like that.

    // TODO: RUN CHECKERS
    // TODO: How to make pluggable checkers? This is the cleanest / most flexible way.
    // TODO: Must support: blender --command extension validate
    // TODO: Must support: Headless pytest with raw bpy module.
    // TODO: Must support: ruff validation.
    // TODO: Must support: ty validation (type check).
    // TODO: Should support: A pack of validators that checks against Blender extension platform policies.

    // TODO: INFORM USER OF RESULTS
    // TODO: Determine missing wheels.
    println!("{check_args:#?}");
}
