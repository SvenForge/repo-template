# Writing documentation

Keep the documentation short enough to read and maintain alongside the code. Readers share reference material but enter through different tasks:

| Reader | Path |
| --- | --- |
| First-time template user | README → feature chooser → selected module questions and setup → generated project's checks and first commit. |
| Returning project maintainer | Generated project's instructions → README update guidance → affected module pages → review, checks, and commit. |
| Template author | Reuse walkthrough → shared module contract → selected module references → render and maintain the pinned sources. |
| Template contributor, including an agent | README or AGENTS → structure and module guide → affected module/source → focused checks and documentation update. |

## Put information with its owner

| Location | Content |
| --- | --- |
| `README.md` | Purpose, prerequisites, canonical copy/update quick start, development setup, and links to the three reader paths. It is also the Sphinx landing page. |
| `doc/features.md` | Selection guidance, the mapping from features to modules, and the index of module pages. |
| `modules/<name>/README.md` | Module purpose, questions, work after generation, and the current input/output/target reference. |
| `doc/reuse.md` | Starter and pinned-submodule walkthroughs, including reusing documentation. |
| `doc/module-guide.md` | Shared module mechanics and change/add/remove recipes. |
| `doc/template-structure.md` | Repository map and composition/design principles. |
| `doc/testing.md` | Test strategy, shared setup, and verification commands. |
| `doc/api.md` | Generated test-support API entry for contributors. |
| `AGENTS.md` | Workflow instructions and pointers to the applicable documentation. |

Link to the owning page instead of copying its explanation. Link official tool documentation for general Copier, Sphinx, or other tool behavior. Keep project-specific links out of the reusable agent-instruction template, since generated projects do not contain this template's guides.

## Write and update module pages

Use the same order: purpose/activation, **Questions and choices**, **After generation**, then **Reuse reference**. Questions use an **Answer / Decision** table. If a module has no questions, use a short note instead. Lead with decisions and useful outcomes; keep manifests and contracts in the reference section.

Under **Reuse reference**, use these subheadings and table layouts in order. If a table would be empty, retain the subheading with a short note instead.

| Subheading | Columns |
| --- | --- |
| Input variables | Input / Type / Standalone fallback and role |
| Output variables | Variable / Type / Meaning |
| Generated files | Path / Condition / Purpose |
| Receiving targets | Target / Destination / Fragment contract |
| Emitted contributions | Target / Condition / Content |

List accepted inputs with types, defaults or calculations, and whether they supply question defaults or direct settings. Separate persisted answers and effective outputs. Describe conditional files and contributions, and document each receiving target's format and separators in its owning module. Keep host activation policies in the feature chooser. Module pages should describe their own contracts and generic requirements on the host; limit references to other modules to those necessary for understanding.

Use ordinary Markdown and reference links for cross-page dependencies. Put link definitions after `<!-- module-docs-links -->` so a consuming template can include the text and supply its own destinations, as shown in [Reuse modules](./reuse.md#reuse-module-documentation). Keep each page readable on its own.

Use American English, brief paragraphs, and consistent terms. Document necessary decisions, contracts, and user actions; leave issue history, debugging notes, exhaustive combinations, and incidental implementation details in issues or source. Update affected pages with behavior changes. Preserve useful paths and anchors when moving content, leaving short pointers when practical.

While this template is in early development and is not widely used, variable changes do not yet require migration or update guidance for existing repositories. Keep the current module contracts documented.

## Navigation and checks

Preserve the README's section order and toctree markers. Its Sphinx wrapper orders the paths: feature chooser with nested module pages, reuse and shared contract, then structure, testing, this guide, and test-support API. Module pages have one parent; other paths link to them. Keep License reachable. New module pages need both an index link and a toctree entry.

Review links in GitLab Markdown and the rendered Sphinx navigation. Run the strict build documented in [Testing](./testing.md); check that module pages appear as HTML pages in the intended order. Follow its small smoke-test policy, and regenerate generated API/build output through Sphinx rather than editing it.
