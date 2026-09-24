# [Repo Template](https://gitlab.com/sventerprise/repo-template.git)

Common [copier](https://copier.readthedocs.io/en/stable/) template to setup new or update existing Git repositories. Batteries included.

## Getting started

### Installation

Install the supported Copier release:

```shell
python -m pip install "copier==9.17.2"
```

### Usage

Render the template interactively from this repository:

```shell
copier copy . path/to/new-project
```

### Development

Use one of the supported development environments:

* Open this repository in its included [development container](./.devcontainer/devcontainer.json). VS Code with the Dev Containers extension is recommended for creating and accessing the container. Please note that a Docker-compliant CLI must be installed on your machine to start the Dev Container.
* Start an AI task in [Codex Cloud](https://chatgpt.com/codex/cloud) using the preconfigured environment for this repository.

To update this repository from its own template simply run the following command:

```shell
copier update
```

## Documentation

_TODO: Link or add documentation._

## Contributing

### Maintainer

* [Sven Krummen](mailto:sven@nichtgerade.de) - @krum_sv


## License

Please see: [LICENSE.md](./LICENSE.md)
