use blext::cli::CLIArgs;
use clap::Parser;

fn main() {
    let args = CLIArgs::parse();
    args.run()
}
