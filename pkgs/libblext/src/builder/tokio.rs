use super::ty::{BlextBuilder, BlextBuilderError};
use crate::{BlextSpec, BlextSrc, BlextSrcError, bl, spec, src};
use rayon::iter::{IntoParallelRefIterator, ParallelIterator};
use std::io::Write;

fn invert<'a, 'b, A, B>(
	original: &'a hashbrown::HashMap<&'a A, hashbrown::HashSet<&'b B>>,
) -> hashbrown::HashMap<&'b B, hashbrown::HashSet<&'a A>>
where
	A: std::hash::Hash + Eq + Sync,
	B: std::hash::Hash + Eq + Sync,
{
	original
		.par_iter()
		.fold(
			hashbrown::HashMap::new,
			|mut acc: hashbrown::HashMap<&'b B, hashbrown::HashSet<&'a A>>,
			 (a_ref, bs)| {
				let a: &'a A = *a_ref;
				for b_ref in bs.iter() {
					let b: &'b B = *b_ref;
					acc.entry(b)
						.or_insert_with(hashbrown::HashSet::new)
						.insert(a);
				}
				acc
			},
		)
		.reduce(hashbrown::HashMap::new, |mut acc, partial| {
			for (b, a_set) in partial {
				acc.entry(b)
					.or_insert_with(hashbrown::HashSet::new)
					.extend(a_set);
			}
			acc
		})
}

//####################
//# - enum: Entry in a Zip
//####################
#[derive(Debug)]
pub enum ZipEntry {
	Buffer {
		dst_path: std::path::PathBuf,
		compression: zip::CompressionMethod,
		last_modified: chrono::DateTime<chrono::Utc>,

		buffer: bytes::Bytes,
	},
	Path {
		dst_path: std::path::PathBuf,
		compression: zip::CompressionMethod,
		last_modified: chrono::DateTime<chrono::Utc>,

		src_path: std::path::PathBuf,
	},
	FileInZip {
		dst_path: std::path::PathBuf,

		src_path: std::path::PathBuf,
		src_zip_path: std::path::PathBuf,
	},
	// TODO:
	// - We need this so that we can pre-zip each cached wheel, then copy it over without
	//   re-compression, for high performance (and avoidance of pre-packing).
}

impl ZipEntry {
	/// Write this entry to a zip file.
	///
	/// # Warnings
	/// `zip.finish()` must be called after this function.
	/// While this _is_ done automatically on [`Drop`], any failure would become a silent failure.
	///
	/// See [`zip::write::ZipWriter`].
	pub fn write_to_zip(
		&self,
		zip: &mut zip::ZipWriter<impl std::io::Write + std::io::Seek>,
	) -> Result<(), ZipEntryError> {
		// Write data to the currently active file in the zip.
		match self {
			Self::Buffer {
				dst_path,
				compression,
				buffer,
				..
			} => {
				tracing::info!(
					zip_entry = ?self,
					"writing buffer entry to zip file"
				);

				// Start write to a file in the zip.
				let options = zip::write::SimpleFileOptions::default()
					.compression_method(*compression);
				zip.start_file(dst_path.to_str().unwrap(), options).unwrap();

				// Write data to zip.
				zip.write_all(buffer).unwrap();
			}
			Self::Path {
				dst_path,
				compression,
				src_path,
				..
			} => {
				tracing::info!(
					zip_entry = ?self,
					"writing path entry to zip file"
				);

				// Start write to a file in the zip.
				let options = zip::write::SimpleFileOptions::default()
					.compression_method(*compression);
				zip.start_file(dst_path.to_str().unwrap(), options).unwrap();

				// Write data to zip.
				let mut src_file = std::fs::File::open(src_path).unwrap();
				std::io::copy(&mut src_file, zip).unwrap();
			}
			Self::FileInZip {
				dst_path,
				src_path,
				src_zip_path,
			} => {
				let zip_file = std::fs::File::open(src_path).unwrap();
				let mut src_zip = zip::ZipArchive::new(zip_file).unwrap();
				let dst_zip = zip;

				let file_in_zip =
					src_zip.by_name(src_zip_path.to_str().unwrap()).unwrap();

				dst_zip
					.raw_copy_file_rename(
						file_in_zip,
						dst_path.to_str().unwrap(),
					)
					.unwrap();
				// TODO: See
				// https://docs.rs/zip/latest/zip/write/struct.ZipWriter.html#method.raw_copy_file_rename.
				// - Question: How do we avoid re-parsing the zip file all the time?
			}
		}

		Ok(())
	}
}

