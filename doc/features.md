# Choose features

Choose capabilities in Copier's checklist with Space, then confirm with Enter. All features are optional; selecting none generates only `.copier-answers.yml`.

Follow the README's Usage section on the documentation landing page to generate a repository. Use the module pages below while answering questions and completing setup afterward.

| Feature | Choose it for | Main result | Modules |
| --- | --- | --- | --- |
| Core | Repository documentation and metadata | README, license, and gitignore choices. | [core](../modules/core/README.md) |
| Python | Python packages, tests, or code checks | Optional package/test scaffolding and selected tool configuration. | [python](../modules/python/README.md), [pyproject](../modules/pyproject/README.md) |
| Sphinx | Project documentation, with optional API or requirements tracking | Documentation sources and build configuration. | [sphinx](../modules/sphinx/README.md), [pyproject](../modules/pyproject/README.md) |
| GitLab | CI/CD and a contribution workflow on GitLab | Selected pipelines and issue/MR templates. | [gitlab](../modules/gitlab/README.md) |
| Dev Container | A consistent development environment | Container configuration with selected integrations. | [devcontainer](../modules/devcontainer/README.md) |
| Copier | Building another Copier template | A minimal template host and optional starter module. | [copier](../modules/copier/README.md) |
| Codex | Agent guidance and Codex integration files | Shared instructions, optional scripts and container tooling. | [codex](../modules/codex/README.md), [agents](../modules/agents/README.md) |
| Claude Code | Agent guidance and Claude Code container tooling | Shared instructions, `CLAUDE.md`, and optional container integration. | [claude](../modules/claude/README.md), [agents](../modules/agents/README.md) |

Sphinx works without Python application scaffolding. Python can provide tests and tools without a production package. Agent container integrations are offered when Dev Container is selected.

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
../modules/pyproject/README
../modules/agents/README
```
