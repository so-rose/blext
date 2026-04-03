use crate::uityp::{BLTargetArg, LocationArg, GlobalConfigArgs};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct CacheArgs {
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
pub fn cache(cache_args: CacheArgs) {
    println!("{cache_args:#?}");
}