//####################
//# - struct: Builder for Tokio-Based Extension Builder
//####################
#[derive(Debug)]
/// Blender extension builder, which relies on `tokio` and `uv`.
pub struct TokioBuilder<'a> {
	/// Source code of the Blender extension to build.
	blext_src: &'a dyn BlextSrc,

	/// Specification of the Blender extension specification to build.
	blext_spec: BlextSpec,

	/// Matrix of Blender versions and platforms to build extensions for.
	bl_support_matrix: bl::SupportMatrix,
}

impl<'a> TokioBuilder<'a> {
	/// Create a new Blender extension builder, with all parameters.
	pub async fn new(
		blext_src: &'a dyn BlextSrc,
		bl_support_matrix: bl::SupportMatrix,
	) -> Result<TokioBuilder<'a>, TokioBuilderError> {
		let blext_spec = blext_src
			.parse_blext_spec()
			.await
			.map_err(TokioBuilderError::ParseSpecFromSource)?;
		// TODO: This should be "cheap enough", because pydeps should be lazy.

		Ok(TokioBuilder::<'a> {
			blext_src,
			blext_spec,
			bl_support_matrix,
		})
	}
}

#[async_trait::async_trait]
impl<'a> BlextBuilder for TokioBuilder<'a> {
	fn blext_spec(&self) -> &BlextSpec {
		&self.blext_spec
	}

