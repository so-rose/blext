use crate::uityp::{BLTargetArg, LocationArg, GlobalConfigArgs};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct AddArgs {
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
pub fn add(add_args: AddArgs) {
    println!("{add_args:#?}");
}
