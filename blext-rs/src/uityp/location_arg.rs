use clap::Parser;
use std::path::PathBuf;

#[derive(Parser, Debug)]
struct GitLocationArg {
    /// Git repo of a blext project
    #[arg(long, required = true)]
    git_repo: Option<String>,

    /// Git: Locate by Commit ID
    #[arg(long, group = "location")]
    git_rev: Option<String>,

    /// Git: Locate by Tag
    #[arg(long, group = "location")]
    git_tag: Option<String>,

    /// Git: Locate by Branch HEAD
    #[arg(long, group = "location")]
    git_branch: Option<String>,

    /// Git: Locate on subpath
    #[arg(long)]
    git_subpath: Option<String>,
}

#[derive(Parser, Debug)]
#[clap(next_help_heading = "Location")]
pub struct LocationArg {
    #[arg(group = "location")]
    proj: Option<String>,

    /// Path to a blext project.
    #[arg(long, group = "location")]
    path: Option<PathBuf>,

    /// URL of a blext project.
    #[arg(long, group = "location")]
    url: Option<String>,

    #[command(flatten)]
    git: Option<GitLocationArg>,
}
