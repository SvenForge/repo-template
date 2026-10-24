# Reuse modules

Build another Copier template from a starter, or compose a host from selected modules in a pinned Git submodule. The [Module guide](./module-guide.md) defines their shared contract; [Choose features](./features.md) indexes the individual module references.

## Generate a template starter

Select the Copier feature to scaffold another template:

```shell
copier copy --defaults --data 'features=[copier]' https://gitlab.com/svenforge/repo-template.git my-template
copier copy --defaults my-template my-project
```

The `copier_module_name` answer defaults to `custom`; pass `--data copier_module_name=example` to rename it or `--data copier_module_name=` to skip it. The starter initially renders only its answers file. Add files and contributions through its module manifest.

## Compose a host from a Git submodule

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

Save the following as the host's `copier.yml`. It offers shared agent guidance or a development workspace using Codex and Dev Container. Both features share the instruction provider; the workspace also enables Codex and Dev Container and defaults to Cloud integration. The feature IDs differ from the module IDs. Keep static includes and path registrations aligned. The input blocks follow their includes, and the two aggregators match the root configuration.

```yaml
_min_copier_version: "9.17"
_subdirectory: template

module_paths:
  type: yaml
  when: false
  default:
    agents: vendor/repo-template/modules/agents
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
!include vendor/repo-template/modules/agents/copier.yml
---
agents_inputs:
  type: yaml
  when: false
  default: |
    enabled: {{ 'guidance' in features or 'workspace' in features }}

---
!include vendor/repo-template/modules/codex/copier.yml
---
codex_inputs:
  type: yaml
  when: false
  default: |
    enabled: {{ 'workspace' in features }}
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

## Reuse module documentation

The module README files are canonical Markdown pages beside their source. A host can include a selected page from its pinned submodule using MyST, without copying its contents or importing all upstream pages.

For a host page at `doc/agents.md` with the submodule at `vendor/repo-template`, use:

````markdown
```{include} ../vendor/repo-template/modules/agents/README.md
:end-before: <!-- module-docs-links -->
:relative-images:
```

[module-guide]: https://svenforge.gitlab.io/repo-template/doc/module-guide.html
````

Add `agents` to the host's own toctree. The marker excludes the source page's link definitions so the host can provide destinations for its own documentation or public upstream pages. Supply every reference defined below that marker in the selected module README; this Agents example needs only `module-guide`. This also avoids unresolved references to upstream pages that the host does not build. The included text follows the submodule pin; public documentation links describe the published template. Use the pinned sources when checking revision-specific behavior.

The `relative-images` option rebases image paths from the included page. For additional Markdown file links, either supply reference-link destinations as above or use MyST's `relative-docs` option with the appropriate path prefix, ensuring the destination is available to the host. See [MyST content inclusion](https://myst-parser.readthedocs.io/en/latest/syntax/organising_content.html#inserting-other-documents-directly-into-the-current-document).

Review the clearly labeled bundled-host details when adapting guidance for a different feature selector. Build the host documentation with warnings treated as errors to check inclusion and links.
