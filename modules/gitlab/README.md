# GitLab

Generate GitLab issue/MR templates and selected CI/CD pipelines. Host inputs determine which pipeline choices are available and supply repository metadata and tool settings.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `gitlab_pipeline` | Select Copier update checks, a demonstration job, Python checks when tools are configured, and Sphinx build/publication when documentation is enabled. Available jobs are selected by default. Clear all choices to generate only issue/MR templates. |
| `gitlab_pages_url` | Optional documentation URL, asked when the Sphinx pipeline and a README are present. On `gitlab.com`, the default is derived from the repository path; review it for your project's actual Pages configuration. |

## After generation

Push to the intended GitLab development project and check that runners can execute the selected jobs. Review issue/MR templates and any contributed workflow guidance. Adapt template TODOs when opening issues and merge requests.

The documentation pipeline publishes from the default branch; confirm the actual Pages URL and access settings. Copier checks need access to the saved template source. The demonstration job is optional. Ruff, mypy, and Copier checks are generated with `allow_failure`; review their results even when the pipeline succeeds.

If the host renders the environment setup integration, its GitLab fragment expects `GITLAB_TOKEN` in secret configuration and installs/authenticates the pinned `glab` CLI. Configure credentials through the environment, then verify access; never add their values to repository files.

## Reuse reference

Supply `gitlab_inputs` after including the module. See the [module guide][module-guide] for precedence, path rules, and manifest conventions.

### Input variables

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. |
| `pipeline` | list[str] | `copier`, `demo`, plus `python`/`sphinx` when available; question default override. |
| `pages_url` | str | Derived for `gitlab.com` plus a repository path, otherwise empty; question default override. |
| `repository_host`, `repository_path` | str | `gitlab.com`, empty; direct integration metadata. |
| `has_readme` | bool | `false`; controls Pages URL question visibility. |
| `copier_version` | str | `9.17` series; version installed by the Copier job. |
| `python_enabled` | bool | `false`; enables the Python pipeline choice with nonempty tools. |
| `python_tools` | list[str] | Empty; selects pytest/Ruff/mypy jobs. |
| `python_version` | str | `3.12`; Python job/build image version. |
| `has_python_distribution` | bool | `false`; whether dependency installation includes an editable project. |
| `sphinx_enabled` | bool | `false`; enables the Sphinx pipeline choice. |

### Output variables

Fields in `gitlab.vars`:

| Variable | Type | Meaning |
| --- | --- | --- |
| `enabled` | bool | Effective activation. |
| `pipeline` | list[str] | Answered pipeline selection. |
| `pages_url` | str | Answered documentation URL. |
| `repository_host`, `repository_path` | str | Effective repository location for integrations. |
| `has_readme` | bool | Host-supplied README availability. |
| `copier_version` | str | Copier version installed by the update-check job. |
| `python_enabled` | bool | Host-supplied Python-check availability. |
| `python_tools` | list[str] | Tools for which quality jobs are generated. |
| `python_version` | str | Version used in Python job images. |
| `has_python_distribution` | bool | Whether generated installation commands install an editable project. |
| `sphinx_enabled` | bool | Host-supplied documentation-pipeline availability. |

### Generated files

| Path | Condition | Purpose |
| --- | --- | --- |
| `.gitlab/issue_templates/default.md` | Enabled. | Issue description template. |
| `.gitlab/merge_request_templates/default.md` | Enabled. | Merge request description template. |
| `.gitlab-ci.yml` | Enabled and pipeline selection is nonempty. | CI workflow and includes. |
| `.gitlab/ci/<pipeline>.yml` | Enabled, for each selected pipeline. | Selected job definitions. |

### Receiving targets

There are no receiving targets.

### Emitted contributions

| Target | Condition | Content |
| --- | --- | --- |
| `agents.sections` | Enabled. | GitLab development workflow as a Markdown section. |
| `codex.setup` | Enabled. | Bash statements installing/authenticating the GitLab CLI. |
| `codex.maintenance` | Enabled. | Bash statements checking cached GitLab authentication. |
| `core.readme.documentation` | Enabled, Sphinx pipeline selected, and Pages URL nonempty. | Markdown documentation link. |

Contributions render only when the host supplies the matching receiving files/targets.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
