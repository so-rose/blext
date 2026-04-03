use crate::arg::{self, BlArg, GlobalConfigArg, SrcArg};
use libblext as blext;
use libblext::BlextBuilder;

//####################
//# - Arguments
//####################
#[derive(clap::Parser, Debug)]
pub struct BuildArgs {
	#[command(flatten)]
	src: SrcArg,

	#[command(flatten)]
	bl: BlArg,

	#[arg(long, default_value_t = true)]
	/// Output path for the extension `.zip`.
	output: bool,

	#[arg(long, default_value_t = true)]
	/// Whether to overwrite any pre-existing extension `.zip`.
	overwrite: bool,

	#[arg(long, default_value_t = true)]
	/// Include wheel dependencies in the '.zip'.
	vendor_pydeps: bool,

	#[command(flatten)]
	global_config: GlobalConfigArg,
}

impl BuildArgs {
	/// Parse the extension specification and Blender support matrix from the given arguments.
	pub async fn parse(
		self: std::sync::Arc<Self>,
	) -> Result<
		(
			Box<dyn blext::BlextSrc>,
			blext::BlextSpec,
			blext::bl::SupportMatrix,
		),
		BuildError,
	> {
		// Parse Blender extension specification from source code.
		let _self = self.clone();
		let blext_spec_handle = tokio::spawn(async move {
			// Parse and normalize location of the extension source code.
			//
			// NOTE: "Normalization" could involve ex. downloading a script at a URL, or cloning a git repo.
			let blext_src = _self.src.blext_src().await;

			match blext_src {
				// Attempt to parse the specification from successful parse / normalization.
				Ok(blext_src) => blext_src
					.parse_blext_spec()
					.await
					.map_err(BuildError::ParseSpecFromSource),

				// Propagate the error from parsing / normalization.
				Err(err) => Err(BuildError::from(err)),
			}
		});

		// Parse requested support matrix of Blender versions / platforms.
		//
		// NOTE: The user rarely wants the extension built for *all* the Blender versions/platforms that
		// a given extension supports. This allows the user to specify what they'd actually like built!
		let _self = self.clone();
		let bl_support_matrix_handle = tokio::spawn(async move {
			_self.bl.bl_support_matrix().await.map_err(BuildError::from)
		});
		// TODO: The 'detect' logic is going to need to be able to "cut down" the requested support matrix based on what the extension supports.

		// Join concurrent tasks and return results.
		let (blext_spec_result, bl_support_matrix_result) =
			tokio::try_join!(blext_spec_handle, bl_support_matrix_handle)?;
		Ok((blext_spec_result?, bl_support_matrix_result?))
	}
}

//####################
//# - Command
//####################
pub async fn build(build_args: BuildArgs) -> Result<(), BuildError> {
	let build_args = std::sync::Arc::new(build_args);
	tracing::debug!(?build_args);

	// Parse the specification of the Blender extension, from the extension source code.
	let (blext_src, blext_spec, bl_support_matrix) = build_args.parse().await?;
	tracing::debug!(
		?blext_spec,
		?bl_support_matrix,
		"successfully parsed spec, BL support matrix"
	);

	// TODO: Do we actually need to do all this work?
	// - If the spec is parsed from the source, then I can't think of a single good reason to
	//   force the BuilderBuilder to accept source AND spec. Instead, it sould auto-generate the
	//   spec from the source at the start.
	// - What if the user wants to change something? Well, as I recall, that's what "release
	//   profiles" are for - why bend over backwards to support "monkey patching" after the spec
	//   already exists?
	// - Now, it is true that informing the user of all the things requires us to have a blext_spec
	//   ready to go. But couldn't we have the src produce a &BlextSpec via method?
	// - What if we made the builder object keep a field with a &'a BlextSpec, such that <'a> is the
	//   lifetime of the BlextSrc object? After all, it wouldn't make much sense to build an
	//   extension when we've lost track of the source code. But then, what about all the things
	//   that have to happen in threaded contexts? Is it so wrong to have the builder clone out the
	//   spec?
	//
	// - OKAY, so the reason we're even sidecar'ing the Src to the Spec, instead of letting the Spec
	//   be the single source of truth, is because we don't want to keep OS-dependent stuff in
	//   there. That's all good, particularly elegant actually...
	//
	// - IDEA: What if we keep &'a dyn BlextSrc in the builder, then use it to generate &'a BlextSpec
	//   on `::new()`? Both would go to the builder.

	// Inform the user of selections.
	// TODO: Perhaps a fancy method (shared by core::fmt::Display) on blext::BlextSpec, which shows:
	// - Informs the user which (and how) Blender versions were selected, including any deviations (ex. larger min supported MacOS), but in simple terms overall.
	// - Informs the user which (and how) Blender platforms were selected, in simple terms overall.
	// - Informs the user how many extension zips will be built.

	// Build the extension from the specification, for the specified Blender versions / platform.
	//
	// NOTE: A lot is going on in here. Downloading and caching missing wheels, packing zips, etc. .
	let mut blext_builder =
		blext::builder::TokioBuilder::new(&*blext_src, bl_support_matrix)
			.await?;
	tracing::debug!(
		?blext_builder,
		"successfully initialized extension builder extension"
	);

	let blext_packed = blext_builder.build_zip_files().await?;
	tracing::debug!(?blext_packed, "successfully built extension");

	// Inform the user of the result.
	// TODO: Inform what was built, and where it landed.
	Ok(())
}

//####################
//# - Errors
//####################
#[derive(Debug, thiserror::Error)]
pub enum BuildError {
	#[error(transparent)]
	SrcTarget(#[from] args::SrcArgError),

	#[error(transparent)]
	BlTarget(#[from] args::BlArgError),

	#[error(transparent)]
	ParseSpecFromSource(#[from] Box<dyn blext::BlextSrcError>),

	#[error(transparent)]
	CreateBlextBuilder(#[from] blext::builder::TokioBuilderBuilderError),

	#[error(transparent)]
	BuildExtension(#[from] blext::builder::TokioBuilderError),
}

impl BuildError {
	pub fn exitcode(&self) -> exitcode::ExitCode {
		match self {
			Self::ParseSpecFromSource(_) => todo!(),
			Self::SrcTarget(err) => err.exitcode(),
			Self::BlTarget(err) => err.exitcode(),
			Self::CreateBlextBuilder(err) => todo!(),
			Self::BuildExtension(err) => todo!(),
		}
	}
}
