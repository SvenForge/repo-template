# Copier

Scaffold a repository that will itself be a Copier template. This feature is optional in the bundled template. For the generation and submodule walkthroughs, see [Reuse modules][reuse].

## Questions and choices

`copier_module_name` names the initial module, defaulting to `custom`. Use lowercase letters, digits, and underscores, starting with a letter; reserved host/Jinja names are rejected. Clear the answer to skip creating an initial module.

## After generation

The new host contains rendering infrastructure and an optional empty module. Its first inner render creates only `.copier-answers.yml`. Add questions, files, or contributions to the module manifest to generate useful project content; its configuration marks the question insertion point with a TODO. Follow the [module guide][module-guide] when extending it.

## Reuse reference

Supply `copier_inputs` after including the module. Shared precedence and output/path conventions are in the [module guide][module-guide].

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. The bundled host activates it only for the Copier feature. |
| `version` | str | `9.17.2`; direct minimum version for the generated host. The bundled host supplies its supported Copier version. |
| `module_name` | str | `custom`; default for `copier_module_name`, preserving an explicit empty answer. |

`copier.vars` exports the effective `enabled`, `version`, and answered `module_name`.

When enabled, `files` owns `copier.yml` and two generic templates under `template/`: the yield template named `{% yield file from files %}{{ file.path }}{% endyield %}.jinja` and the answers template named `{{ _copier_conf.answers_file }}.jinja`. A nonempty name also generates `modules/<name>/copier.yml` and `modules/<name>/exports.jinja`.

The outer generation substitutes the version/name and preserves the inner Jinja expressions for the next Copier run. This module emits no contributions and has no receiving targets. Its README and other template source files are not copied into the generated project.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
[reuse]: ../../doc/reuse.md
