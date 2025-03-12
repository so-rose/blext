# Options: Conforming
**How is the `blext` project conformed?**

- [Platform][to-platforms]: Select a subset of extension platforms to support.
- [Release Profiles][to-release-profiles]: Alter the extension's settings for a particular use case.

_All commands locate `blext` project can also conform them using options defined in this section._

### to Platforms
`--platform`: Target a subset of the platforms defined in `tool.blext.supported_platforms`.

- **Choices**: `linux-x64`, `linux-arm64`, `macos-x64`, `macos-arm64`, `detect`.
- **Default**: All `tool.blext.supported_platforms`.

_Can be specified several times, to specify several platforms._

!!! example "How To: Build a Linux (x64) Version of a Script Extension"
	```
	$ blext build my-blext-extension.py --platform linux-x64
	```

!!! example "How To: Show Project Extension Dependencies for Locally-Detected Platform"
	```
	$ blext show deps my-blext-extension.py --platform detect
	```



### to Release Profiles
`--profile`: Target a "release profile".

- **Choices**: `test`, `dev`, `release`, `release-debug`, `$custom`.
- **Default**: All `tool.blext.supported_platforms`.

_Any `$custom` profile defined in `pyproject.toml` can also be specified._

!!! example "How To: Prepare a Release-Debug Build of a Project Extension, from a URL"
	```
	$ blext build project+https://example.com/my-blext-extension.zip --profile release-debug
	```
