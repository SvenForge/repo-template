# Agents

Generate shared coding-agent instructions in `AGENTS.md`. The host can activate this module independently and supply additional instruction sections through contributions.

## Questions and choices

There are no module questions.

## After generation

Review the generated general guidelines, contributed workflow sections, and safety boundaries for the project. Add project-specific documentation pointers and conventions as needed.

## Reuse reference

Supply `agents_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |

### Output variables

Fields in `agents.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `AGENTS.md` | Enabled. | Shared instructions assembled from contributed sections. |

### Receiving targets

| Target | Destination | Fragment contract |
| --- | --- | --- |
| `agents.sections` | `AGENTS.md` after its title. | Complete nonempty Markdown sections, including headings. The receiver separates fragments with blank lines in aggregate contribution order. |

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `agents.sections` | Enabled. | General-guidelines and safety Markdown sections. |

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
