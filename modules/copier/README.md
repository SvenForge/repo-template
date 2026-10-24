# Copier

Scaffold a repository that will itself be a Copier template. For the generation and submodule walkthroughs, see [Reuse modules][reuse].

## Questions and choices

| Answer | Decision |
| --- | --- |
| `copier_module_name` | Initial module name, defaulting to `custom`. Use lowercase letters, digits, and underscores, starting with a letter; reserved host/Jinja names are rejected. Clear the answer to skip creating an initial module. |

## After generation

The new host contains rendering infrastructure and an optional empty module. Its first inner render creates only `.copier-answers.yml`. Add questions, files, or contributions to the module manifest to generate useful project content; its configuration marks the question insertion point with a TODO. Follow the [module guide][module-guide] when extending it.

## Reuse reference

Supply `copier_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `version` | str | `9.17` series; direct minimum version for the generated host. |
| `module_name` | str | `custom`; default for `copier_module_name`, preserving an explicit empty answer. |

### Output variables

Fields in `copier.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `version` | str | Minimum Copier version supplied to the generated host. |
| `module_name` | str | Answered starter-module name, possibly empty. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `copier.yml` | Enabled. | Inner host configuration with module registration and aggregators. |
| `template/{% yield file from files %}{{ file.path }}{% endyield %}.jinja` | Enabled. | Generic file-rendering template. |
| `template/{{ _copier_conf.answers_file }}.jinja` | Enabled. | Inner Copier answers template. |
| `modules/<name>/copier.yml` | Enabled and module name is nonempty. | Empty module configuration to extend. |
| `modules/<name>/exports.jinja` | Enabled and module name is nonempty. | Export of that module's output. |

The outer generation substitutes the version/name and preserves inner Jinja expressions for the next Copier run. Module documentation and other source files are not copied into the generated project.

### Receiving targets

There are no receiving targets.

### Emitted contributions

There are no emitted contributions.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
[reuse]: ../../doc/reuse.md
