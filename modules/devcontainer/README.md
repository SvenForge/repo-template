# Dev Container

Provide a consistent development environment through `.devcontainer/devcontainer.json`. This feature is selected by default in the bundled template. Selected providers contribute tools, extensions, mounts, and setup commands.

## Questions and choices

There are no module questions. The bundled host chooses a Python image when the shared Pyproject module is active, and otherwise uses the base image below. Codex and Claude Code ask their own optional container-integration questions.

## After generation

Review the image and contributed configuration, then open the generated project in a tool supporting the [Development Container specification](https://containers.dev/). The configuration imports the host's Git identity, marks the workspace safe for Git, and runs contributed setup commands. Customize it for additional system tools or project needs, and document the project's checks in its README.

## Reuse reference

Supply `devcontainer_inputs` after including the module; see the [module guide][module-guide] for the shared contract.

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. The bundled host uses the Dev Container feature. |
| `image` | str | `mcr.microsoft.com/devcontainers/base:2-bookworm`; direct container image. |

`devcontainer.vars` exports the effective `enabled` and `image`. When enabled, `files` owns `.devcontainer/devcontainer.json`, and `contributions` supplies the module's common VS Code extensions to its own `devcontainer.extensions` target.

| Receiving target | JSON slot in `devcontainer.json` | Fragment format |
| --- | --- | --- |
| `devcontainer.features` | `features` object | Object members naming container features. |
| `devcontainer.containerEnv` | `containerEnv` object | Environment-variable members. |
| `devcontainer.mounts` | `mounts` array | Array items describing mounts. |
| `devcontainer.postCreateCommand` | `postCreateCommand` object | Named command members. |
| `devcontainer.extensions` | `customizations.vscode.extensions` array | Extension-ID string items. |

Each fragment must contain valid, nonempty JSON members/items without an enclosing object/array or a trailing comma. The receiver adds indentation and commas between fragments in aggregate order. Use distinct member names when multiple providers contribute to the same object. Contributed setup commands occupy an object; their execution order should not depend on the textual fragment order.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
