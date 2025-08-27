use crate::uityp::{BLTargetArg, LocationArg, GlobalConfigArgs};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct InfoArgs {
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
pub fn info(info_args: InfoArgs) {
    println!("{info_args:#?}");
}
