# Module guide

_TODO: Introduce the guide for module authors and templates that reuse modules._

## Module skeleton

_TODO: Describe `copier.yml`, `exports.jinja`, `files/`, and `fragments/`._

## Module interface

### Defaults, inputs, and questions

_TODO: Explain defaults, sparse input overrides, questions, and effective-value precedence._

### Output manifest

_TODO: Describe `vars`, `files`, and `contributions` and their required shape._

### Path conventions

_TODO: State the path bases for host includes and registration, module templates, and generated destinations._

### Contributions and extension points

_TODO: Explain how providers register fragments and receivers render them._

## Working on modules

### Modify an existing module

_TODO: Outline changes to files, fragments, questions, and contributions._

### Add a module

_TODO: Outline registration, input wiring, and output ownership._

### Deselect or remove a module

_TODO: Distinguish deselection from removal and describe consumer adapter cleanup._

## Reuse in another template

### Git submodule setup

_TODO: Document initialization, updates, and pinning._

### Minimal consumer example

_TODO: Show a complete host that selects Codex and Dev Container._

### Verify the render

_TODO: Show the render command and expected generated files._
