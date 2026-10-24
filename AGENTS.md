# AGENTS.md

## General guidelines

* Prefer simple, pragmatic, and effective solutions.
* Keep changes focused and minimal.
* Preserve existing style and conventions.
* Use American English in all files in this repository, unless a specific topic requires another language, such as German.

## Repository structure

* Consult [Template structure](doc/template-structure.md) for the repository layout.
* Consult [Module guide](doc/module-guide.md) when adding, changing or reusing modules.
* Consult [Testing](doc/testing.md) for the test strategy and shared test setup.
* Consult [Choose features](doc/features.md) for user guidance and the module documentation index, and [Reuse modules](doc/reuse.md) for custom templates.
* Follow [Writing documentation](doc/documentation.md) when adding or changing documentation. Keep module contracts in `modules/<name>/README.md`.

## GitLab development workflow

* Follow these workflow stages in order: **plan**, **create**, **verify**, and **deploy**.
* Keep the issue's workflow label synchronized with its current stage by replacing the previous label with `workflow::plan`, `workflow::create`, `workflow::verify`, or `workflow::deploy`. Also apply one appropriate `type::*` label and one `priority::*` label.
* Treat the GitLab project linked in the title of `README.md` as the authoritative source of truth. Push branches and commits only to this remote.
* Use other remotes, such as GitHub mirrors, only to clone the repository. Do not push to or make changes on those services.
* Use the native `@GitLab` plugin for GitLab interactions when available. Otherwise, use the `glab` CLI if installed. If neither is available, interact only with the local Git repository, remain in the current workflow stage, and report which required GitLab actions could not be completed.
* Before every local commit created autonomously by an agent, retrieve the authenticated GitLab user's `name` and `commit_email` through the selected interface (the native `@GitLab` plugin when available, otherwise `glab api user`). If either value is unavailable or empty, stop and report the blocker. Apply the values only to that commit with command-scoped configuration, for example `git -c user.name="<name>" -c user.email="<commit_email>" commit ...`; do not change the stored repository or global Git identity.

### Workflow stage transitions

* The user must perform or explicitly authorize transitions from **plan** to **create** and from **create** to **verify**.
* Only a maintainer may transition an issue from **verify** to **deploy**, normally by merging the approved merge request. If GitLab automatically closes the issue on merge, assigning `workflow::deploy` is optional.
* An agent must remain within the scope of the current workflow stage. When that stage is complete, ask the user to perform or to authorize the next transition.
* For open issues, the `workflow::*` label is the authoritative indicator of the current workflow stage. When an issue is automatically closed by merging its merge request, the closed state takes precedence over a stale workflow label. Do not apply `workflow::*` labels to merge requests.

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
* Use `Closes` only when merging the merge request completes all work required for the issue. Otherwise, use `Related`.
* When an issue requires multiple merge requests, transition the issue only after every required merge request completes the current stage. Keep all issues addressed by one merge request in the same workflow stage.
* Use the default merge request template and keep its content current as the implementation changes.
* Make atomic, logically connected commits. Each commit should represent an understandable development step and be independently revertible when practical.
* Write each commit message as a short sentence that describes the purpose and logical content of the change.
* Run relevant local checks throughout implementation and use CI/CD feedback to catch issues early.

### 3. Verify

* Adapt behavior to the role in the merge request. If the role is unclear, check whether the agent is assigned to the merge request as an `Assignee` or a `Reviewer`.
* Review the completed merge request for compliance with repository guidelines, correctness, and scope.
* Run all relevant local checks when feasible and confirm that the latest merge request CI/CD pipeline and all required jobs pass.
* Report checks that could not be run and any non-blocking failures or warnings in the merge request. Required checks must pass before approval.
* When acting as a reviewer:
  * Report findings only as merge request comments. Prefer comments on the relevant lines and make every recommendation actionable.
  * Keep follow-up discussions in GitLab threads and resolve each thread after its concern is addressed.
  * Do not modify code or contribute commits unless explicitly instructed to do so.
* When acting as an author:
  * Fetch the latest `main` and verify that the feature branch has no conflicts. Merge `main` into the feature branch when it has diverged.
  * Update the code as needed to address review comments, user feedback, or findings from your own review.
  * Inspect the latest changes and review discussions before editing to avoid reverting work that addressed other feedback.
  * Answer questions and briefly explain changes in GitLab threads. Resolve each thread after its concern is addressed.
* Iterate until the responsible code owner or maintainer approves the merge request.

### 4. Deploy

* A maintainer enters this stage by merging the approved merge request into `main`, usually by clicking **Merge** in GitLab.
* Allow the CI/CD pipeline to perform the deployment, and complete any required manual deployment actions.
* Treat the workflow as complete only after the merged change is deployed as required. Issues automatically closed on merge may remain closed while deployment completes; close other linked issues only when all required work is complete.

## Safety and boundaries

* Do not edit or publish any secrets or credentials.
* Keep the content of the repository confidential. Do not push code, data, documentation, or proprietary know-how to public servers or APIs.
* Do not modify generated files unless the change requires regeneration.
* Do not commit, push or merge into the `main` git branch.
* Do not create git tags or other forms of "releases" unless specifically requested.
