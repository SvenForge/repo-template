# Codex

Provide optional environment setup/maintenance scripts and Dev Container tooling for Codex. The host supplies activation, available integrations, and any shared agent instructions.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `codex_cloud` | Whether to generate environment setup and maintenance scripts; defaults to true when enabled. This creates files, rather than provisioning a cloud environment. |
| `codex_devcontainer` | Whether to add Codex tooling to an available Dev Container; defaults to true when available. |

## After generation

Review contributed setup steps before configuring an environment to run `bash .codex/setup.sh` or `bash .codex/maintenance.sh`. They contain only the integrations supplied by the host. Confirm that your current environment supports the repository provider and setup/maintenance commands before using them; environment provisioning and provider compatibility are not configured by this module.

Review any host-supplied agent guidance and container configuration. Configure credentials required by contributing integrations through the environment's secret settings.

## Reuse reference

Supply `codex_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `cloud_integration` | bool | `true` when enabled; default for `codex_cloud`. |
| `devcontainer_available` | bool | `false`; host-supplied capability. |
| `devcontainer_integration` | bool | `true` when a container is available; default for `codex_devcontainer`. |

### Output variables

Fields in `codex.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `cloud_integration` | bool | Effective script generation: module enabled and answer true. |
| `devcontainer_available` | bool | Host-supplied container availability. |
| `devcontainer_integration` | bool | Effective integration: module enabled, container available, and answer true. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `.codex/setup.sh` | Effective cloud integration. | Bash environment setup script assembled from contributions. |
| `.codex/maintenance.sh` | Effective cloud integration. | Bash refresh script for a cached environment. |

### Receiving targets

| Target | Destination | Fragment contract |
| --- | --- | --- |
| `codex.setup` | `.codex/setup.sh` after its header and `set -euo pipefail`. | Complete Bash statements joined by newlines in aggregate order. |
| `codex.maintenance` | `.codex/maintenance.sh` after the same header. | Complete Bash statements for a cached environment, joined by newlines in aggregate order. |

Fragments share one shell scope, must tolerate strict Bash mode, and should avoid conflicting variable/function names. These targets require cloud integration to generate their receiving files.

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `devcontainer.features` | Effective container integration. | JSON members selecting Codex tooling. |
| `devcontainer.mounts` | Effective container integration. | JSON mount items for persisted tool state. |
| `devcontainer.extensions` | Effective container integration. | JSON extension-ID string items. |
| `devcontainer.postCreateCommand` | Effective container integration. | Named JSON setup command members. |

These contributions require matching receiving files/targets in the host. JSON fragments omit enclosing containers and trailing commas.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
