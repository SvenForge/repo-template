# AGENTS.md

## General guidelines

* Prefer simple, pragmatic, and effective solutions.
* Keep changes focused and minimal.
* Preserve existing style and conventions.
* Use American English in all files in this repository, unless a specific topic requires another language, such as German.

## GitLab development workflow

Follow these workflow stages in order: **plan**, **create**, **verify**, and **deploy**. Keep the issue's workflow label synchronized with its current stage by replacing the previous label with `workflow::plan`, `workflow::create`, `workflow::verify`, or `workflow::deploy`. Also apply one appropriate `type::*` label and one `priority::*` label. An agent may act as an issue owner, merge request author, or merge request reviewer.

* Treat the GitLab project linked in the title of `README.md` as the authoritative source of truth.
* Other remotes, such as GitHub mirrors, may be used only to clone the repository. Do not push to or make changes on those services.
* Work exclusively in GitLab. Push branches and commits only to the authoritative GitLab remote.
* Agents must use the `glab` CLI for all GitLab interactions, including issues, merge requests, comments, labels, assignments, reviews, and merges.

### Workflow stage transitions

* A maintainer must perform or explicitly authorize transitions from **plan** to **create** and from **create** to **verify**.
* Only a maintainer may transition an issue from **verify** to **deploy**.
* An agent must respect the scope of the current workflow stage and may ask a maintainer to transition the issue when the current stage is complete.
* The `workflow::*` label on the issue is the authoritative indicator of the current workflow stage. Do not apply `workflow::*` labels to merge requests.

### 1. Plan

* Document every in-scope difference between the repository's current and desired state in a GitLab issue. Create an issue when no relevant issue exists; otherwise update and refine the existing issue.
* Use the default issue template. Describe the problem or deviation first, then research, discuss, and document a proposed solution.
* Assign the issue to the person responsible for planning and, when practical, implementation.
* Triage duplicate or obsolete issues. Split issues whose scope is too broad. Consolidate unnecessarily narrow or overlapping issues, cross-reference the retained issue, and close those it supersedes.
* When closing, splitting, or consolidating an issue, leave a short comment explaining why.
* Move to **create** only after the problem has a clear, appropriately scoped implementation plan.

### 2. Create

* Contribute directly to an existing merge request's feature branch when appropriate; do not open another merge request targeting that branch.
* Otherwise, create a feature branch and corresponding merge request targeting `main`. Keep the `Draft:` prefix throughout **create**; it may be removed when transitioning to **verify**.
* Keep the changes in each merge request and feature branch focused and logically connected so that they are easy to understand and review.
* Link the merge request to every issue it addresses. Usually, one merge request closes one or more related issues; an issue may require multiple merge requests when its work cannot remain logically connected.
* Use the default merge request template and keep its content current as the implementation changes.
* Make atomic, logically connected commits. Each commit should represent an understandable development step and be independently revertible when practical.
* Write each commit message as a short sentence that describes the purpose and logical content of the change.
* Use the CI/CD pipeline's static analysis, code quality checks, and automated tests throughout implementation.

### 3. Verify

* Self-review the completed merge request for compliance with repository guidelines, correctness, and scope.
* Fetch the latest `main`, confirm that all relevant tests and quality checks pass, and verify that the feature branch has no conflicts. Merge `main` into the feature branch when it has diverged.
* Assign an appropriate independent reviewer, such as a code owner or maintainer, and tag them in a comment requesting review.
* Keep review discussions in GitLab threads. Answer questions, or implement requested improvements and briefly explain the response. Resolve each thread after its concern is addressed.
* When acting as a reviewer, inspect the changes and leave clear questions or actionable improvement requests in the merge request.
* Iterate until the responsible code owner or maintainer approves the merge request.

### 4. Deploy

* A maintainer enters this stage by merging the approved merge request into `main`, usually by clicking **Merge** in GitLab.
* Allow the CI/CD pipeline to perform the deployment, and complete any required manual deployment actions.
* Treat the workflow as complete only after the merged change is deployed as required. Close a linked issue only when all work needed to resolve it is complete.

## Safety and boundaries

* Do not edit or publish any secrets or credentials.
* Keep the content of the repository confidential. Do not push code, data, documentation, or proprietary know-how to public servers or APIs.
* Do not modify generated files unless the change requires regeneration.
* Do not commit, push or merge into the `main` git branch.
* Do not create git tags or other forms of "releases" unless specifically requested.
