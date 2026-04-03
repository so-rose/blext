use crate::uityp::{BLTargetArg, LocationArg, GlobalConfigArgs};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct InitArgs {
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
pub fn init(init_args: InitArgs) {
    println!("{init_args:#?}");
}
