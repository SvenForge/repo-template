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

- A feature names a user-facing capability, such as `python`. The host maps selected features to module inputs. One feature can enable several modules, and several features can share a module without exposing it as a choice. Saved feature names remain stable when modules are split or moved.
- Each generated destination should have one owning module. Other modules extend that file through named contribution targets. Duplicate destinations can overwrite one another; they are not yet rejected automatically.
- Modules own their settings, templates, and integration fragments. The host owns decisions that connect modules, such as passing repository metadata or declaring that another selected module provides development dependencies.
- Module templates use their own `<name>.vars` for content. Consumers use another module's `vars` for shared settings or capabilities and its `files` manifest to check whether a file is actually generated.

## Host composition

### Feature selection and module paths

The root `features` question stores selected public capabilities. The hidden `module_paths` mapping registers every module by name and host-relative directory, including support modules with no public choice. It is not saved in Copier answers. When a module moves, change both its path entry and its static `!include`; feature names can remain stable.

### Module registration and input wiring

The root configuration statically includes every module's `copier.yml`, even when disabled. Each include is followed by a host `<name>_inputs` block that defines activation and other feature-dependent settings together, alongside cross-module values. Explicitly supply `enabled` for optional modules; standalone module defaults may enable them. Place providers before consumers so a consumer input can use the provider's output. Disabled modules return empty `files` and `contributions` lists; their configuration remains loaded.

### Aggregation and rendering

1. Each module computes one output with `vars`, `files`, and `contributions`.
2. The hidden root `files` and `contributions` values iterate all `module_paths` entries in registry order. They import each module's `exports.jinja` with context and prefix module-relative template paths with its registered path. Each module is aggregated once, regardless of how many features enable it. Each manifest retains its own record order.
3. The yield template under `template/` renders each aggregated file at its project-relative destination. A receiving file can include fragments from the aggregated contributions that match one of its named targets.
4. The answers template saves user answers, including stable feature names, for later Copier updates. Hidden host values such as `module_paths` are not saved.

## Generated project

A manifest record separates source from destination: `template: files/AGENTS.md.jinja` is relative to its module, while `path: AGENTS.md` is relative to the generated project. The module directories and root configuration are template sources; only the selected manifest files and Copier's answers file appear in the generated project. See the [module guide](./module-guide.md) for the path rules and a working consumer example.
