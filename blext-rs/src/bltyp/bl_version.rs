use super::bl_manifest::BLManifestVersion;
use super::bl_platform::BLPlatform;
use std::collections::HashSet;

//####################
//# - trait: BLVersion
//####################
// A single, particular version of Blender.
pub trait BLVersion {
    fn released_on(&self) -> String;
    fn python_version(&self) -> (usize, usize, usize, usize, usize);
    // TODO: Perhaps a dedicated struct for "python version"?

    // TODO: We've removed the ref to official versioning. Good idea?
    // TODO: Use a generic way of referencing a release commit / version / etc.? Or leave it to the dedicatd impl? (Learning towards 2)

    fn valid_manifest_versions(&self) -> HashSet<BLManifestVersion>;
    fn valid_extension_tags(&self) -> HashSet<String>;
    // TODO: Something like an enum for valid tags, since we believe they are hard-coded into Blender itself.
    // - If they are not hard-coded into Blender proper, then something like a dynamic enum.
    fn valid_bl_platforms(&self) -> HashSet<BLPlatform>;
    // TODO: We don't need the min GLIBC / min MACOS fields seperately anymore, since they're part of the BLPlatform enum.
    // - Perhaps we want to instead use a bit of a smarter "BLPlatformSet" type thing? This current approach seems to require either adding every single GLIBC/MacOS version under the sun, or having an implicit convention that it means "minimum".

    fn valid_python_wheel_tags(&self) -> HashSet<String>;
    // TODO: Use a proper type instead of String.
    fn valid_abi_wheel_tags(&self) -> HashSet<String>;
    // TODO: Use a proper type instead of String.

    // TODO: We need a way to get a unique 'extras' tag ex. 'bl4-2' for each BLVersion.
    //
    fn pymarker_implementation_name(&self) -> &'static str;
    fn pymarker_platform_python_implementation(&self) -> &'static str;
    // TODO: Do we have to give this so explicitly? Can't it be derived?

    fn vendored_pydeps(&self) -> HashSet<String>;
    // TODO: Use a PyDep type to describe what the Blender version ships with
}

//####################
//# - trait: BLVersionSet
//####################
pub trait BLVersionSet {}
// TODO: Is this the right architecture? If so, should provide:
// - All contiguous ranges (min. inclusive, max. exclusive) of analogous/supported official Blender versions for the Blender manifest - or, alternatively, some mechanism of putting it in there.
// TODO: Should this be a range of official version (enum)s? Or min/max range fields?
