# [Repo Template](https://gitlab.com/sventerprise/repo-template)

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

The root questionnaire is the only Copier entry point. Its `features` question
selects independently maintained modules. Each module keeps its conditional
questions and template content together under `template/modules/<feature>/`;
output paths in `template/` conditionally include that content. Question names
and output paths must be unique across modules.

## Documentation
*TBW*

## Contributing

Install the development dependencies and run the smoke tests:

```shell
python -m pip install --requirement requirements-dev.txt
pytest
```

### Maintainer
* [Sven Krummen](sven@nichtgerade.de) - @krum_sv

## License
Copyright © 2026 Sven Krummen. All rights reserved.
