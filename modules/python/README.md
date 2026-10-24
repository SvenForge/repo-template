# Python

Set up an optional import package, tests, and selected Python code checks. Python is selected by default in the bundled template. Shared metadata, dependencies, and installation support are owned by [Pyproject][pyproject].

## Questions and choices

| Answer | Decision |
| --- | --- |
| `python_package_name` | Optional name used by Python imports, using lowercase letters/digits/underscores. Leave empty for a repository that only needs tests or tools. |
| `python_distribution_name` | Optional installable distribution name, asked when a package is named. Defaults to its name with underscores replaced by hyphens. Clear it to keep source code without creating an installable distribution. |
| `python_tools` | Select pytest, Ruff, and/or mypy; all are selected by default. An empty selection is allowed. |
| `python_testpackage_name` | Test package name, asked when pytest is selected. Defaults to `test_<package>`, or a name derived from the repository. It must differ from the production package. |

## After generation

Add production code and meaningful tests to the generated `src/` packages. Review tool configuration and development dependencies in `pyproject.toml`. Install dependencies with `python -m pip install --group dev` when that group exists; add `--editable .` when an installable distribution is configured. Run the selected tools, for example `python -m pytest`, `ruff check`, and `mypy`. Keep the generated project's own README current with its actual setup and checks.

## Reuse reference

Supply `python_inputs` after including the module. The [module guide][module-guide] describes precedence and manifests.

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. The bundled host uses the Python feature. |
| `package_name` | str | Empty; question default. |
| `distribution_name` | str | Derived from the package name, otherwise empty; question default override. |
| `tools` | list[str] | `pytest`, `ruff`, `mypy`; question default. |
| `testpackage_name` | str | Derived from package/repository name, otherwise `test_project`; question default override. |
| `repository_name` | str | `My Repository`; direct input to the test-name calculation. The bundled host supplies Core metadata. |

`python.vars` exposes merged settings and answered names/tools, plus calculated `has_distribution` (enabled with both package and distribution names). This capability is an output, not an input override.

When enabled, `files` contains `src/<package>/__init__.py` for a nonempty package. Selecting pytest adds `src/<testpackage>/__init__.py` and `test_self.py`; a production package also adds `test_import.py`.

| Emitted contribution | Condition and content |
| --- | --- |
| [Core's `core.gitignore`][core] | Enabled: Python ignore patterns. |
| [Pyproject's `pyproject.sections`][pyproject] | Installable distribution: setuptools/build configuration. Each selected tool adds its own TOML section. |
| [Pyproject's `pyproject.dev_dependencies`][pyproject] | At least one tool: development dependency entries. |

There are no receiving targets. A custom host must provide the shared Pyproject receiver and wire distribution metadata/install mode as appropriate; the module itself does not own `pyproject.toml`.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
[core]: ../core/README.md
[pyproject]: ../pyproject/README.md
