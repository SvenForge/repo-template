# Codex

Provide optional Codex setup/maintenance scripts and Dev Container tooling. Codex is optional in the bundled template, which also activates [Agents][agents] to generate shared instructions.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `codex_cloud` | Whether to generate environment setup and maintenance scripts; defaults to true when enabled. This creates files, rather than provisioning a cloud environment. |
| `codex_devcontainer` | Whether to add Codex tooling to an available Dev Container; defaults to true when one is available. |

## After generation

Review contributed setup steps before configuring an environment to run `bash .codex/setup.sh` or `bash .codex/maintenance.sh`. They contain only the integrations supplied by selected modules. The generated scripts implement the template's existing integration; confirm that your current environment supports the repository provider and setup/maintenance commands before using them. Environment provisioning and provider compatibility are not configured by this module.

Review `AGENTS.md` and any Dev Container integration. Configure the credentials required by contributing modules through the environment's secret settings, following their setup instructions.

## Reuse reference

Supply `codex_inputs` after including the module; see the [module guide][module-guide] for shared rules.

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. The bundled host uses the Codex feature. |
| `cloud_integration` | bool | `true` when enabled; default for `codex_cloud`. |
| `devcontainer_available` | bool | `false`; direct capability supplied by the host. |
| `devcontainer_integration` | bool | `true` when a container is available; default for `codex_devcontainer`. |

`codex.vars` exports merged settings with effective `cloud_integration` (enabled and answered true) and `devcontainer_integration` (also requiring container availability). These effective values determine manifests.

Cloud integration owns `.codex/setup.sh` and `.codex/maintenance.sh`. Container integration emits feature, mount, extension, and post-create command fragments to the corresponding [Dev Container targets][devcontainer]. Shared `AGENTS.md` belongs to Agents; a custom host must activate that provider separately.

| Receiving target | Destination and fragment contract |
| --- | --- |
| `codex.setup` | `.codex/setup.sh` after its Bash header and `set -euo pipefail`: complete shell statements. |
| `codex.maintenance` | `.codex/maintenance.sh` after the same header: complete shell statements for a cached environment. |

Receivers join fragments with newlines in aggregate contribution order. Fragments share one shell scope, must tolerate strict Bash mode, and should avoid conflicting variable/function names. The targets have no rendered destination when cloud integration is disabled.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
[agents]: ../agents/README.md
[devcontainer]: ../devcontainer/README.md
