use crate::uityp::{BLTargetArg, GlobalConfigArgs, LocationArg};
use clap::Parser;

//####################
//# - Arguments
//####################
#[derive(Parser, Debug)]
pub struct ExportArgs {
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
pub fn export(export_args: ExportArgs) {
    println!("{export_args:#?}");
}