	async fn build_zip_files(
		self,
		// TODO: Pass a way of specifying a ZIP filename, parameterized by predefined variables.
		//       For instance, "%ext_version", "%bl_version". If making several ZIPs, all must
		//       follow this filename convention.
	) -> Result<src::Packed, Box<dyn BlextBuilderError>> {
		// TODO: Stages are as follows:
		// - Zip up all the files:
		//   - Generate the manifest, then zip it up.
		//   - Load .py files, process, then zip them up.
		//     - Step[Filter]: Require checks to pass.
		//     - Step[Rewrite]: Rewrite absolute imports to relative.
		//   - Download wheels, zip up.
		//     - Cache: Keep "prepacked" zips w/wheels already added.
		//
		// - Cache Mechanics:
		//   - Wheels: Keep downloaded wheels - next download is "super fast".
		//   - Pre-packing: Keep "prepacked" zips w/large files.
		let blext_spec = std::sync::Arc::new(self.blext_spec);
		let bl_support_matrix = std::sync::Arc::new(self.bl_support_matrix);

		// Split incoherent extension specification into smallest number of coherent specs.
		let coherent_blext_specs: Vec<spec::CoherentBlextSpec> = blext_spec
			.clone()
			.coherent_iter()
			.filter(|coherent_blext_spec| {
				coherent_blext_spec
					.bl_support_matrix()
					.subseteq(&self.bl_support_matrix)
			})
			.collect();

		//####################
		//# - section: Initialize Coherent Zip-Writers w/Senders
		//####################
		let zip_writer_handles: hashbrown::HashMap<
			spec::CoherentBlextSpec,
			tokio::task::JoinHandle<()>,
		> = hashbrown::HashMap::new();
		let zip_writer_txs: std::sync::Arc<
			hashbrown::HashMap<spec::CoherentBlextSpec, flume::Sender<ZipEntry>>,
		> = std::sync::Arc::new(hashbrown::HashMap::new());

		for coherent_blext_spec in coherent_blext_specs {
			// Get the concrete path to the extension zip.
			let blext_zip_path = String::from("hello");
			// TODO: Pass the path template to the CoherentBlextSpec to get a concrete path.

			// Create a channel to send `ZipEntry`s to this coherent zip.
			//
			// NOTE: This tx channel is used by "everyone else" to send data to the zip.
			let (tx, rx) = flume::bounded::<ZipEntry>(1000);
			// TODO: Configurable channel size.

			// Spawn a blocking thread for this coherent zip.
			//
			// NOTE: Each coherent zip gets a dedicated writer thread. Its job is to
			// wait for data, then compress and write it to the zip file.
			let zip_writer_handle = tokio::task::spawn_blocking(move || {
				// Create a new `.zip` file.
				let blext_zip_file =
					std::fs::File::create(&blext_zip_path).unwrap();
				let blext_zip = zip::ZipWriter::new(blext_zip_file);

				// Configure the `.zip` file to work with large files.
				blext_zip.set_auto_large_file();
				// TODO: We need to check whether the 4GB is an issue for extensions.

				// Handle Messages
				let recv_err = loop {
					match rx
						.recv_timeout(core::time::Duration::from_millis(60_000))
						// TODO: Configurable timeout.
					{
						Ok(zip_entry) => {
							// Compress and write data to the zip.
							zip_entry.write_to_zip(&mut blext_zip).unwrap();
						}
						Err(err) => break err,
					}
				};

				// Determine whether the end of the ZipEntry listener loop was expected.
				match recv_err {
					flume::RecvTimeoutError::Timeout => panic!(
						"blocking zip writer exited incorrectly, due to timeout"
					),
					flume::RecvTimeoutError::Disconnected => tracing::debug!(
						blext_zip_path,
						"blocking zip writer task exited correctly after all producers disconnected"
					),
				}

				//
				blext_zip.finish().unwrap();
			});

			// Register this coherent spec's zip-writing handle and ZipEntry sender.
			zip_writer_handles
				.insert(coherent_blext_spec.clone(), zip_writer_handle);
			// TODO: Check if this is actually cheap - it should all be references in
			// CoherentBlextSpec.
			zip_writer_txs.insert(coherent_blext_spec.clone(), tx);
		}

		// Register interest in a subset of the incoherent spec wheels.
		// TODO: Proceed with the following steps.
		// - I think we first need to register our interest in some of the wheels.
		//   - We ask CoherentBlextSpec for a list of wheels it wants.
		//   - Perhaps this goes into a HashMap...
		//   - ...or a newtype? Since wheels should be a subset of the incoherent spec.
		type PyWheel = String;
		let cspec_to_wheels: hashbrown::HashMap<
			&spec::CoherentBlextSpec,
			hashbrown::HashSet<&PyWheel>,
		> = coherent_blext_specs
			.par_iter()
			.map(|coherent_blext_spec| {
				(coherent_blext_spec, coherent_blext_spec.wheels())
			})
			.collect();
		let wheel_to_cspecs = invert(&cspec_to_wheels);

		let all_wheels: hashbrown::HashSet<&PyWheel> = cspec_to_wheels
			.par_values()
			.flat_map(|wheels| wheels.par_iter().cloned()) // Only clones the reference (cheap).
			.collect();

		for whl in all_wheels {
			// Get wheel from cache, or download it.
			// TODO: Implement this logic.
			// - Our `py::Wheel` should already have all relevant URLs and such.
			// - Use reqwest (ex. method of wheel) to download wheels directly to single-file zip.
			// - Set sensible compression level for wheel-zip; possibly very low (it's already a zip).
			// - Downloaded wheel in zip must have last_modified set to wheel publication datetime.
			// - On download done, need to yeet a "wheel available" signal over some channel.
			//
			// TODO: IN practice:
			// - Concurrently (spawn or no?) start one future per wheel.
			//   - Everything here is extremely I/O bound!
			// - If the wheel is cached, send() a "wheel available {cached}" message, then exit.
			//   - What this says is that the wheel is available & ready to be packed into a zip!
			//   - A spawned listener task then send()s a ZipEntry to all cspecs needing that wheel.
			//   - The listener can actually itself join! on ZipEntry sends - the data is identical!
			// - If the wheel is not cached, start downloading it with reqwest.
			//   - Any status messages need to bubble alll the way up to the UI (not handled here).
			//   - When done, send() a "wheel available {downloaded}" message, then exit.
			// - At the end of the day, we join all the wheel-getter futures.
			// - Once they finish, we join the listener future.
			//   - It should automatically stop once it has sent ZipEntry's for all wheels.
			// -
			// - We may want to use `wheel.filename()` (includes `<wheel-name>.whl`).
			// - We may want to use `coherent_blext_spec.wheels_root()` (includes `wheel/`). I'm
			//   unsure how that information makes it out - via the hashmap?

			// Tell all coherent extensions that need this wheel to write it.
			let whl_zip_entry = ZipEntry::FileInZip {
				dst_path: "wherever/it/is".into(),
				src_path: "downloaded/wheel/file.zip".into(),
				src_zip_path: "whl_filename.whl".into(),
				// TODO: Set src_path from process above.
				// TODO: Set last_modified to wheel publication datetime.
				// TODO: Downloader should make a single-file zip with the wheel to
				// avoid compression during pack. Use new ZipEntry enum element.
			};
			for cspec in wheel_to_cspecs[whl] {
				zip_writer_txs[cspec].send(whl_zip_entry.clone()).unwrap();
			}
		}

		// Send all extension files to all zip writers, w/processing pipelines.
		// TODO: Implement by asking BlextSrc for bytes / strings, etc. .
		// - BlextSrc decides which files to load into memory, and which to pass by path.
		//   - Processed large files will, if still too large, be put in the blext cache.
		//   - Then, the processed file will be passed by path, with metadata indicating where
		//     it should go.
		// - BlextSrc also decides what processing to do. Actually, it does it too!
		//   - By the time the builder gets a buffer / path, everything is good to go.
		//   - This makes builders satisfyingly "dumb".
		//   - Behind the scenes, the processing we want is essentially:
		//     - Rewriting absolute imports to relative imports.
		//     - Checking of `.gitignore`.

		// Generate Blender extension manifests for each CoherentBlextSpec.
		let _coherent_blext_specs = coherent_blext_specs.clone();
		let _zip_writer_txs = zip_writer_txs.clone();
		let generate_manifests_handle = tokio::task::spawn_blocking(move || {
			_coherent_blext_specs
				.par_iter()
				.map(|coherent_blext_spec| {
					(
						coherent_blext_spec,
						zip_writer_txs.get(coherent_blext_spec),
					)
				})
				.try_for_each(|(coherent_blext_spec, tx_result)| {
					let tx = tx_result.unwrap();

					let manifest = coherent_blext_spec.manifest();
					tx.send(ZipEntry::Buffer {
						dst_path: manifest.filename().into(),
						compression: zip::CompressionMethod::Deflated,
						last_modified: chrono::Utc::now(),
						buffer: manifest.export_toml().into(),
						// TODO: Last modified time to that of `pyproject.toml` or similar, etc. .
					})
					.unwrap();

					Ok(())
				})
				.unwrap();
		});

		// Join all the things, then wait for all of it to finish!
		// TODO: There are two ways to stop the zip writers: Either drop all of the per-zip senders,
		// by dropping the outermost `tx` joining all tasks w/cloned `tx`s - or wait for timeout.
		// CLEARLY, the cleanest approach is to get rid of all the `tx`s, then join all the zip
		// writers until they finish without error.

		todo!();
	}
}

//####################
//# - Errors
//####################
/// An error encountered while building a `TokioBuilder` object.
#[derive(Debug, thiserror::Error)]
pub enum ZipEntryError {}

#[derive(Debug, thiserror::Error)]
/// Error encountered while building a `TokioBuilder` object.
pub enum TokioBuilderBuilderError {
	#[error("unable to detect supported Blender versions / platforms. {0}")]
	DetectSupportMatrix(bl::SupportMatrixError),

	#[error(
		"unable to build extension for some requested Blender versions / platforms, since the extension does not support them"
	)]
	// TODO: Add {0} once SupportMatrix implements core::fmt:Display
	InvalidSupportMatrix {
		requested_matrix: bl::SupportMatrix,
		extension_matrix: bl::SupportMatrix,
		unsupported_matrix: bl::SupportMatrix,
	},

	#[error(
		"unable to unambiguously determine which Blender versions / platforms to build the extension for"
	)]
	AmbiguousSupportMatrix,
}

/// An error encountered while building a `TokioBuilder` object.
#[derive(Debug, thiserror::Error)]
pub enum TokioBuilderError {
	#[error(transparent)]
	ParseSpecFromSource(Box<dyn BlextSrcError>),
}
