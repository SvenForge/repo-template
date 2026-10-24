# Pyproject

Own `pyproject.toml`, shared Python-version selection, and installation contributions. This support module is activated by Python or Sphinx in the bundled template; it has no separate feature choice. A documentation-only project can therefore install its dependencies without generating Python application scaffolding.

## Questions and choices

`python_version` is the minimum Python major/minor version, such as `3.12` (the default). The bundled host also uses it for CI images and the Dev Container image.

## After generation

Review project metadata and contributed sections in `pyproject.toml`. The bundled host selects editable installation for an installable Python distribution, dependency installation when providers add development dependencies, or no project/dependency installation otherwise. Install the generated `dev` group with `python -m pip install --group dev` when present; add `--editable .` for a distribution. Contributed Codex/Dev Container setup commands perform the applicable installation automatically when those integrations are generated.

## Reuse reference

Supply `pyproject_inputs` after including the module. See the [module guide][module-guide] for shared precedence and output rules.

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

The bundled host supplies activation, metadata, dependency-group availability, and install mode from provider outputs. `pyproject.vars` exports merged settings with the answered Python version; a dynamic version requires a suitable version provider, such as Python's distribution contribution.

When enabled, `files` owns `pyproject.toml`. The module contributes project metadata to its own `pyproject.sections`, and adds the dependency section when `has_dependency_groups` is true. For `dependencies` or `editable` install modes it also emits shell fragments to [Codex's `codex.setup`/`codex.maintenance`][codex] and a named setup command to [Dev Container's `devcontainer.postCreateCommand`][devcontainer]. The installers inspect emitted dependency contributions to decide whether to install the `dev` group.

| Receiving target | Destination and fragment contract |
| --- | --- |
| `pyproject.sections` | `pyproject.toml`: complete TOML sections. The receiver separates blocks with blank lines. Providers must avoid duplicate tables/keys. |
| `pyproject.dependency_groups` | Inside `[dependency-groups]`, before `dev`: complete named group assignments, without another table header. Separate groups with newlines; do not redefine `dev`. |
| `pyproject.dev_dependencies` | Inside the `dev` array: quoted dependency entries with trailing commas. The receiver supplies indentation and newlines, not commas. |

All preserve aggregate contribution order. The last two targets exist only when the dependency section is enabled. Keep `has_dependency_groups` aligned with the host's emitted dependency contributions.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
[codex]: ../codex/README.md
[devcontainer]: ../devcontainer/README.md
