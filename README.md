# [Repo Template](https://gitlab.com/sventerprise/repo-template.git)

Common [copier](https://copier.readthedocs.io/en/stable/) template to setup new or update existing Git repositories. Batteries included.

## Getting started

### Installation

Install the Copier CLI to use this template:

```shell
python -m pip install "copier>=9.17.2"
```

### Use this template

To create a new repository from this template:

```shell
copier copy https://gitlab.com/sventerprise/repo-template.git path/to/new-project
```

During the creation process, Copier prompts you to answer questions that customize the new repository.

To check for a template update and then apply it to a generated repository, run these commands from the repository root (where `.copier-answers.yml` was saved):

```shell
copier check-update
copier update
```

### Reuse this template in your own template

To reuse modules in your own Copier template, add this repository as a Git submodule inside your host template:

```shell
git submodule add https://gitlab.com/sventerprise/repo-template.git vendor/repo-template
```

After cloning that host, initialize its submodules with `git submodule update --init --recursive`. See [Template structure](./doc/template-structure.md) for the repository layout and [Module guide](./doc/module-guide.md) for registration, input overrides, extension points, and a working consumer example.

### Development

It is recommended to develop this repository in the provided [development container](./.devcontainer/devcontainer.json) (VS Code Dev Containers and a Docker-compatible CLI) or in the preconfigured [Codex Cloud](https://chatgpt.com/codex/cloud) environment. For a local Python environment, install the `dev` dependency group:

```shell
python -m pip install --group dev
```

The group includes all relevant development dependencies. Run the relevant checks for your changes; for example:

```shell
python -m pytest
ruff check
mypy
make -C doc/sphinx html SPHINXOPTS='-W --keep-going'
copier check-update
```

## Documentation

<!-- toctree-start -->
The documentation is available on [GitLab Pages](https://sventerprise.gitlab.io/repo-template/).

For module reuse and template development, see [Template structure](./doc/template-structure.md) and [Module guide](./doc/module-guide.md). For Copier commands and concepts, see the [Copier documentation](https://copier.readthedocs.io/en/stable/).
<!-- toctree-end -->

## Contributing

### Maintainer

* [Sven Krummen](mailto:sven@nichtgerade.de) - @krum_sv

## License

Please see: [LICENSE.md](./LICENSE.md)
