<!-- Reuse modified README.md as index page -->
```{include} ../../README.md
:relative-docs: ./
:end-before: <!-- sphinx-toctree-start -->
```

```{toctree}
:maxdepth: 2
:glob:

../*
License <../../LICENSE>
```

```{include} ../../README.md
:relative-docs: ./
:start-after: <!-- sphinx-toctree-end -->
```
