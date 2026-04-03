mod add;
mod build;
//mod cache;
//mod check;
//mod clean;
//mod export;
//mod info;
//mod init;
//mod inspect;
//mod publish;
//mod remove;
//mod run;

use crate::style::STYLES;

//####################
//# - CLI Arguments
//####################
#[derive(clap::Parser, Debug)]
#[command(version)]
#[clap(styles = STYLES)]
pub enum Cli {
	//####################
	//# - Global
	//####################
	// /// Initialize a new blext project.
	// #[clap(name = "init")]
	// Init(init::InitArgs),

	// /// Manage the global blext cache.
	// #[clap(name = "cache")]
	// Cache(cache::CacheArgs),

	//####################
	//# - Project Information
	//####################
	// /// Show an informative overview of a blext project.
	// #[clap(name = "info")]
	// Info(info::InfoArgs),

	// /// Export blext project information.
	// #[clap(name = "inspect")]
	// Inspect(inspect::InspectArgs), // deps, platforms, bl_versions, etc. .

	// /// Export blext project information.
	// #[clap(name = "export")]
	// Export(export::ExportArgs), // blender_manifest, init_settings, ci, etc. .

	//####################
	//# - Project Build
	//####################
	/// Build a blext project to a Blender extension.
	#[clap(name = "build")]
	Build(build::BuildArgs),

	// /// Check the validity of a blext project.
	// #[clap(name = "check")]
	// Check(check::CheckArgs),

	// /// Run a blext project in Blender.
	// #[clap(name = "run")]
	// Run(run::RunArgs),

	// /// Cleanup after a blext project.
	// #[clap(name = "clean")]
	// Clean(clean::CleanArgs),

	//####################
	//# - Project Dependencies
	//####################
	/// Add a Python dependency to a blext project.
	#[clap(name = "add")]
	Add(add::AddArgs),
	// /// Remove a Python dependency from a blext project.
	// #[clap(name = "remove")]
	// Remove(remove::RemoveArgs),

	//####################
	//# - Distribution
	//####################
	// /// Publish a blext project to an extension repository.
	// #[clap(name = "publish")]
	// Publish(publish::PublishArgs),
}

//####################
//# - CLI Runner
//####################
impl Cli {
	pub async fn entrypoint(self) -> Result<(), CliError> {
		match self {
			// Cli::Init(init_args) => {
			// 	tracing::debug!(
			// 		"selected the `init` command w/args:\n{init_args:#?}"
			// 	);
			// 	init::init(init_args).await?;
			// }
			// Cli::Cache(cache_args) => {
			// 	tracing::debug!(
			// 		"selected the `cache` command w/args:\n{cache_args:#?}"
			// 	);
			// 	cache::cache(cache_args).await?;
			// }

			// //####################
			// //# - Project Information
			// //####################
			// Cli::Info(info_args) => {
			// 	tracing::debug!(
			// 		"selected the `info` command w/args:\n{info_args:#?}"
			// 	);
			// 	info::info(info_args).await?;
			// }
			// Cli::Inspect(inspect_args) => {
			// 	tracing::debug!(
			// 		"selected the `inspect` command w/args:\n{inspect_args:#?}"
			// 	);
			// 	inspect::inspect(inspect_args).await?;
			// }
			// Cli::Export(export_args) => {
			// 	tracing::debug!(
			// 		"selected the `export` command w/args:\n{export_args:#?}"
			// 	);
			// 	export::export(export_args).await?;
			// }

			// //####################
			// //# - Project Build
			// //####################
			Cli::Build(build_args) => {
				tracing::debug!(
					"selected the `build` command w/args:\n{build_args:#?}"
				);
				build::build(build_args).await?;
			}
			// Cli::Check(check_args) => {
			// 	tracing::debug!(
			// 		"selected the `check` command w/args:\n{check_args:#?}"
			// 	);
			// 	check::check(check_args).await?;
			// }
			// Cli::Run(run_args) => {
			// 	tracing::debug!(
			// 		"selected the `run` command w/args:\n{run_args:#?}"
			// 	);
			// 	run::run(run_args).await?;
			// }
			// Cli::Clean(clean_args) => {
			// 	tracing::debug!(
			// 		"selected the `clean` command w/args:\n{clean_args:#?}"
			// 	);
			// 	clean::clean(clean_args).await?;
			// }

			//####################
			//# - Project Dependencies
			//####################
			Cli::Add(add_args) => {
				tracing::debug!(
					"selected the `add` command w/args:\n{add_args:#?}"
				);
				add::add(add_args).await?;
			} // Cli::Remove(remove_args) => {
			  // 	tracing::debug!(
			  // 		"selected the `remove` command w/args:\n{remove_args:#?}"
			  // 	);
			  // 	remove::remove(remove_args).await?;
			  // }

			  // //####################
			  // //# - Distribution
			  // //####################
			  // Cli::Publish(publish_args) => {
			  // 	tracing::debug!(
			  // 		"selected the `publish` command w/args:\n{publish_args:#?}"
			  // 	);
			  // 	publish::publish(publish_args).await?;
			  // }
		}
		Ok(())
	}
}

//####################
//# - Errors
//####################
#[derive(Debug, thiserror::Error)]
pub enum CliError {
	// #[error(transparent)]
	// Init(#[from] init::InitError),

	// #[error(transparent)]
	// Cache(#[from] cache::CacheError),

	//####################
	//# - Project Information
	//####################
	// #[error(transparent)]
	// Info(#[from] info::InfoError),

	// #[error(transparent)]
	// Inspect(#[from] inspect::InspectError),

	// #[error(transparent)]
	// Export(#[from] export::ExportError),

	//####################
	//# - Project Build
	//####################
	// #[error(transparent)]
	// Build(#[from] build::BuildError),

	// #[error(transparent)]
	// Check(#[from] check::CheckError),

	// #[error(transparent)]
	// Run(#[from] run::RunError),

	// #[error(transparent)]
	// Watch(#[from] watch::WatchError),

	// #[error(transparent)]
	// Clean(#[from] clean::CleanError),

	//####################
	//# - Project Dependencies
	//####################
	#[error(transparent)]
	Add(#[from] add::AddError),
	// #[error(transparent)]
	// Remove(#[from] remove::RemoveError),

	//####################
	//# - Distribution
	//####################
	// #[error(transparent)]
	// Publish(#[from] publish::PublishError),
}
impl CliError {
	pub fn exitcode(&self) -> exitcode::ExitCode {
		match self {
			// Self::Init(err) => err.exitcode(),
			// Self::Cache(err) => err.exitcode(),
			// Self::Info(err) => err.exitcode(),
			// Self::Inspect(err) => err.exitcode(),
			// Self::Export(err) => err.exitcode(),
			// Self::Build(err) => err.exitcode(),
			// Self::Check(err) => err.exitcode(),
			// Self::Run(err) => err.exitcode(),
			// Self::Watch(err) => err.exitcode(),
			// Self::Clean(err) => err.exitcode(),
			Self::Add(err) => err.exitcode(),
			// Self::Remove(err) => err.exitcode(),
			// Self::Publish(err) => err.exitcode(),
		}
	}
}
