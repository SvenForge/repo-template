# Module guide

This is the current module author and consumer contract. Use it to change a module or reuse selected modules in another Copier template. See [Template structure](./template-structure.md) for the repository map.

## Module skeleton

Each module has the same small layout:

```text
modules/<name>/
├── copier.yml       # Defaults, inputs, questions, and one output
├── exports.jinja    # Exposes that output to the host
├── files/           # Templates for files the module owns
└── fragments/       # Templates contributed to other files
```

`files/` and `fragments/` contain only the templates a module needs. `exports.jinja` names the module output, for example `{% set output = codex %}`. The host imports that export with context; modules do not need their own rendering extension.

### Generate a template starter

Select the Copier feature to scaffold another template:

```shell
copier copy --defaults --data 'features=[copier]' https://gitlab.com/svenforge/repo-template.git my-template
copier copy --defaults my-template my-project
```

The `copier_module_name` answer defaults to `custom`; pass `--data copier_module_name=example` to rename it or `--data copier_module_name=` to skip it. The starter initially renders only its answers file. Add files and contributions through its module manifest.

## Module interface

### Defaults, inputs, and questions

`<name>_defaults` supplies module-owned fallback values. A host defines a sparse `<name>_inputs` mapping after the module's static include; omitted keys retain their defaults. An ordinary question may prompt the user and save its answer, while a hidden question can calculate a value needed by later questions.

Keep activation and other feature-dependent settings together in this host input block. One feature can enable several modules, and a shared module can be enabled by several features. Modules consume their namespaced inputs instead of reading the host's `features`. Explicitly supply `enabled` for optional modules, since standalone defaults may enable them. The consumer example below shows shared activation and feature-dependent integration defaults.

For an effective field, precedence is **saved or new question answer → supplied input → applicable calculation → module default**. For a question, the lower-priority values determine its prompt default. An explicit `false`, empty string, or zero is a supplied value, not a missing key. Keep input, default, and output field names consistent where they represent the same setting. Renaming a persisted question can affect existing Copier answers.

Prefix visible question help with the module's display name, such as `[Python]`, and use one distinct `qmark` consistently throughout that module. Keep questions brief, explain unfamiliar choices, and mark optional text answers with `(optional)` or an explicit instruction to leave them empty. The host owns the module selector and copy/update messages; modules own their question wording and marks.

### Output manifest

The module output always has these keys:

| Key | Meaning |
| --- | --- |
| `vars` | Effective content settings and shared capabilities. File-only choices need not be repeated here. |
| `files` | A list of `{path, template}` records for files this module owns. |
| `contributions` | A list of `{target, template}` records for fragments included by receiving files. |

Both lists exist even when empty. A disabled module returns `files: []` and `contributions: []`; the host aggregates every registered module without repeating activation logic. For example, Codex can own `AGENTS.md` with `template: files/AGENTS.md.jinja` and contribute `fragments/devcontainer.extensions.json.jinja` to `devcontainer.extensions`. A consumer that needs to know whether `AGENTS.md` exists should check the provider's `files` paths, not infer it from an input flag.

### Path conventions

| Reference | Base |
| --- | --- |
| `!include` and `module_paths` entries | Host template root. |
| A `template` in a module's `files` or `contributions` list | That module's directory. The root aggregators prefix it with the registered module path. |
| A `path` in a `files` record | Generated project root. |
| A `target` in a `contributions` record | A named extension point, not a file path. |

Jinja imports inside a module also resolve from the host loader root. Use a registered module path for a module-owned helper, such as `module_paths['custom'] ~ '/fragments/helper.jinja'`. A relative helper include or a hardcoded `modules/custom` path would break when the module is mounted elsewhere.

### Contributions and extension points

The root aggregator preserves `module_paths` registry order and each module's contribution order. Static include order separately controls provider evaluation. A receiving file selects matching `target` records and includes their templates. The receiver owns the surrounding syntax and separators; a listed fragment must render valid, nonempty content for that slot. A contribution to an absent receiver simply has no rendered destination. Keep the target name and fragment format aligned when either changes.

## Working on modules

### Modify an existing module

Edit content in its owning `files/` template or contributing `fragments/` template. When adding or removing an artifact, update its `files` or `contributions` record in the module output. Keep shared calculations consistent with `vars` and manifest selection. For a question or input change, check defaults, effective values, dependent questions, and existing saved-answer names. Check receivers and host adapters that consume changed outputs.

### Add a module

