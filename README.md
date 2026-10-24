# [Repo Template](https://gitlab.com/svenforge/repo-template.git)

[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Documentation](https://img.shields.io/badge/docs-GitLab%20Pages-007EC6?logo=gitlab&logoColor=white)](https://svenforge.gitlab.io/repo-template/)
[![Support me on Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20me-FF5E5B?logo=kofi&logoColor=white)](https://ko-fi.com/krumsv)

Set up a Git repository without repeating the same documentation and tool configuration. [Copier](https://copier.readthedocs.io/en/stable/) asks questions and generates editable project files, which you can update as this template evolves.

Select the parts you need:

* README and license files; Sphinx documentation.
* Python testing and code checks; GitLab CI/CD.
* Dev Containers, Codex or Claude Code support, or a starter for another Copier template.

The default selection includes Core, Python, Sphinx, GitLab, and Dev Container. This template is in early development; feedback on setup and documentation is welcome.

## Getting started

### Installation

You need Git and Python 3.12 or newer. Install Copier 9.17.2 or newer:

```shell
python -m pip install "copier>=9.17.2"
```

### Usage

Generate a project and answer Copier's questions:

```shell
copier copy https://gitlab.com/svenforge/repo-template.git path/to/new-project
cd path/to/new-project
```

You can use [Choose features](./doc/features.md) to decide which parts to select and to find guidance on their questions and setup.
With default choices, you get `README.md`, `LICENSE.md`, `pyproject.toml`, documentation under `doc/`, Dev Container and GitLab configuration, and saved answers in `.copier-answers.yml`.

Review the instruction of the selected modules and customize the generated README, license, and configuration. Initialize Git, run the generated project's checks, and commit the reviewed files:

```shell
git init
git add .
git commit -m "Initialize repository"
```

To update a repository generated from this template, keep `.copier-answers.yml` and start from a clean, committed Git working tree:

```shell
copier check-update
copier update
```

Review any conflicts before committing. Copier normally uses the latest tagged template release; see its [update guide](https://copier.readthedocs.io/en/stable/updating/) for details and version selection.

To build your own template, start with [Reuse modules](./doc/reuse.md). It covers the template starter and composition from a pinned Git submodule.

### Development

Use the provided [development container](./.devcontainer/devcontainer.json) or preconfigured [Codex Cloud](https://chatgpt.com/codex/cloud) environment. For local development of this template, install the `dev` dependency group:

```shell
python -m pip install --group dev
```

To develop this template, use [Template structure](./doc/template-structure.md), the [Module guide](./doc/module-guide.md), and [Testing](./doc/testing.md). See [Writing documentation](./doc/documentation.md) when changing the guides or module pages.

## Documentation

<!-- toctree-start -->
The documentation is available on [GitLab Pages](https://svenforge.gitlab.io/repo-template/).

* **Use this template:** [Choose features](./doc/features.md), then follow the selected modules' questions and setup instructions.
* **Build another template:** [Reuse modules](./doc/reuse.md) and the shared [Module guide](./doc/module-guide.md).
* **Develop this template:** [Template structure](./doc/template-structure.md), [Testing](./doc/testing.md), and [Writing documentation](./doc/documentation.md).

For Copier commands and concepts, see the [Copier documentation](https://copier.readthedocs.io/en/stable/).
<!-- toctree-end -->

## Contributing

Questions, setup problems, documentation gaps, and proposed improvements are welcome in the [issue tracker](https://gitlab.com/svenforge/repo-template/-/issues). For contributions, follow the workflow in [AGENTS.md](https://gitlab.com/svenforge/repo-template/-/blob/main/AGENTS.md).

### Maintainer

* [Sven Krummen](mailto:sven@nichtgerade.de) - @krum_sv

## License

Please see: [LICENSE.md](./LICENSE.md)
