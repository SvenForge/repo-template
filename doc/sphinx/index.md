<!-- Reuse modified README.md as index page -->
```{include} ../../README.md
:relative-docs: ./
:end-before: <!-- toctree-start -->
```

```{toctree}
:maxdepth: 2
:caption: Use this template

../features
```

```{toctree}
:maxdepth: 1
:caption: Build another template

../reuse
../module-guide
```

```{toctree}
:maxdepth: 1
:caption: Develop this template

Agent instructions <../../AGENTS>
../template-structure
../testing
../documentation
../api
```

```{toctree}
:maxdepth: 1

License <../../LICENSE>
```

```{include} ../../README.md
:relative-docs: ./
:start-after: <!-- toctree-end -->
```
