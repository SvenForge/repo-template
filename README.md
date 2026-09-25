# [Repo Template](https://gitlab.com/sventerprise/repo-template.git)

Common [copier](https://copier.readthedocs.io/en/stable/) template to setup new or update existing Git repositories. Batteries included.

## Getting started

### Installation

Install the supported Copier release:

```shell
python -m pip install "copier==9.17.2"
```

### Usage

To create a repository from a checkout of this template:

```shell
copier copy . path/to/new-project
```

From the generated repository root, where `.copier-answers.yml` was saved, check for an available template update and then apply it:

```shell
copier check-update
copier update
```

### Advanced use

To reuse modules in your own Copier template, add this repository as a Git submodule inside your host template:

```shell
git submodule add https://gitlab.com/sventerprise/repo-template.git vendor/repo-template
```

After cloning that host, initialize its submodules with `git submodule update --init --recursive`. See [Template structure](./doc/template-structure.md) for the repository layout and [Module guide](./doc/module-guide.md) for registration, input overrides, extension points, and a working consumer example.

### Development

Develop this repository in its [development container](./.devcontainer/devcontainer.json) (VS Code Dev Containers and a Docker-compatible CLI) or the preconfigured [Codex Cloud](https://chatgpt.com/codex/cloud) environment. For a local Python environment, install the `dev` dependency group:

```shell
python -m pip install --group dev
```

The group includes Copier, pytest, Ruff, mypy, and Sphinx. Run the relevant checks for your changes; for example:

```shell
python -m pytest
make -C doc/sphinx html SPHINXOPTS='-W --keep-going'
```

## Documentation

<!-- toctree-start -->
The documentation is available on [GitLab Pages](https://sventerprise.gitlab.io/repo-template/).

For basic use, see Getting started above. For module reuse and template development, see [Template structure](./doc/template-structure.md) and [Module guide](./doc/module-guide.md).
<!-- toctree-end -->

## Contributing

### Maintainer

* [Sven Krummen](mailto:sven@nichtgerade.de) - @krum_sv

## License

Please see: [LICENSE.md](./LICENSE.md)
