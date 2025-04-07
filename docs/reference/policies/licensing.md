# Licensing
!!! note "Disclaimer"
	We are not lawyers, and a such, everything written here might be hogwash.

	If in doubt, please refer to the `LICENSE` file in the repository root and/or your own legal council.

`blext` is distributed under the [AGPL](https://www.gnu.org/licenses/agpl-3.0.html) software license.

!!! question "My organization prohibits the AGPL! What do I do?"
	**If the license is stopping you** from using `blext`, then **tell us**.
	Open an Issue or send us an email.

	We are investigating a _strictly identical_, proprietary version of `blext`, as a mindful and ethical revenue stream.
	This could also easily include:

	- A private repository.
	- A standard SLA / support agreement.
	- Training and prioritized communication.

	What's **off the table** is anything that puts the AGPL version at a disadvantage, ex. exclusive features or easy access.

	_**If there's no interest, we won't pursue this!**_

!!! abstract
	At the moment, `blext` doesn't accept contributions.

	See our [Contributions Policy](contributing.md) for more.





## Why AGPL?
The AGPL guarantees your right to use, modify, fork, redistribute, **or even sell `blext`**, in whole or in part.
The AGPL also guarantees your right to ask for the source code. [^1]

[^1]: For convenience, you can find it here: <https://codeberg.org/so-rose/blext>.

What's the catch?
If you **give someone** `blext`, then you **must extend the same rights** as you yourself were given, by applying a compatible software license.

We think that's pretty fair.

!!! question "Does my extension have to be GPLv3-compatible?"
	**Yes**, but it's not our fault.

	Blender itself is `GPL` software.
	Therefore, [all extensions must be `GPLv3` compatible](https://www.blender.org/about/license/).

	A built extension contains no trace of `blext`, or code injected by `blext`.
	However, since Blender extensions run `import bpy`, and therefore, your extension too must _always_ be licensed under at least a ex. `GPLv3` or `AGPL` license.

!!! question "Can I use `blext` in other projects?"
	It's important to note that **distributing any software that uses `blext`** also requires you to use a compatible software license.

	For example, in the following (non-exclusive) cases, you must grant the user a license compatible with the AGPL:
	
	- A software library that depends on `blext`, ex. distributed on PyPi.
	- A website that uses `blext` on the backend, ex. to provide a build service.
	- An application that provides a GUI interface to `blext`.

!!! question "Do I have to make internal `blext`-based tools public?"
	**Absolutely not**.
	The AGPL only applies on _distribution_.

	If you don't give your `blext`-based tool to anyone, then nobody gets to claim any AGPL-protected rights.
