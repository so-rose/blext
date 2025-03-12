# `git` Resources
`git` is an incredible piece of software.
It can, however, also be a bit confusing at times.

Since **we borderline require** using `git` to manage all extension projects, we felt it would be nice to have a helpful page of `git` resources.

!!! warning
	It's worth saying: **`git` and GitHub are two very, very different things**.

	- `git` is "distributed version control software". It enables thousands of people from around the globe to collaborate on the same project.
	- GitHub is a commercial source-code hosting platform built on top of `git`.



## Learning
[A Grip on `git`](https://agripongit.vincenttunru.com/): How does `git` work?
This guide answers that question one step at a time, with great visuals to help you keep your footing.

[Learn `git` Branching](https://learngitbranching.js.org/): The puzzle game that makes you good at `git`.
**Yes, really**.



## Remembering
There is a tool that makes your console-based life much easier: [`tldr`](https://github.com/tldr-pages/tldr).


!!! example
	Forgot how `git remote` works?
	```
	$ tldr git remote
	git remote
	Manage set of tracked repositories ("remotes").
	More information: https://git-scm.com/docs/git-remote.

	 - List existing remotes with their names and URLs:
	   git remote -v

	 - Show information about a remote:
	   git remote show {{remote_name}}

	 - Add a remote:
	   git remote add {{remote_name}} {{remote_url}}

	 - Change the URL of a remote (use --add to keep the existing URL):
	   git remote set-url {{remote_name}} {{new_url}}

	 - Show the URL of a remote:
	   git remote get-url {{remote_name}}

	 - Remove a remote:
	   git remote remove {{remote_name}}

	 - Rename a remote:
	   git remote rename {{old_name}} {{new_name}}
	```

_This works for all kinds of commands, but it's particularly nice for `git` commands._



## Hosting Services
While `git` does not require a server, choosing a high-quality hosting service is generally suggested when developing extensions:

- [`projects.blender.org`](https://projects.blender.org/): Run by the Blender Foundation, accessible to everyone.
	- **Ideal For**: Keeping your extension close to Blender, on a platform that shares Blender's values.
	- **Account**: You login with your Blender ID, which is free to create.
	- **See Also**: The official [`blender.org` Extension Hosting Guide](https://developer.blender.org/docs/handbook/extensions/hosted/).

- [Codeberg](https://codeberg.org/): Community-led, non-profit, EU-based `git` server with all the bells and whistles.
	- **Ideal For**: Great features incl. CI/CD compatible with GHA. Run with respect and passion. Insulation against the whims of multinational conglomerates. _Like an organic, family-owned farm of software._
	- **Account**: Dedicated account, login with GitHub, or login with GitLab.

- [GitHub](https://github.com/): Microsoft-owned de-facto standard.
	- **Ideal For**: For better or worse, most of open source is at least mirrored here.
	- **Account**: Dedicated account.
