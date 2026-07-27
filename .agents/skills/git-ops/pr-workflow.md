# Branch, push, and PR workflow

Follow after the SKILL.md bootstrap. Policy:
`@agent/rules/git-and-branches.md`. CI:
`@agent/specs/ci-and-quality-gates.md`. Template:
`@.github/pull_request_template.md`.

## Branch

Never develop commits on `main`.

Create or switch as needed:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c <prefix>/<short-description>
```

`<prefix>` must be one of:

```text
feature | fix | test | docs | experiment | research | ci | chore
```

Full name must match:

```text
^(feature|fix|test|docs|experiment|research|ci|chore)/[a-z0-9]+(-[a-z0-9]+)*$
```

Examples: `feature/dictionary-validator`, `ci/add-dependabot`.

If already on a valid short-lived branch for the work, keep using it. Do not
combine unrelated tickets on one branch.

## Push

1. Confirm branch name matches the regex above (CI job `branch-name` enforces
   it on PRs into `main`).
2. Push and set upstream when needed:

```bash
git push -u origin HEAD
```

3. Avoid force-push unless the user clearly requested a history rewrite on
   that feature branch. Never force-push `main`.

## Pull request

### Preconditions

* Branch is pushed and tracks `origin`.
* If `project/` changed, run and record:

```bash
cd project && make check
```

* Working tree has no unintended staged files.
* PR base is `main`.

### Create

Use `gh pr create` with a HEREDOC body that covers the repository template
checklist and summary:

```bash
gh pr create --title "<concise title>" --body "$(cat <<'EOF'
## Pull request checklist

- [x] Scope is limited; non-goals are clear (or N/A for tiny fixes)
- [ ] Linked ticket (or N/A):
- [ ] Linked handoff (or N/A):
- [ ] Research note / formal source (or N/A):
- [x] Relevant tests were added or updated
- [x] Validation run (`make check` in `project/`, plus any ticket-specific commands)
- [x] Branch name matches `feature|fix|test|docs|experiment|research|ci|chore` / kebab-case
- [x] Expected CI jobs: `branch-name`, `quality`, `submission-export`
- [ ] Documentation updated where required (or N/A)
- [x] No private, secret, or collaborative-only material entered `project/`
- [ ] AI-generated material was human-reviewed and not accepted blindly
- [ ] I can explain the implementation (including any AI-assisted parts)

## Summary

<what changed and why>

## Notes

<edge cases, follow-ups, ticket/handoff/research links, validation outcomes>

EOF
)"
```

Mark checklist items honestly. Leave human-only items (partner explanation,
blind-acceptance review) unchecked unless the human already confirmed them.

### Update an existing PR

If a PR already exists for the branch, push new commits and, when useful,
update the body with `gh pr edit`. Return the PR URL.

### After open

Report:

* PR URL
* expected CI jobs: `branch-name`, `quality`, `submission-export`
* local validation already run
* anything deliberately excluded from scope

Do not merge unless the user explicitly asks to merge **and** merge is legal
under branch protection (PR + required checks + review). Prefer leaving merge
to the human reviewer by default; if the user explicitly asks to merge, use
`gh pr merge` only when checks and policy allow.
