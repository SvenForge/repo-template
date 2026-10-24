# GitLab

Generate GitLab issue/MR templates and selected CI/CD pipelines. GitLab is selected by default in the bundled template. Other selected features determine which pipeline choices are offered.

## Questions and choices

| Answer | Decision |
| --- | --- |
| `gitlab_pipeline` | Select Copier update checks, a demonstration job, Python checks when tools are configured, and Sphinx build/publication when documentation is enabled. Available jobs are selected by default. Clear all choices to generate only issue/MR templates. |
| `gitlab_pages_url` | Optional documentation URL, asked when the Sphinx pipeline and a README are present. On `gitlab.com`, the default is derived from the repository path; review it for your project's actual Pages configuration. |

## After generation

Push to the intended GitLab development project and check that runners can execute the selected jobs. Review issue/MR templates and the workflow guidance contributed to `AGENTS.md` when that file is generated. Adapt template TODOs when opening issues and merge requests.

The Sphinx pipeline publishes documentation from the default branch; confirm the actual Pages URL and access settings in your project. Copier checks need access to the saved template source. The demonstration job is optional. Ruff, mypy, and Copier checks are generated with `allow_failure`; review their results even when the pipeline succeeds.

If using the generated Codex setup integration, its GitLab fragment expects `GITLAB_TOKEN` in the environment's secret configuration and installs/authenticates the pinned `glab` CLI. Configure credentials through your environment, then verify access; never add their values to repository files.

## Reuse reference

Supply `gitlab_inputs` after including the module. The [module guide][module-guide] explains precedence and contribution handling.

| Input | Type | Standalone fallback and role |
| --- | --- | --- |
| `enabled` | bool | `true`; direct activation. The bundled host uses the GitLab feature. |
| `pipeline` | list[str] | `copier`, `demo`, plus `python`/`sphinx` when available; question default override. |
| `pages_url` | str | Derived for `gitlab.com` plus a repository path, otherwise empty; question default override. |
| `repository_host`, `repository_path` | str | `gitlab.com`, empty; direct integration metadata. |
| `has_readme` | bool | `false`; controls Pages URL question visibility. |
| `copier_version` | str | `9.17.2`; version installed by the Copier job. |
| `python_enabled` | bool | `false`; enables the Python pipeline choice with nonempty tools. |
| `python_tools` | list[str] | Empty; selects pytest/Ruff/mypy jobs. |
| `python_version` | str | `3.12`; Python job/build image version. |
| `has_python_distribution` | bool | `false`; whether dependency installation includes an editable project. |
| `sphinx_enabled` | bool | `false`; enables the Sphinx pipeline choice. |

The bundled host supplies provider metadata, tool/runtime settings, and file-presence flags. `gitlab.vars` exports the merged settings with answered `pipeline` and `pages_url`.

When enabled, `files` always owns `.gitlab/issue_templates/default.md` and `.gitlab/merge_request_templates/default.md`. A nonempty pipeline selection adds `.gitlab-ci.yml` and `.gitlab/ci/<pipeline>.yml` for each choice.

| Emitted contribution | Condition and content |
| --- | --- |
| [Agents' `agents.sections`][agents] | Enabled: GitLab development workflow instructions. |
| [Codex's `codex.setup` and `codex.maintenance`][codex] | Enabled: GitLab CLI installation/authentication and cached authentication checks. |
| [Core's `core.readme.documentation`][core] | Sphinx pipeline selected and Pages URL nonempty: documentation link. |

There are no receiving targets. Contributions render only when the host supplies their receiving files.

<!-- module-docs-links -->
[module-guide]: ../../doc/module-guide.md
[agents]: ../agents/README.md
[codex]: ../codex/README.md
[core]: ../core/README.md
