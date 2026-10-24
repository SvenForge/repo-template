# Core

Create a project's README, license, and `.gitignore`. The host supplies activation and repository metadata defaults through this module's inputs.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `core_repository_name` | Display name used in project documentation and available to host integrations. |
| `core_repository_url` | Optional repository link; also supplies the calculated host and repository path. |
| `core_owner_name` | Optional owner name for documentation and licensing. |
| `core_owner_email` | Optional contact email, asked when an owner name is supplied. |
| `core_owner_user` | Optional username on the repository host, asked when an owner name is supplied. |
| `core_include_readme` | Whether to create the README. |
| `core_license` | All rights reserved (`NONE`, the default), MIT (`MIT`), or no license file (`NOASSERTION`). |
| `core_include_gitignore` | Whether to create `.gitignore`. |

## After generation

Replace the README TODOs for purpose/audience, installation, usage and expected result, development/checks, contributions, and any missing contact or license information. Add documentation links if none were contributed. Review the license's owner/year and the project customization area in `.gitignore`.

## Reuse reference

Supply `core_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
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

### Output variables

Fields in `core.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `repository_name`, `repository_url` | str | Answered display name and repository link. |
| `repository_host`, `repository_path` | str | Effective supplied or calculated repository location. |
| `owner_name`, `owner_email`, `owner_user` | str | Answered owner/contact details. |
| `year` | int | Effective supplied or current year. |
| `license` | str | Answered license identifier. |
| `readme`, `gitignore` | bool | Retained input/default preferences; use the file manifest for actual file presence. |
| `license_file` | bool | Retained only when explicitly supplied; otherwise file selection is calculated without exporting this field. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `README.md` | Enabled and `core_include_readme` is true. | Project introduction, setup, documentation, and contribution guidance. |
| `LICENSE.md` | Enabled and effective license-file selection is true. | Chosen license text. |
| `.gitignore` | Enabled and `core_include_gitignore` is true. | Shared ignore patterns and a project customization area. |

### Receiving targets

| Target | Destination | Fragment contract |
| --- | --- | --- |
| `core.readme.documentation` | README Documentation section. | Nonempty Markdown blocks, separated by blank lines. An empty slot produces a customization TODO. Preserve the surrounding toctree markers when adapting the README. |
| `core.gitignore` | `.gitignore`. | Complete ignore-pattern/comment lines, separated by blank lines before a project customization heading. |

Both targets preserve aggregate contribution order and require their receiving files to be generated.

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `core.gitignore` | Enabled and gitignore is generated. | Common ignore-pattern/comment lines. |

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
