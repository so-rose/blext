use libblext as blext;

//####################
//# - struct: Blender Extension Source Argument
//####################
#[derive(clap::Parser, Debug)]
#[clap(next_help_heading = "Source Target")]
/// Specifies the location of a Blender extension's source code.
pub struct SrcArg {
	/// Directory containing a blext project as a `uv`-compatible Python package.
	#[arg(long, group = "src-arg")]
	dir: Option<std::path::PathBuf>,

	/// Path to a blext project.
	#[arg(long, group = "src-arg")]
	script: Option<patharg::InputArg>,

	#[command(flatten)]
	url: Option<UrlSrcArg>,

	#[command(flatten)]
	git: Option<UrlSrcArg>,
}

impl SrcArg {
	pub async fn blext_src(
		&self,
	) -> Result<Box<dyn blext::BlextSrc>, SrcArgError> {
		todo!()
	}
}
// TODO: A way to specify a source without long arguments, aka. `blext run test_extension.py`.

//####################
//# - struct: Blender Extension URL-Source Argument
//####################
#[cfg(feature = "networking")]
#[derive(clap::Parser, Debug)]
struct UrlSrcArg {
	#[arg(long, group = "src-arg")]
	url_script: Option<url::Url>,

	// TODO: A proper URL.
	// TODO: Feature-gating for networking.
	#[arg(long, group = "src-arg")]
	url_dir: Option<url::Url>,
}

//####################
//# - struct: Blender Extension git-Source Argument
//####################
#[cfg(feature = "git")]
#[derive(clap::Parser, Debug)]
struct GitSrcArg {
	/// Path or link to a repository.
	#[arg(long, group = "src-arg", required = true)]
	git_repo: String,

	/// Locate by commit ID.
	#[arg(long, group = "src-arg", value_parser = git2::Oid::from_str)]
	git_rev: Option<git2::Oid>,

	/// Locate by tag.
	#[arg(long, group = "src-arg")]
	git_tag: Option<String>,

	/// Git: Locate by Branch HEAD
	#[arg(long, group = "src-arg")]
	git_branch: Option<String>,

	/// Git: Locate on subpath
	#[arg(long, group = "src-arg")]
	git_subpath: Option<std::path::PathBuf>,
}

impl GitSrcArg {
	pub fn git_repo(
		&self,
		git_repo_cache_dir: &std::path::Path,
	) -> Result<git2::Repository, SrcArgError> {
		// TODO: Need validation of this struct! But where? clap-validate or some such?

		// TODO: Need to check if git_repo_cache_dir already contains this repository (by name).
		// - If no, continue as implemented here.
		// - If yes, then:
		//   - How do we know? Repo name & remote URL of 'origin' match?
		//   - How do we get the name of this repository before cloning?
		//   - What then? Re-fetch then checkout the requested cid/branch/tag?

		// Register callbacks, as hooks into the cloning process.
		let callbacks = {
			let mut callbacks = git2::RemoteCallbacks::new();
			// TODO: Add some key stuff:
			// - Add credentials given by the user using 'callbacks.credentials'.
			// - Certificate failure callback w/user input, via 'callbacks.certificate_check'.
			// - "Total progress" to async channel with 'callbacks.transfer_progress'.
			// - "Number of objects" to async channel with 'callbacks.transfer_progress'.
			callbacks
		};

		// Configure the particulars of the fetch.
		let fetch_options = {
			let mut fetch_options = git2::FetchOptions::new();
			// TODO: Maybe add some "fetch tags" stuff?
			fetch_options
		};

		// Create a repository builder for cloning.
		let mut repo_builder = git2::build::RepoBuilder::new();
		repo_builder.fetch_options(fetch_options);

		// Case: If the user provided a git branch, then
		if let Some(git_branch) = &self.git_branch {
			repo_builder.branch(&git_branch);
		};

		// Clone the git repository to the cache path.
		let clone_path = git_repo_cache_dir.join("repo");
		Ok(repo_builder.clone(&self.git_repo, &clone_path).unwrap())
		// TODO: Get repository name properly and use to clone.
		// TODO: Handle any clone errors.
	}
}

//####################
//# - Errors
//####################
#[derive(Debug, thiserror::Error)]
pub enum SrcArgError {}

impl SrcArgError {
	pub fn exitcode(&self) -> exitcode::ExitCode {
		todo!()
	}
}
