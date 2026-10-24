# Choose features

Choose capabilities in Copier's checklist with Space, then confirm with Enter. All features are optional; selecting none generates only `.copier-answers.yml`. The default selection is a starting point you can change for your project.

Follow the README's Usage section on the documentation landing page to generate a repository. Use the module pages below while answering questions and completing setup afterward.

| Feature | Default | Choose it for | Main result |
| --- | --- | --- | --- |
| [Core](../modules/core/README.md) | Selected | Repository documentation and metadata | README, license, and gitignore choices. |
| [Python](../modules/python/README.md) | Selected | Python packages, tests, or code checks | Optional package/test scaffolding and selected tool configuration. |
| [Sphinx](../modules/sphinx/README.md) | Selected | Project documentation, with optional API or requirements tracking | Documentation sources and build configuration. |
| [GitLab](../modules/gitlab/README.md) | Selected | CI/CD and a contribution workflow on GitLab | Selected pipelines and issue/MR templates. |
| [Dev Container](../modules/devcontainer/README.md) | Selected | A consistent development environment | Container configuration with selected integrations. |
| [Copier](../modules/copier/README.md) | Optional | Building another Copier template | A minimal template host and optional starter module. |
| [Codex](../modules/codex/README.md) | Optional | Agent guidance and Codex integration files | Shared instructions, optional scripts and container tooling. |
| [Claude Code](../modules/claude/README.md) | Optional | Agent guidance and Claude Code container tooling | Shared instructions, `CLAUDE.md`, and optional container integration. |

Two support modules are activated by these choices: [Pyproject](../modules/pyproject/README.md) supplies `pyproject.toml` for Python or Sphinx; [Agents](../modules/agents/README.md) supplies shared `AGENTS.md` for Codex or Claude Code. They have no separate checklist choices. Sphinx works without Python application scaffolding. Python can provide tests and tools without a production package. Agent container integrations are offered when Dev Container is selected.

## After generation and later updates

Read each selected module's **After generation** section, replace applicable TODOs, and run the generated project's checks before committing. A teammate joining that repository should start with its own README; this template's development setup and test suite are for developing the generator.

Keep the saved answers file. To change choices or adopt template updates later, follow the README's update instructions and [Copier's update guide](https://copier.readthedocs.io/en/stable/updating/). Review changed files and conflicts, complete any new customization tasks, and commit the result. Update behavior and version selection belong to Copier's documentation.

```{toctree}
:hidden:
:maxdepth: 1

../modules/core/README
../modules/python/README
../modules/sphinx/README
../modules/gitlab/README
../modules/devcontainer/README
../modules/copier/README
../modules/codex/README
../modules/claude/README
```

```{toctree}
:hidden:
:maxdepth: 1
:caption: Shared support modules

../modules/pyproject/README
../modules/agents/README
```
