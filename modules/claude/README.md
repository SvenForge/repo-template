# Claude Code

Generate `CLAUDE.md` and optionally add Claude Code tooling to the Dev Container. This feature is optional in the bundled template. The host also activates [Agents][agents], which owns the shared instructions imported by `CLAUDE.md`.

## Questions and choices

`claude_devcontainer` asks whether to add Claude Code to the Dev Container, defaulting to true when a container is available. It is asked only when both the module and container availability are enabled.

## After generation

Review shared `AGENTS.md` guidance and the `CLAUDE.md` import. If using the container integration, review its tooling, mounts, and environment configuration, and complete the tool's normal authentication in your environment. This module does not create credentials or provision an account.

## Reuse reference

Supply `claude_inputs` after including the module. See the [module guide][module-guide] for precedence and manifest conventions.

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. The bundled host uses the Claude feature. |
| `devcontainer_available` | bool | `false`; direct capability supplied by the host. |
| `devcontainer_integration` | bool | `true` when a container is available; default for `claude_devcontainer`. |

`claude.vars` exports merged settings with effective `devcontainer_integration` (enabled, available, and answered true).

When enabled, `files` owns `CLAUDE.md`, whose contents import `AGENTS.md`; the custom host must activate Agents separately. The module emits Claude ignore patterns to [Core's `core.gitignore`][core]. With container integration, it contributes features, mounts, environment members, and post-create commands to the corresponding [Dev Container targets][devcontainer]. It has no receiving targets.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
[agents]: ../agents/README.md
[core]: ../core/README.md
[devcontainer]: ../devcontainer/README.md
