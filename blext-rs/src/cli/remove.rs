use crate::uityp::{BLTargetArg, LocationArg, GlobalConfigArgs};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct RemoveArgs {
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
pub fn remove(remove_args: RemoveArgs) {
    println!("{remove_args:#?}");
}
