# Testing

The suite provides quick smoke checks for typical uses of the template. Test central user expectations: useful generated content, selected files, calculated settings, and contributions. Exhaustive input combinations and 100% coverage are not goals.

Prefer positive assertions. Check an omission only when its presence would cause a serious problem or violate the purpose of the scenario, such as generating files for an empty feature selection. Minor changes may be verified by review; every merge request does not need a new test.

## Test layers

| Location under `src/test_template/` | Responsibility |
| --- | --- |
| `test_modules/test_<name>.py` | One parameterized output test per module, using its own `copier.yml` with explicit inputs and question answers. One parameterized render test per file or fragment, using explicit Jinja context. |
| `test_integration/test_variables.py` | One parameterized test with a few representative user choices, checking host wiring and the aggregate `files` and `contributions`. |
| `test_e2e/test_copy.py` | One parameterized `copier copy` CLI test for default, empty, and maximal selections. Only this layer creates temporary template sources and generated repositories. |
| `test_e2e/test_update.py` | Empty placeholder; update testing is currently out of scope. |

Keep the existing self-test as a discovery check.

## Shared setup and cases

Use the same pattern in each module test file. Give scenarios readable names and use the records in `support.py`:

- `ModuleCase`: module inputs, question answers, and expected output fields.
- `VariableCase`: host question answers and expected context fields.
- `RenderCase`: explicit context, expected text, and an optional parser and expected parsed values.
- `TemplateCase`: CLI answers and an exhaustive mapping of expected file paths to content anchors.

Define cases directly in each test's `@pytest.mark.parametrize` list as `pytest.param(Case(...), id='scenario')`, using the appropriate record type. Keep short definitions on one line.

The shared checks compare selected mapping fields, require expected list members, and compare scalar values exactly. An empty expected list requires an empty list, such as a disabled module's manifest. They allow unrelated output to evolve. For structured output, use JSON, TOML, YAML, or Python syntax parsing; fragments can use the shared container wrappers. Macro-only helpers are rendered by naming their macro in the case.

End-to-end cases compare the complete generated file set with the keys of `TemplateCase.expected`, then check the listed content anchors. An empty tuple checks only that a file exists.

Reuse contexts and small helpers where that clarifies the scenario. Keep one or a few typical cases per template; avoid opaque boolean tuples, duplicated setup, and custom assertion frameworks.

The fixtures in `conftest.py` read the checkout without copying or cloning it. Questionnaire evaluation uses pinned Copier internals and ignores this repository's saved answers. Rendering uses Copier's Jinja environment with undefined variables treated as errors. Keep those private APIs inside the shared fixtures and check them when upgrading Copier.

## Run the checks

Install the `dev` dependency group, then run:

```shell
python -m pip install --group dev
python -m pytest
ruff check
mypy
make -C doc/sphinx html SPHINXOPTS='-W --keep-going'
```

For a focused change, pass a package or test file to pytest, for example `python -m pytest src/test_template/test_modules/test_core.py`.

CI uses the existing `python:pytest` job and trigger rules. Keep execution relatively fast through in-memory checks, reusable setup, and small scenario sets. No runtime benchmark, duration limit, or coverage-percentage gate is required.
