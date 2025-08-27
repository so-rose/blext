// Replaces BLReleaseOfficial.
// Implement BLVersion

pub enum BLVersionOfficial {
    BL4_2_0,
    BL4_2_1,
    BL4_2_2,
    BL4_2_3,
    BL4_2_4,
    BL4_2_5,
    BL4_2_6,
    BL4_2_7,
    BL4_2_8,
    BL4_3_0,
    BL4_3_1,
    BL4_3_2,
    BL4_4_0,
}
// TODO: Would it be better to have a runtime-readable TOML file that contains version information,
// which this object parses - instead of hard-coding this information in an enum w/magic values in impl?

//impl BLVersion for BLVersionOfficial
