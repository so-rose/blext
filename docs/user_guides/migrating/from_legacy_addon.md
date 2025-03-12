# Migrating from Legacy Addon
!!! question "Why Switch to Extensions?"
	**Believe me, we get it**: A lot about extensions are more hassle than they're worth.
	Why mess with a thing that works?

	We made `blext` for this exact purpose: To get rid of the hassle, while taking advantage of the "good stuff" about extensions.

	We think we've succeeded; we've solved things like:

	- **PyDeps**: `blext` makes Python dependencies "just work", across all platforms your addon supports. _No more homemade `pip` logic, no more niche wheel-related problems._
	- **Absolute Imports**: In `blext` projects, absolute imports "just work". _Under the hood, they are converted to relative imports whenever you `blext build`._
	- **Mental Overhead**: The mental overhead between "code changed", "clicking on operators", and "ready to use" can be rough sometimes. We tried to minimize it greatly in `blext`. _When your extension re-builds fast, installs with the same process for you as for your users, and more, then it's easier to focus on what matters - **being awesome in space, Celia**!_

	**Any other concerns?**
	Open an Issue!

	We really want `blext` to make the `Addon -> Extension` use case pleasant.


!!! info
	_Expansion of this page is planned._ For now, we suggest browsing the rest of the documentation (but especially the [Official Extension Resources](../../resources/official_extension_resources.md)).

	Watch this space!
