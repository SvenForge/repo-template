# Agents

Own the shared `AGENTS.md` instructions used by coding agents. This is a support module: the bundled host activates it for Codex or Claude Code, with no separate feature choice. A custom host can activate it independently.

## Questions and choices

There are no module questions. Additional instruction sections come from contributing modules, such as GitLab's development workflow.

## After generation

Review the generated general guidelines, workflow sections, and safety boundaries for the project. Add project-specific documentation pointers and conventions as needed. Claude Code's generated `CLAUDE.md` imports this same file, so maintain shared guidance here.

## Reuse reference

Supply `agents_inputs` after including the module. See the [module guide][module-guide] for precedence and composition.

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |

`agents.vars` exports `enabled`. When enabled, `files` owns `AGENTS.md`, and `contributions` provides general-guidelines and safety Markdown sections to `agents.sections`.

| Receiving target | Destination and fragment contract |
| --- | --- |
| `agents.sections` | `AGENTS.md` after its title: complete nonempty Markdown sections, including their headings. The receiver separates fragments with blank lines in aggregate contribution order. |

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