Create the module skeleton and one output with all three keys. Register it in `module_paths`, then add a matching static `!include` followed by its input override. Add a `features` choice only when exposing a public capability; a support module needs none. Put providers before consumers and define activation and other supplied settings in the input block. The generic aggregators need no module-specific edits. Check that the new module owns distinct generated destinations and that every contribution target has the expected receiver and format.

### Deselect a feature or remove a module

Deselecting a feature disables a module only when no remaining feature enables it through the host inputs. Its static configuration remains loaded. To remove a module from a host, delete its path registration, static include, input block, and module directory or submodule reference, then adjust affected feature choices and adapters. Also remove or replace **consumer adapters that still read its output**; otherwise rendering can fail with an undefined module value. Review contributions and receiving targets, then render the remaining feature combinations.

### Whitespace conventions

Use local Jinja controls with Copier's default settings. Preserve content indentation and meaningful internal whitespace; receivers supply fragment spacing and base indentation. End nonempty text files with one LF newline, and keep generic yield templates newline-free.

## Reuse in another template

### Git submodule setup

Today the supported reuse path is to mount this repository as a Git submodule. In a new host template repository, run:

```shell
mkdir consumer-template
cd consumer-template
git init
git submodule add https://gitlab.com/svenforge/repo-template.git vendor/repo-template
mkdir -p template
cp vendor/repo-template/template/*.jinja template/
```

The two copied files are the generic yield template and Copier answers template. The host must supply its own root `copier.yml`. The checked-out submodule commit becomes pinned when the host commits its gitlink. To select or update to a reviewed revision, run `git -C vendor/repo-template checkout <commit-sha>`, then stage and commit `vendor/repo-template` in the host. A fresh clone restores that revision with `git submodule update --init --recursive`.

### Minimal consumer example

Save the following as the host's `copier.yml`. It offers agent guidance or a development workspace using Codex and Dev Container. Both features share Codex; only the workspace enables Dev Container and defaults to Cloud integration. The feature IDs differ from the module IDs. Keep static includes and path registrations aligned. The input blocks follow their includes, and the two aggregators match the root configuration.

```yaml
_min_copier_version: "9.17.2"
_subdirectory: template

module_paths:
  type: yaml
  when: false
  default:
    codex: vendor/repo-template/modules/codex
    devcontainer: vendor/repo-template/modules/devcontainer

features:
  type: str
  multiselect: true
  choices:
    Agent guidance: guidance
    Development workspace: workspace
  default:
    - workspace

---
!include vendor/repo-template/modules/codex/copier.yml
---
codex_inputs:
  type: yaml
  when: false
  default: |
    enabled: {{ 'guidance' in features or 'workspace' in features }}
    cloud_integration: {{ 'workspace' in features }}
    devcontainer_available: {{ 'workspace' in features }}

---
!include vendor/repo-template/modules/devcontainer/copier.yml
---
devcontainer_inputs:
  type: yaml
  when: false
  default: |
    enabled: {{ 'workspace' in features }}

---
files:
  type: yaml
  when: false
  default: |
    {%- set result = namespace(files=[]) -%}
    {%- for module_path in module_paths.values() -%}
      {%- from module_path ~ '/exports.jinja' import output with context -%}
      {%- for file in output.files -%}
        {%- set result.files = result.files + [{
          'path': file.path,
          'template': module_path ~ '/' ~ file.template,
        }] -%}
      {%- endfor -%}
    {%- endfor -%}
    {{ result.files | to_json }}

contributions:
  type: yaml
  when: false
  default: |
    {%- set result = namespace(contributions=[]) -%}
    {%- for module_path in module_paths.values() -%}
      {%- from module_path ~ '/exports.jinja' import output with context -%}
      {%- for contribution in output.contributions -%}
        {%- set result.contributions = result.contributions + [{
          'target': contribution.target,
          'template': module_path ~ '/' ~ contribution.template,
        }] -%}
      {%- endfor -%}
    {%- endfor -%}
    {{ result.contributions | to_json }}
```

Commit the host configuration and its submodule pin, then render:

```shell
git add .gitmodules vendor/repo-template copier.yml template
git commit -m "Add reusable template modules"
copier copy --defaults . ../generated-project
```

### Verify the render

With Copier 9.17.2 and the default workspace selected, the generated project contains `AGENTS.md`, `.codex/setup.sh`, `.codex/maintenance.sh`, `.devcontainer/devcontainer.json`, and `.copier-answers.yml`. The Dev Container JSON includes Codex's contributions. Guidance alone defaults to only `AGENTS.md` and the answers file. Selecting both still emits each module's output once; selecting neither emits only the answers file. This example needs no custom Jinja extension or `--trust`. It uses a fixed Git submodule revision once the host commits the gitlink.
