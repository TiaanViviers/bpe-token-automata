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
* pins the university GitLab SSH host keys in reviewed source;
* uses a dedicated SSH key registered either as a project deploy key or as an
  automation-only key on an authorised student account;
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

Do not reuse a personal SSH key. Generate a dedicated key pair outside this
repository:

```bash
key_dir="$(mktemp -d)"
ssh-keygen -t ed25519 -N '' \
  -C 'github-actions-bpe-token-automata-to-gitlab' \
  -f "${key_dir}/gitlab-actions"
```

Keep that terminal open until both sides are configured.

### 1. Add the public key to GitLab

Prefer a project-scoped deploy key when a Maintainer can configure one:

1. Open the university GitLab project.
2. Go to **Settings → Repository → Deploy keys**.
3. Add a project deploy key named `GitHub Actions publication` using the
   contents of `${key_dir}/gitlab-actions.pub`.
4. Enable **Grant write permissions to this key**.
5. If `main` is protected, allow this deploy key to push to `main`. Do not
   permit force-pushes.

GitLab requires Maintainer or Owner access to create a project deploy key.
See GitLab's official [deploy-key documentation](https://docs.gitlab.com/user/project/deploy_keys/)
for current role, write-access, and protected-branch requirements.

When both students have only Developer access and no project administrator is
available, register the same dedicated public key as an additional key on one
authorised student's GitLab account under **Edit profile → Access → SSH keys**.
Do not reuse that student's everyday laptop key. The automation then has that
student's GitLab permissions, while commit authorship remains embedded in the
original subtree commits.

### 2. Add the private key to GitHub

In the private GitHub repository, go to **Settings → Secrets and variables →
Actions** and create this repository secret:

```text
GITLAB_SSH_PRIVATE_KEY
```

Set its value to the complete contents of `${key_dir}/gitlab-actions`, including
the `BEGIN` and `END` lines. Never commit this value.

Alternatively, store the secret on the `gitlab-submission` environment if the
repository's GitHub plan supports environment secrets for private repositories.

After confirming that GitLab has the public key and GitHub has the private-key
secret, securely remove the temporary key directory. If the secret must later
be rotated, remove the old GitLab key before creating a replacement.

### 3. Configure the optional GitHub environment guard

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

The workflow fetches GitLab `main`, creates a publication merge whose tree is
exactly the verified submission tree, then performs a normal push. For the
known initial repository state, it can bridge a single `README.md` commit. On
later runs it requires the previous publication marker, unchanged GitLab tree,
and descendant subtree history. It fails safely if validation fails, the secret
is missing, the SSH host identity changes, GitLab rejects the credential, or
GitLab was edited outside this workflow. Resolve the cause; do not add `--force`.

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
