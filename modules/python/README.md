# Python

Set up an optional import package, tests, and selected Python code checks. Host inputs supply activation and naming defaults; tool, build, and dependency configuration is emitted as contributions for the host to receive.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `python_package_name` | Optional name used by Python imports, using lowercase letters/digits/underscores. Leave empty for a repository that only needs tests or tools. |
| `python_distribution_name` | Optional installable distribution name, asked when a package is named. Defaults to its name with underscores replaced by hyphens. Clear it to keep source code without creating an installable distribution. |
| `python_tools` | Select pytest, Ruff, and/or mypy; all are selected by default. An empty selection is allowed. |
| `python_testpackage_name` | Test package name, asked when pytest is selected. Defaults to `test_<package>`, or a name derived from the repository. It must differ from the production package. |

## After generation

Add production code and meaningful tests to the generated `src/` packages. Review the tool configuration and development dependencies supplied by the host. For a generated `dev` group, install with `python -m pip install --group dev`; add `--editable .` when an installable distribution is configured. Run the selected tools, for example `python -m pytest`, `ruff check`, and `mypy`. Keep the project's README current with its actual setup and checks.

## Reuse reference

Supply `python_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `package_name` | str | Empty; question default. |
| `distribution_name` | str | Derived from the package name, otherwise empty; question default override. |
| `tools` | list[str] | `pytest`, `ruff`, `mypy`; question default. |
| `testpackage_name` | str | Derived from package/repository name, otherwise `test_project`; question default override. |
| `repository_name` | str | `My Repository`; direct input to the test-name calculation. |

### Output variables

Fields in `python.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `package_name`, `distribution_name` | str | Answered production-package and distribution names. |
| `tools` | list[str] | Answered tool selection. |
| `testpackage_name` | str | Answered test-package name. |
| `repository_name` | str | Supplied/default name used in the test-name calculation. |
| `has_distribution` | bool | Calculated capability: enabled with both package and distribution names. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `src/<package>/__init__.py` | Enabled and package name is nonempty. | Production package scaffold. |
| `src/<testpackage>/__init__.py` | Enabled and pytest is selected. | Test package scaffold. |
| `src/<testpackage>/test_self.py` | Enabled and pytest is selected. | Test discovery smoke check. |
| `src/<testpackage>/test_import.py` | Enabled, pytest selected, and package name nonempty. | Production-package import smoke check. |

### Receiving targets

There are no receiving targets.

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `core.gitignore` | Enabled. | Python ignore-pattern/comment lines. |
| `pyproject.sections` | `has_distribution` is true. | Setuptools/build TOML configuration. |
| `pyproject.sections` | Enabled, for each selected tool. | Tool-specific TOML sections. |
| `pyproject.dev_dependencies` | Enabled and at least one tool selected. | Quoted dependency entries with trailing commas. |

The host must supply matching receiving files/targets and wire distribution metadata and installation policy as appropriate. This module does not own `pyproject.toml`.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
