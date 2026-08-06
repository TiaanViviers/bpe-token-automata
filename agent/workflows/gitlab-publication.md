# GitLab Publication Workflow

## Purpose

Publish only the verified contents of `project/` from GitHub `main` to the
university GitLab repository. GitHub remains the collaborative source of truth;
GitLab receives a filtered submission history.

Workflow source: [`.github/workflows/publish-gitlab.yml`](../../.github/workflows/publish-gitlab.yml).

## Safety model

The workflow:

* runs only through GitHub's manual `workflow_dispatch` interface;
* rejects any selected ref other than `main`;
* requires the exact confirmation text `publish project/ to gitlab`;
* has read-only access to the GitHub repository;
* rebuilds `submission` with `git subtree split --prefix=project`;
* runs the export verifier and `make check` in a clean extracted export;
* connects over HTTPS because university GitLab's SSH port is unreachable from
  GitHub-hosted runners;
* uses a dedicated personal access token with only `write_repository` scope;
* creates `gitlab-publication` with the verified subtree as its exact tree;
* retains subtree commits and authorship as the publication merge's second parent;
* uses GitLab's current `main` as the first parent, so publication is a normal
  fast-forward even when `main` is protected;
* rejects unmanaged GitLab drift rather than overwriting it;
* never force-pushes.

The `gitlab-submission` GitHub environment provides a place for deployment
history and optional protection rules. Required reviewers for environments in
private repositories depend on the GitHub plan, so the workflow does not treat
that feature as its only approval control.

## One-time credential setup

### Local repository guard

Each contributor should enable the tracked local safety hook and guarded default
push refspec once per clone:

```bash
./scripts/configure_gitlab_remote.sh
```

The script checks the exact GitLab URL, sets a bare `git push gitlab` to mean
only `gitlab-publication:main`, and enables a pre-push hook that verifies the
publication tree and rejects unsafe refspecs such as `main:main`. It never
pushes. Because Git hooks and remote configuration are local clone state, this
step cannot be enabled by merely cloning the repository.

The local hook is defence in depth, not a server-side security boundary: Git
allows hooks to be bypassed with `--no-verify`. Never bypass this hook. The
strongest available protection is the protected GitLab `main` branch. The
workflow deliberately works without force-push permission.

## GitHub Actions credential setup

Create a dedicated personal access token on the authorised student's GitLab
account under **Edit profile → Access → Personal access tokens**:

* name: `GitHub Actions CS345 publication`;
* expiration: after final marking;
* scope: `write_repository` only.

See GitLab's official [personal access token](https://docs.gitlab.com/user/profile/personal_access_tokens/)
and [token scope](https://docs.gitlab.com/security/tokens/access_token_scopes/)
documentation.

The token inherits that student's repository access but cannot use the GitLab
API. Store it as the GitHub repository or `gitlab-submission` environment
secret:

```text
GITLAB_HTTPS_TOKEN
```

Never place the token in a remote URL, repository file, command-line argument,
issue, or chat. The workflow exposes it only through the environment to the
tested askpass helper. GitHub masks the registered secret in workflow logs.

Rotate the token before expiry or immediately if exposure is suspected. After
the first successful HTTPS publication, remove the obsolete automation SSH key
from the GitLab profile and delete the `GITLAB_SSH_PRIVATE_KEY` GitHub secret.

### Configure the optional GitHub environment guard

Open **Settings → Environments → gitlab-submission**. Where the GitHub plan
supports these controls:

* restrict deployment branches to `main`;
* require the other project partner as reviewer;
* prevent self-review.

The manual trigger, typed confirmation, and `main` check remain active even
when these optional controls are unavailable.

GitHub documents current plan availability and behaviour under
[Deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

## Publication procedure

Before starting, merge the intended project state to GitHub `main` and confirm
the required `Checks` jobs pass.

1. Open **Actions → Publish project to GitLab → Run workflow**.
2. Select `main`.
3. Enter `publish project/ to gitlab` exactly.
4. Run the workflow and approve the `gitlab-submission` environment if it has a
   reviewer rule.
5. Inspect the run summary and GitLab `main` after success.

The workflow fetches GitLab `main` over HTTPS, creates a publication merge
whose tree is exactly the verified submission tree, then performs a normal
push. For the known initial repository state, it can bridge a single
`README.md` commit. On later runs it requires the previous publication marker,
unchanged GitLab tree, and descendant subtree history. It fails safely if
validation fails, the secret is missing, TLS validation fails, GitLab rejects
the credential, or GitLab was edited outside this workflow. Resolve the cause;
do not add `--force`.

## Local emergency publication

The repository rules still require explicit human approval immediately before
any local GitLab publication. Once approved, use the same guarded sequence:

```bash
git switch main
git pull --ff-only origin main
cd project && make check && cd ..
./scripts/build_submission.sh
./scripts/verify_submission.sh
git ls-tree -r --name-only submission
git fetch gitlab main
./scripts/create_gitlab_publication_commit.sh \
  submission refs/remotes/gitlab/main gitlab-publication
git push gitlab
```

Never run `git push gitlab main:main`: that would attempt to publish the private
monorepo history and files.
