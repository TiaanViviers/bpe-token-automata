# Safety rails

Even when `git-ops` is active, stop and get a **clearer separate human
instruction** before these. Do not treat a vague "handle git" request as
approval for them.

## Always blocked without explicit extra direction

* Publishing to university GitLab (subtree push / submission publish)
* Editing or committing on the generated `submission` branch
* Force-pushing `main`
* Deleting `main` or changing default-branch / protection settings
* Modifying remotes
* Changing repository or Actions security settings
* Committing secrets, credentials, `.env` files, or private keys
* Copying private collaborative paths into `project/` to "make Git easier"
* `git reset --hard` or other destructive working-tree wipes when unrelated
  local work exists
* Rewriting history that has already been shared on a PR **unless** the user
  clearly asked for that rewrite on the feature branch

## Still allowed under git-ops (no re-ask)

These are legal within `@agent/rules/git-and-branches.md` once this skill
applies to the user's request:

* create / switch short-lived branches with legal names
* stage intended files; commit; push feature branches
* open / update GitHub PRs into `main`
* amend unpushed HEAD under the commit-workflow amend rules
* rebase or merge `main` into a feature branch to integrate
* delete local short-lived branches during cleanup the user asked for
* force-push a **feature** branch only when the user clearly requested a
  history rewrite on that branch

## Submission / GitLab reminder

Local export is fine:

```bash
./scripts/build_submission.sh
./scripts/verify_submission.sh
```

Pushing the export to GitLab is a controlled human release operation, not a
`git-ops` default.
