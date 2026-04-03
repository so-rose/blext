// itypst: style.rs
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

use clap::builder::styling::{AnsiColor, Effects, Style, Styles};

// Mirror Cargo's color style
// - See https://stackoverflow.com/a/79614957
pub const HEADER: Style = AnsiColor::Green.on_default().effects(Effects::BOLD);
pub const USAGE: Style = AnsiColor::Green.on_default().effects(Effects::BOLD);
pub const LITERAL: Style = AnsiColor::Cyan.on_default().effects(Effects::BOLD);
pub const PLACEHOLDER: Style = AnsiColor::Cyan.on_default();
pub const ERROR: Style = AnsiColor::Red.on_default().effects(Effects::BOLD);
pub const VALID: Style = AnsiColor::Cyan.on_default().effects(Effects::BOLD);
pub const INVALID: Style = AnsiColor::Yellow.on_default().effects(Effects::BOLD);

/// Cargo's color style
/// [source](https://github.com/crate-ci/clap-cargo/blob/master/src/style.rs)
pub const STYLES: Styles = Styles::styled()
	.header(HEADER)
	.usage(USAGE)
	.literal(LITERAL)
	.placeholder(PLACEHOLDER)
	.error(ERROR)
	.valid(VALID)
	.invalid(INVALID);
