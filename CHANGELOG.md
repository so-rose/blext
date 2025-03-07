## Unreleased

### BREAKING CHANGE

- All is ready for #13, and implementing #12 is now very doable. Closes #20.
- CLI interface was altered
- Closes #1. Progress on #3.

### Feat

- finish refactor w/global config
- added basic config logic
- implemented and integrated 'blext.blender' abstraction
- new ui for pre-packing feat. many fixes
- created ui module w/`ui_download_wheels` context manager
- complete beauty-refactor of `blext build` w/ugly code
- standardize legacy manylinux tags to PEP600 equivalents
- working single-file extension and CLI overhaul
- progress on single-file extension
- blob of fixes, features and refactor

### Fix

- added a dep that is very required
- more illustrative and compact dependency setup
- deleted redundant test
- added sensible exports to __init__.py files
- vendoring of wheel packing now correctly detects all use cases
- fixes from new automated testing
- setuptools portability and wheel download intiialization

### Refactor

- renamed extension_file to minimal_file_ext

## v0.3.0 (2025-01-15)

### Feat

- Better exceptions and parsing.
- Working app!

### Fix

- fixed Windows detection trying to detect Linux
- fixed --version and removed pip
