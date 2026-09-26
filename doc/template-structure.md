# Template structure

Start with the repository README if you want to create or update a repository. This page maps the template's source for people who customize or maintain it. The [module guide](./module-guide.md) covers the module interface and reuse. See [Testing](./testing.md) for the smoke-test strategy and shared test setup.

## Repository layout

| Path | Responsibility |
| --- | --- |
| `copier.yml` | Defines feature choices, module locations, static includes, host input wiring, and the two output aggregators. |
| `modules/<name>/` | Owns a module's questions, output, file templates, and contribution fragments. |
| `template/` | Holds the generic yield template that renders the aggregated files and the template that saves Copier answers. |
| `doc/` | Holds these Markdown pages; `doc/sphinx/index.md` wraps the README and inserts the documentation table of contents. |
| `src/test_template/` | Tests module outputs and rendered projects. |
| `.gitlab-ci.yml` and `.gitlab/ci/` | Define repository checks, including the Sphinx build. |

## Design principles

- A feature has a stable name, such as `python`, independent of the directory that contains its module. Saved feature selections therefore survive a directory move when the host updates its path mapping and static include.
- Each generated destination should have one owning module. Other modules extend that file through named contribution targets. Duplicate destinations can overwrite one another; they are not yet rejected automatically.
- Modules own their settings, templates, and integration fragments. The host owns decisions that connect modules, such as passing repository metadata or declaring that another selected module provides development dependencies.
- Module templates use their own `<name>.vars` for content. Consumers use another module's `vars` for shared settings or capabilities and its `files` manifest to check whether a file is actually generated.

## Host composition

### Feature selection and module paths

The root `features` question stores selected module names. The hidden `module_paths` mapping resolves each name to a directory relative to the host template root and is not saved in Copier answers. When a module moves, change both its path entry and its static `!include`; the feature name can remain stable.

### Module registration and input wiring

The root configuration statically includes every module's `copier.yml`, even when that module is not selected. Each include is followed by a host `<name>_inputs` block that sets `enabled` from `features` and passes any cross-module values. Place providers before consumers so a consumer input can use the provider's output. Deselecting a feature stops it from contributing files; it does not unload its configuration.

### Aggregation and rendering

1. Each module computes one output with `vars`, `files`, and `contributions`.
2. The hidden root `files` and `contributions` values iterate selected features in their selected order. They import each module's `exports.jinja` with context and prefix module-relative template paths with `module_paths[feature]`.
3. The yield template under `template/` renders each aggregated file at its project-relative destination. A receiving file can include fragments from the aggregated contributions that match one of its named targets.
4. The answers template saves user answers, including stable feature names, for later Copier updates. Hidden host values such as `module_paths` are not saved.

## Generated project

A manifest record separates source from destination: `template: files/AGENTS.md.jinja` is relative to its module, while `path: AGENTS.md` is relative to the generated project. The module directories and root configuration are template sources; only the selected manifest files and Copier's answers file appear in the generated project. See the [module guide](./module-guide.md) for the path rules and a working consumer example.
