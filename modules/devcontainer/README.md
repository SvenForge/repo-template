# Dev Container

Generate `.devcontainer/devcontainer.json` for a consistent development environment. The host supplies an image and contributes tools, extensions, mounts, and setup commands through the receiving targets below.

## Questions and choices

There are no module questions. Configure the image through the module input.

## After generation

Review the image and contributed configuration, then open the generated project in a tool supporting the [Development Container specification](https://containers.dev/). The configuration imports the host's Git identity, marks the workspace safe for Git, and runs contributed setup commands. Customize it for additional system tools or project needs, and document the project's checks in its README.

## Reuse reference

Supply `devcontainer_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `image` | str | `mcr.microsoft.com/devcontainers/base:2-bookworm`; direct container image. |

### Output variables

Fields in `devcontainer.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `image` | str | Effective container image. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `.devcontainer/devcontainer.json` | Enabled. | Development environment configuration assembled from inputs and contributions. |

### Receiving targets

| Target | Destination | Fragment contract |
| --- | --- | --- |
| `devcontainer.features` | `features` object. | JSON members naming container features. |
| `devcontainer.containerEnv` | `containerEnv` object. | JSON environment-variable members. |
| `devcontainer.mounts` | `mounts` array. | JSON items describing mounts. |
| `devcontainer.postCreateCommand` | `postCreateCommand` object. | Named JSON command members. |
| `devcontainer.extensions` | `customizations.vscode.extensions` array. | JSON extension-ID string items. |

All slots are in `devcontainer.json`. Each fragment must contain valid, nonempty JSON members/items without enclosing containers or trailing commas. The receiver adds indentation and commas between fragments in aggregate order. Use distinct member names for contributions to the same object. Setup-command execution order should not depend on textual fragment order.

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `devcontainer.extensions` | Enabled. | Common VS Code extension-ID string items. |

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
