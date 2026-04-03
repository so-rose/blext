// TODO: The idea is to have a formal way of expression a "version of Python".

/// Particular version of Python.
pub struct Version {
	major: usize,
	minor: usize,
	patch: usize,
}
