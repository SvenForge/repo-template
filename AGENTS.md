# AGENTS.md

## General guidelines

* Prefer simple, pragmatic, and effective solutions.
* Keep changes focused and minimal.
* Preserve existing style and conventions.
* Use American English in all files in this repository, unless a specific topic requires another language, such as German.

## GitLab development workflow

Follow these workflow stages in order: **plan**, **create**, **verify**, and **deploy**. Use the corresponding `workflow::plan`, `workflow::create`, `workflow::verify`, or `workflow::deploy` label to show an issue's current stage. Also apply one appropriate `type::*` label and one `priority::*` label. An agent may act as an issue owner, merge request author, or merge request reviewer.

* Work exclusively in GitLab. The GitHub repository is only a source for cloning into the remote agent environment; do not push to or otherwise interact with GitHub.
* Push branches and commits only to the GitLab remote.
* Use the `glab` CLI for all GitLab interactions, including issues, merge requests, comments, labels, assignments, reviews, and merges.

### 1. Plan

* Document every observed difference between the repository's current and desired state in a GitLab issue. Create an issue for a new observation, or update and refine an existing relevant issue.
* Use the default issue template. Describe the problem or deviation first, then research, discuss, and document a proposed solution.
* Assign the issue to the person responsible for planning and, when practical, implementation.
* Triage duplicate or obsolete issues. Split issues whose scope is too broad, and merge issues that are unnecessarily narrow or overlapping.
* When closing, splitting, or merging an issue, leave a short comment explaining why.
* Move to **create** only after the problem has a clear, appropriately scoped implementation plan.

### 2. Create

* Implement changes on a feature branch and open a merge request; never push changes directly to `main`.
* Link the merge request to every issue it addresses. A merge request may resolve multiple closely related issues, and an issue may require multiple merge requests.
* Keep each merge request focused on one clear topic so that it is easy to understand and review.
* Use the default merge request template and keep its content current as the implementation changes.
* Make atomic, logically connected commits. Each commit should represent an understandable development step and be independently revertible when practical.
* Write each commit message as a short sentence that describes the purpose and logical content of the change.
* Use the CI/CD pipeline's static analysis, code quality checks, and automated tests throughout implementation.

### 3. Verify

* Self-review the completed merge request for compliance with repository guidelines, correctness, and scope.
* Confirm that all relevant tests and quality checks pass and that the feature branch has no conflicts with the latest `main`. Merge the latest `main` into the feature branch when necessary.
* Assign an appropriate independent reviewer, such as a code owner or maintainer, and tag them in a comment requesting review.
* Keep review discussions in GitLab threads. Answer questions, or implement requested improvements and briefly explain the response. Resolve each thread after its concern is addressed.
* When acting as a reviewer, inspect the changes and leave clear questions or actionable improvement requests in the merge request.
* Iterate until the responsible code owner or maintainer approves the merge request.

### 4. Deploy

* The maintainer enters this stage by using `glab` to merge the approved merge request into `main`.
* Allow the CI/CD pipeline to perform the deployment, and complete any required manual deployment actions.
* Treat the workflow as complete only after the merged change is deployed as required. Close a linked issue only when all work needed to resolve it is complete.

## Safety and boundaries

* Do not edit or publish any secrets or credentials.
* Keep the content of the repository confidential. Do not push code, data, documentation, or proprietary know-how to public servers or APIs.
* Do not modify generated files unless the change requires regeneration.
* Do not commit, push or merge into the `main` git branch.
* Do not create git tags or other forms of "releases" unless specifically requested.
