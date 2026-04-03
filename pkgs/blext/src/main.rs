// itypst: main.rs
// Copyright (C) 2025 itypst Project Contributors
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

mod arg;
mod cli;
mod style;
mod ui;

use cli::Cli;

fn main() {
	tokio::runtime::Builder::new_current_thread()
		//.enable_io()
		//.enable_time()
		.thread_name("itypst-tokio-main")
		.build()
		.expect("failed to initialize tokio runtime.")
		.block_on(async {
			match Cli::parse().entrypoint().await {
				Ok(()) => std::process::exit(exitcode::OK),
				Err(err) => {
					eprintln!("{err}");
					std::process::exit(err.exitcode());
				}
			};
		});
}
