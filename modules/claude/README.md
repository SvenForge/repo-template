# Claude Code

Generate `CLAUDE.md` and optionally contribute Claude Code tooling to a Dev Container. The host must also provide the `AGENTS.md` file imported by `CLAUDE.md`.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `claude_devcontainer` | Whether to add Claude Code tooling to a Dev Container. Asked only when the module is enabled and a container is available; defaults to true when available. |

## After generation

Review the `CLAUDE.md` import and the shared `AGENTS.md` guidance supplied by your host. If using the container integration, review its tooling, mounts, and environment configuration, and complete the tool's normal authentication in your environment.

## Reuse reference

Supply `claude_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `devcontainer_available` | bool | `false`; host-supplied capability. |
| `devcontainer_integration` | bool | `true` when a container is available; default for `claude_devcontainer`. |

### Output variables

Fields in `claude.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `devcontainer_available` | bool | Host-supplied container availability. |
| `devcontainer_integration` | bool | Effective integration: module enabled, container available, and answer true. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `CLAUDE.md` | Enabled. | Imports `AGENTS.md`, which the host must supply separately. |

### Receiving targets

There are no receiving targets.

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `core.gitignore` | Enabled. | Claude ignore-pattern/comment lines. |
| `devcontainer.features` | Effective container integration. | JSON members selecting Claude Code tooling. |
| `devcontainer.mounts` | Effective container integration. | JSON mount items for persisted tool state. |
| `devcontainer.containerEnv` | Effective container integration. | JSON environment-variable members. |
| `devcontainer.postCreateCommand` | Effective container integration. | Named JSON setup command members. |

These contributions require matching receiving files/targets in the host. JSON fragments omit enclosing containers and trailing commas.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
