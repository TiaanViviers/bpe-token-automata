# Commit workflow

Follow after the SKILL.md bootstrap. Canonical message and safety policy:
`@agent/rules/git-and-branches.md`.

## Preconditions

* Current branch is **not** `main`. If on `main`, create or switch to a legal
  short-lived branch first (see [pr-workflow.md](pr-workflow.md)).
* Working tree intent is clear: stage only files that belong to the requested
  change.
* Unrelated local modifications are identified and left unstaged.

## Stage

1. Inspect `git status`, `git diff`, and `git diff --cached`.
2. Stage intended paths explicitly (`git add -- path`). Avoid `git add .`
   when unrelated files are present.
3. Never stage secrets (`.env`, credentials, private keys) or accidental
   copies of private material into `project/`.

## Commit

1. Draft a concise subject that explains **why**, matching repo style:

```text
feat(dictionary): validate merge dependencies
fix(serialization): sort transitions deterministically
test(dfa): add self-merge regression cases
docs(research): record Unicode symbol decision
ci: pin Actions to Node.js 24-native releases
chore: update dependencies
```

2. Commit with a HEREDOC (never `-i` git commands):

```bash
git commit -m "$(cat <<'EOF'
feat(scope): short why-focused subject

Optional body if needed for non-obvious rationale.

EOF
)"
```

3. Run `git status` after the commit.
4. If a pre-commit hook **fails**, fix the issue and create a **new** commit.
   Do not amend a failed/rejected commit.
5. If a hook **succeeds** and auto-modifies files that must be included, amend
   only when all amend safety conditions in [History](#history) hold.

## History

Allowed when needed to complete the user's Git request and still legal under
`@agent/rules/git-and-branches.md`:

| Operation | When allowed |
|---|---|
| `git commit --amend` | User asked to amend, **or** HEAD was created by you in this session, **and** it has not been pushed, **and** the previous commit did not fail hooks |
| `git pull --ff-only` | Prefer for updating `main` or a tracking branch |
| `git fetch` + rebase onto `origin/main` | Feature branch needs updating; explain conflicts before resolving |
| Merge of `main` into a feature branch | Acceptable alternative when rebase is unsuitable; do not invent formal resolutions |
| Local branch delete | After merge/PR cleanup when the user wants cleanup and the branch is not `main` |

Still require a **separate, explicit** human instruction (see
[safety-rails.md](safety-rails.md)):

* `git reset --hard`
* force-push to `main`
* force-push that rewrites history already shared on a PR unless the user
  clearly requested that rewrite
* changing remotes or repository settings

When amending or rebasing a branch that already has an open PR and the user
asked for that rewrite, push with the necessary flags only after stating that
the remote history will change.

## Conflict handling

On merge/rebase conflicts:

1. Identify competing intent on both sides.
2. Do not silently choose between conflicting formal interpretations.
3. Preserve semantics; rerun relevant validation.
4. Document non-obvious resolutions in the PR or handoff notes.
