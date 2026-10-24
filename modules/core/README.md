# Core

Create a project's README, license, and `.gitignore`. Core is selected by default in the bundled template and can be deselected.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `core_repository_name` | Display name used in project documentation and as a default for other features. |
| `core_repository_url` | Optional repository link; also supplies the host and repository path for integrations. |
| `core_owner_name`, `core_owner_email`, `core_owner_user` | Optional owner/contact details. Email and username are asked when an owner name is supplied. |
| `core_include_readme` | Whether to create the README. |
| `core_license` | All rights reserved (`NONE`, the default), MIT (`MIT`), or no license file (`NOASSERTION`). |
| `core_include_gitignore` | Whether to create `.gitignore`. |

## After generation

Replace the README TODOs for purpose/audience, installation, usage and expected result, development/checks, contributions, and any missing contact or license information. Add documentation links if none were contributed. Review the license's owner/year and the project customization area in `.gitignore`.

## Reuse reference

Supply `core_inputs` after including the module. See the [shared module guide][module-guide] for precedence and path rules. These are standalone fallbacks; the bundled host supplies `enabled` from feature selection.

| Input | Type | Fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `repository_name` | str | `My Repository`; question default. |
| `repository_url` | str | Empty; question default. |
| `repository_host` | str | Parsed from the answered URL, otherwise `gitlab.com`; calculated setting override. |
| `repository_path` | str | Parsed from the URL without `.git`, otherwise empty; calculated setting override. |
| `owner_name`, `owner_email`, `owner_user` | str | Empty; question defaults. |
| `year` | int | Current year; calculated setting override. |
| `readme`, `gitignore` | bool | `true` when enabled; question defaults. |
| `license` | str | `NONE`; question default. |
| `license_file` | bool | Whether the effective license differs from `NOASSERTION`; direct file selection. Keep false for `NOASSERTION`, which has no file template. |

`core.vars` exposes merged settings with effective repository/owner metadata, year, and license. Use `core.files` to determine actual file presence; the README/gitignore question answers control the manifest, rather than exported presence flags.

When enabled, `files` contains `README.md` and `.gitignore` according to their answers, and `LICENSE.md` according to `license_file` and the chosen license. If gitignore is generated, the module also contributes its common ignore patterns to `core.gitignore`.

| Receiving target | Destination and fragment contract |
| --- | --- |
| `core.readme.documentation` | README Documentation section: nonempty Markdown blocks. The receiver separates blocks with a blank line; an empty slot produces a customization TODO. Preserve the surrounding toctree markers when adapting the README. |
| `core.gitignore` | `.gitignore`: complete ignore-pattern/comment lines. The receiver separates fragments with a blank line and adds a project customization heading. |

Both targets preserve aggregate contribution order. There are no rendered destinations for contributions when their receiving files are omitted.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
