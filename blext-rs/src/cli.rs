use clap::Parser;

mod add;
mod build;
mod cache;
mod check;
mod clean;
mod export;
mod info;
mod init;
mod inspect;
mod publish;
mod remove;
mod run;

//####################
//# - Define Style
//####################
// Mirror Cargo's color style
// - See https://stackoverflow.com/a/79614957

use clap::builder::styling::{AnsiColor, Effects, Style, Styles};
const HEADER: Style = AnsiColor::Green.on_default().effects(Effects::BOLD);
const USAGE: Style = AnsiColor::Green.on_default().effects(Effects::BOLD);
const LITERAL: Style = AnsiColor::Cyan.on_default().effects(Effects::BOLD);
const PLACEHOLDER: Style = AnsiColor::Cyan.on_default();
const ERROR: Style = AnsiColor::Red.on_default().effects(Effects::BOLD);
const VALID: Style = AnsiColor::Cyan.on_default().effects(Effects::BOLD);
const INVALID: Style = AnsiColor::Yellow.on_default().effects(Effects::BOLD);

/// Cargo's color style
/// [source](https://github.com/crate-ci/clap-cargo/blob/master/src/style.rs)
const CARGO_STYLING: Styles = Styles::styled()
    .header(HEADER)
    .usage(USAGE)
    .literal(LITERAL)
    .placeholder(PLACEHOLDER)
    .error(ERROR)
    .valid(VALID)
    .invalid(INVALID);

//####################
//# - CLI Arguments
//####################
#[derive(Parser, Debug)]
#[command(version)]
#[clap(styles = CARGO_STYLING)]
pub enum CLIArgs {
    //####################
    //# - Global
    //####################
    /// Initialize a new blext project.
    #[clap(name = "init")]
    Init(init::InitArgs),

    /// Manage the global blext cache.
    #[clap(name = "cache")]
    Cache(cache::CacheArgs),

    //####################
    //# - Project Information
    //####################
    /// Show an informative overview of a blext project.
    #[clap(name = "info")]
    Info(info::InfoArgs),

    /// Export blext project information.
    #[clap(name = "inspect")]
    Inspect(inspect::InspectArgs), // deps, platforms, bl_versions, etc. .

    /// Export blext project information.
    #[clap(name = "export")]
    Export(export::ExportArgs), // blender_manifest, init_settings, ci, etc. .

    //####################
    //# - Project Build
    //####################
    /// Build a blext project to a Blender extension.
    #[clap(name = "build")]
    Build(build::BuildArgs),

    /// Check the validity of a blext project.
    #[clap(name = "check")]
    Check(check::CheckArgs),

    /// Run a blext project in Blender.
    #[clap(name = "run")]
    Run(run::RunArgs),

    /// Cleanup after a blext project.
    #[clap(name = "clean")]
    Clean(clean::CleanArgs),

    //####################
    //# - Project Dependencies
    //####################
    /// Add a Python dependency to a blext project.
    #[clap(name = "add")]
    Add(add::AddArgs),

    /// Remove a Python dependency from a blext project.
    #[clap(name = "remove")]
    Remove(remove::RemoveArgs),

    //####################
    //# - Distribution
    //####################
    /// Publish a blext project to an extension repository.
    #[clap(name = "publish")]
    Publish(publish::PublishArgs),
}

//####################
//# - CLI Runner
//####################
impl CLIArgs {
    pub fn run(self) {
        match self {
            //####################
            //# - Global
            //####################
            CLIArgs::Init(init_args) => {
                init::init(init_args);
            }
            CLIArgs::Cache(cache_args) => {
                cache::cache(cache_args);
            }

            //####################
            //# - Project Information
            //####################
            CLIArgs::Info(info_args) => {
                info::info(info_args);
            }
            CLIArgs::Inspect(inspect_args) => {
                inspect::inspect(inspect_args);
            }
            CLIArgs::Export(export_args) => {
                export::export(export_args);
            }

            //####################
            //# - Project Build
            //####################
            CLIArgs::Build(build_args) => {
                build::build(build_args);
            }
            CLIArgs::Check(check_args) => {
                check::check(check_args);
            }
            CLIArgs::Run(run_args) => {
                run::run(run_args);
            }
            CLIArgs::Clean(clean_args) => {
                clean::clean(clean_args);
            }

            //####################
            //# - Project Dependencies
            //####################
            CLIArgs::Add(add_args) => {
                add::add(add_args);
            }
            CLIArgs::Remove(remove_args) => {
                remove::remove(remove_args);
            }

            //####################
            //# - Distribution
            //####################
            CLIArgs::Publish(publish_args) => {
                publish::publish(publish_args);
            }
        }
    }
}
