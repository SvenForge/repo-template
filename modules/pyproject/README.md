# Pyproject

Generate `pyproject.toml`, select the shared Python version, and contribute installation commands. Host inputs supply project metadata, dependency-group availability, and installation policy. A dependency-only setup can be used without application scaffolding.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `python_version` | Minimum Python major/minor version, such as `3.12` (the default). The host can also use this output for runtime/tool configuration. |

## After generation

Review project metadata and contributed sections in `pyproject.toml`. Install the generated `dev` group with `python -m pip install --group dev` when present; add `--editable .` for an installable distribution. Generated environment integrations run the contributed installation commands when the host supplies their receivers.

## Reuse reference

Supply `pyproject_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `python_version` | str | `3.12`; default for the persisted `python_version` question. |
| `has_dependency_groups` | bool | `false`; directly enables the dependency-group section. |
| `install` | str | `none`; `none`, `dependencies`, or `editable` controls installation contributions. |
| `name`, `version` | str | `my-project`, `0.0.0`; direct project metadata. Empty version requests dynamic versioning. |
| `readme`, `license` | str | Empty; optional metadata. `NONE` is rendered as `LicenseRef-Proprietary`. |
| `license_files` | list[str] | Empty; optional license-file paths. |
| `owner_name`, `owner_email` | str | Empty; optional author metadata. |

### Output variables

Fields in `pyproject.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `python_version` | str | Answered minimum Python version. |
| `has_dependency_groups` | bool | Whether the dependency-group section is emitted. |
| `install` | str | Effective installation mode. |
| `name`, `version` | str | Effective project name and version; empty version requires a version provider. |
| `readme`, `license` | str | Effective optional metadata settings. |
| `license_files` | list[str] | Effective license-file paths. |
| `owner_name`, `owner_email` | str | Effective author metadata. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `pyproject.toml` | Enabled. | Project configuration assembled from contributed sections. |

### Receiving targets

| Target | Destination | Fragment contract |
| --- | --- | --- |
| `pyproject.sections` | `pyproject.toml`. | Complete TOML sections, separated by blank lines. Providers must avoid duplicate tables/keys. |
| `pyproject.dependency_groups` | Inside `[dependency-groups]`, before `dev`. | Complete named group assignments without another table header. Separate groups with newlines; do not redefine `dev`. |
| `pyproject.dev_dependencies` | Inside the `dev` array. | Quoted dependency entries with trailing commas. The receiver adds indentation/newlines, not commas. |

All preserve aggregate contribution order. The last two targets exist only when the dependency section is enabled. Keep `has_dependency_groups` aligned with emitted dependency contributions.

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `pyproject.sections` | Enabled. | Project metadata TOML section. |
| `pyproject.sections` | Enabled and `has_dependency_groups` is true. | Dependency-group TOML section containing its own receiving targets. |
| `codex.setup` | Enabled and install mode is `dependencies` or `editable`. | Bash package/dependency installation statements. |
| `codex.maintenance` | Enabled and install mode is `dependencies` or `editable`. | The same installation statements for refresh. |
| `devcontainer.postCreateCommand` | Enabled and install mode is `dependencies` or `editable`. | Named JSON installation command member, without an enclosing object or trailing comma. |

Installers inspect emitted dependency contributions to decide whether to install the `dev` group. External contributions require matching receivers in the host.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
