# Module 4 Labs: Git, GitHub, and Team Engineering Workflows

Standalone lab handout. The theory these labs depend on is in the Module 4 chapter notes, Part B. Work through the labs in order, because 4C depends on the repository habits from 4A and 4B, and 4D depends on the protection and release automation you build in 4C.

## What you will have built by the end

| Lab | Outcome |
|-----|---------|
| 4A | Two clones, a deliberate merge conflict, and a resolution you can explain |
| 4B | Evidence, in your own terminal, of why `reset` is unsafe on a shared branch and `revert` is not |
| 4C | A repository a professional team could actually work in, where merging a `feat:` commit bumps the version and writes the changelog by itself |
| 4D | One feature traced from epic to production, with every link machine verifiable |

## Prerequisites

* A Fedora, RHEL, or CentOS Stream machine (a disposable VM is ideal, because Lab 4B asks you to break things on purpose).
* Git 2.34 or later. The SSH signing and `switch`/`restore` behaviour in these labs assumes it.
* A GitHub account with SSH authentication working (`ssh -T git@github.com` returns a success message).
* Node.js and npm, for commitlint and husky in Lab 4C.
* Python 3, for the `pre-commit` framework in Lab 4C.
* For Lab 4C step 5 you need a **second GitHub account or a classmate**, because a ruleset requiring one approval means you cannot approve your own pull request. That is the point of the rule, not an obstacle to route around.

```bash
sudo dnf install git gh nodejs python3 python3-pip -y
```
```bash
git --version && gh --version && node --version && python3 --version
```

## A warning about Lab 4B

Lab 4B deliberately rewrites history and throws away commits so you can watch the failure mode with your own eyes and then recover from it. It also shows you what a force push *would* do to a shared branch, without asking you to inflict that on anyone. Do it in the throwaway repository the lab creates, never in a repository anyone else uses. If you find yourself reaching for `git reset --hard` on a shared branch, or typing `--force`, outside this lab, stop and reread section B1 of the notes.

## How these labs are marked

| Weight | Criterion |
|--------|-----------|
| 25% | Lab 4A: conflict caused, resolved, and correctly explained. The explanation of *why the push was rejected* carries more marks than the resolution itself. |
| 25% | Lab 4B: evidence for both paths, plus the written comparison and the message to the colleague. Terminal transcripts, not descriptions of terminal transcripts. |
| 35% | Lab 4C: the repository works end to end. Full marks require the automated version bump and generated changelog, not just the hooks and the ruleset. |
| 15% | Lab 4D: the chain links, and you verified each link rather than asserting it. |

A lab where every check passes on the first try is a lab you have not tested. In 4C especially, you are expected to submit evidence of each guardrail **rejecting** something.

## Common environment setup

Environment for all labs: Fedora, RHEL, or CentOS Stream with `git` 2.34 or later, a GitHub account, and the GitHub CLI.

```bash
sudo dnf install git -y
```
```bash
sudo dnf install gh -y
```
```bash
gh auth login          # choose SSH, and let gh upload a key for you
```
```bash
git --version && gh --version
```

Set the defaults that make the rest of the labs behave predictably:

```bash
git config --global init.defaultBranch main
```
```bash
git config --global pull.rebase false          # explicit merge on pull, no surprises
```
```bash
git config --global push.autoSetupRemote true  # plain `git push` on a new branch just works
```

---

## Lab 4A. The Full Cycle Across Two Clones, Including a Deliberate Merge Conflict

**Goal:** experience the conflict as the two sided event it actually is, rather than as an error message. You will play two developers on one machine by keeping two clones of the same repository.

### 1. Create the repository

```bash
gh repo create module4-lab --public --clone --add-readme
```
```bash
cd module4-lab
```
```bash
git log --oneline
```

### 2. Seed a file that both developers will fight over

```bash
cat > pricing.md <<'EOF'
# Pricing

| Plan | Price |
|------|-------|
| Free | 0     |
| Pro  | 10    |
EOF
```
```bash
git add pricing.md
```
```bash
git commit -m "docs: add initial pricing table"
```
```bash
git push
```

### 3. Make the second clone (this is "Bob")

```bash
cd ..
```
```bash
git clone git@github.com:<your-username>/module4-lab.git module4-lab-bob
```
```bash
ls -d module4-lab module4-lab-bob
```

You now have two independent repositories that happen to share a remote. Treat `module4-lab` as Alice and `module4-lab-bob` as Bob. Open two terminals if that helps you keep them straight.

### 4. Alice branches, edits, and merges cleanly

```bash
cd module4-lab
```
```bash
git switch -c feat/alice-pro-price
```
Change the Pro price to 12:
```bash
sed -i 's/| Pro  | 10    |/| Pro  | 12    |/' pricing.md
```
```bash
git diff                                   # inspect before staging, always
```
```bash
git add pricing.md
```
```bash
git commit -m "feat(pricing): raise Pro plan to 12"
```
```bash
git switch main
```
```bash
git merge feat/alice-pro-price             # fast forward, no conflict
```
```bash
git push origin main
```
```bash
git branch -d feat/alice-pro-price
```

### 5. Bob edits the same line, from a stale base

Bob has **not** pulled. His clone still believes Pro costs 10. This is the entire cause of every merge conflict you will ever have: two people editing the same region from different bases.

```bash
cd ../module4-lab-bob
```
```bash
git switch -c feat/bob-pro-price
```
```bash
sed -i 's/| Pro  | 10    |/| Pro  | 15    |/' pricing.md
```
```bash
git commit -am "feat(pricing): raise Pro plan to 15"
```
```bash
git switch main
```
```bash
git merge feat/bob-pro-price
```
```bash
git push origin main
```

The push is rejected:

```
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'github.com:.../module4-lab.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally.
```

Read that hint carefully. Git is not refusing because you did something wrong. It is refusing because accepting your push would silently discard Alice's commit. This rejection is the feature.

### 6. Cause the conflict

```bash
git pull origin main
```

```
Auto-merging pricing.md
CONFLICT (content): Merge conflict in pricing.md
Automatic merge failed; fix conflicts and then commit the result.
```

Inspect the state:

```bash
git status
```
```bash
cat pricing.md
```

```
| Free | 0     |
<<<<<<< HEAD
| Pro  | 15    |
=======
| Pro  | 12    |
>>>>>>> 1a2b3c4... feat(pricing): raise Pro plan to 12
```

Read the markers precisely, because people misread them constantly:

* Between `<<<<<<< HEAD` and `=======` is **your** side, the branch you are currently on.
* Between `=======` and `>>>>>>>` is **their** side, what you are merging in.
* The label after `>>>>>>>` tells you exactly which commit brought it.

Useful during a conflict:

```bash
git diff --name-only --diff-filter=U      # list only the conflicted files
```
```bash
git log --merge --oneline -p pricing.md   # show only the commits touching the conflict
```
```bash
git checkout --ours pricing.md            # take your side wholesale
git checkout --theirs pricing.md          # take their side wholesale
git merge --abort                         # bail out entirely, no harm done
```

### 7. Resolve it

Git cannot decide whether Pro costs 12 or 15. Only a human with business context can. That is precisely why Git stops. Edit the file, delete all three marker lines, and leave the resolved content:

```bash
vim pricing.md
```
```
| Free | 0     |
| Pro  | 15    |
```
```bash
git add pricing.md                        # staging the file is how you declare it resolved
```
```bash
git status
```
```bash
git commit                                # accept the prepared merge message, or improve it
```
```bash
git push origin main
```

### 8. Prove what happened

```bash
git log --oneline --graph --decorate --all
```

You should see two lines of development converging into a merge commit with two parents. Confirm the merge commit really has two parents:

```bash
git cat-file -p HEAD | head -5            # two "parent" lines
```

Finally, bring Alice's clone back in sync and confirm both clones agree:

```bash
cd ../module4-lab && git pull
```
```bash
git rev-parse main                        # same SHA in both clones
```

**Deliverables:** the output of `git log --oneline --graph --all` from both clones, the conflicted `pricing.md` before resolution, and a two sentence explanation of why the push was rejected in step 5.

---

## Lab 4B. log, diff, stash, rebase, revert, reset, and the Difference That Matters

Work in `module4-lab`. Generate some history first:

```bash
for i in 1 2 3; do echo "line $i" >> notes.txt; git add notes.txt; git commit -m "feat(notes): add line $i"; done
```

### log: asking history questions

```bash
git log --oneline --graph --decorate --all
```
```bash
git log -p notes.txt                   # how this file changed, with diffs
```
```bash
git log --author="Alice" --since="2 weeks ago"    # filter by author; use a name that actually appears in your log (these commits carry your configured name, not "Alice")
```
```bash
git log -S "Pro" --oneline             # commits that added or removed the string "Pro"
```
```bash
git log main..feat/x --oneline         # what is on the branch that is not on main
```
```bash
git blame pricing.md                   # who last touched each line, and in which commit
```

`git log -S` is the one most engineers never learn and then use weekly. It answers "when did this string enter the codebase?"

### diff: comparing the three trees

```bash
git diff                    # working tree vs index    (what you have not staged)
git diff --staged           # index vs HEAD            (what you are about to commit)
git diff HEAD               # working tree vs HEAD     (everything uncommitted)
git diff main..feat/x       # branch tip vs branch tip
git diff main...feat/x      # branch vs their merge base (what the PR actually shows)
```

The two dot versus three dot distinction matters in review. Three dots answers "what did this branch add", which is what a pull request displays. Two dots also includes what `main` moved on to, which is usually not what you meant.

### stash: shelving work you are not ready to commit

```bash
echo "half finished idea" >> notes.txt
```
```bash
git stash push -m "wip: pricing experiment"
```
```bash
git status                  # clean
git stash list
git stash show -p stash@{0}
```
```bash
git stash pop               # reapply and drop
```
```bash
git stash push -u -m "wip: including untracked files"    # -u also stashes untracked files
```

Stash is a stack, not a filing cabinet. Anything you stash for more than a day should have been a commit on a branch. Stashes are invisible to `git log`, do not push, and are the single most common way to lose work.

### rebase: replaying commits onto a new base

```bash
git switch -c feat/rebase-demo
```
```bash
echo "feature work" >> notes.txt && git commit -am "feat(notes): feature work"
```
```bash
git switch main && echo "main moved" >> other.txt && git add other.txt && git commit -m "chore: main moves on"
```
```bash
git switch feat/rebase-demo
```
```bash
git log --oneline --graph --all       # note your branch is behind
```
```bash
git rebase main
```
```bash
git log --oneline --graph --all       # your commit now sits on top of main, with a NEW SHA
```

Record the SHA before and after. They differ. That is the whole point, and the whole danger. Rebase does not move commits, it copies them into new commit objects and abandons the originals.

Interactive rebase, for cleaning a branch before review:

```bash
git rebase -i main            # squash, reword, reorder, drop
```

**The golden rule of rebase:** never rebase commits that other people have already pulled. Rebase your own unpushed branch to keep it tidy. Never rebase a shared branch.

### The main event: reset versus revert

Set up something to undo:

```bash
git switch main
```
```bash
echo "DELETE FROM users;" >> migration.sql
```
```bash
git add migration.sql && git commit -m "feat(db): add cleanup migration"
```
```bash
git push origin main
```
```bash
git log --oneline -3
```

Record the SHA of that commit. Call it `$BAD`.

#### revert: safe on a shared branch

```bash
git revert <BAD>
```
```bash
git log --oneline -3
```
```bash
cat migration.sql
```

Observe carefully:

* The bad commit is **still in history**. Nothing was removed.
* A **new** commit exists on top, whose diff is the exact inverse of the bad one.
* The file content is back to the pre-bad state.
* History moved **forward**, so the push is a fast forward:

```bash
git push origin main          # succeeds, no force required
```

Anyone who already pulled the bad commit simply pulls one more commit. Their history stays consistent with yours. Nothing they have is invalidated.

#### reset: rewrites history, destructive on a shared branch

Now do the same undo the wrong way, so you can see the failure mode with your own eyes.

```bash
echo "DROP TABLE users;" >> migration.sql && git commit -am "feat(db): another bad idea"
```
```bash
git push origin main
```
```bash
git rev-parse HEAD            # note this SHA; the remote now has it too
```
```bash
git reset --hard HEAD~1
```
```bash
git log --oneline -3          # the commit is gone from your history
```
```bash
git push origin main
```

The push is **rejected**. Your branch is no longer a descendant of the remote branch, so the push is not a fast forward. To make it land you would have to force:

```bash
git push --force origin main            # DO NOT DO THIS ON A SHARED BRANCH
```

This is the moment to understand what force push does to your colleagues. The remote's `main` now points at a commit that is **not** in their history. Their next `git pull` produces a merge between the old history and the new one, and the commit you "removed" comes straight back, now duplicated, with conflicts. Someone else pushing before they notice can resurrect it permanently. Any CI, any deployment, any tag pointing at the old SHA now dangles.

Recover, because you can:

```bash
git reflog                                    # find the SHA you "lost"
```
```bash
git reset --hard <sha-from-reflog>            # you are back
```
```bash
git reset --hard ORIG_HEAD                    # shorthand: where HEAD was before the last big move
```

#### The comparison, in one table

| | `git revert` | `git reset` |
|---|---|---|
| What it does | Adds a new commit that inverts an old one | Moves the branch pointer to an older commit |
| History | Preserved. The mistake and the fix are both visible | Rewritten. The commits are orphaned |
| Push | Fast forward, ordinary push | Requires `--force`, rewrites the remote |
| Safe on a shared branch | **Yes** | **No** |
| Safe on your own unpushed branch | Yes, but usually unnecessary | **Yes, this is where it belongs** |
| Effect on colleagues | They pull one extra commit | Their history diverges and they must repair it |
| Audit trail | Complete. You can see what was wrong and when it was fixed | The evidence is deleted, which is exactly what an auditor asks about |

**When to use each, stated as a rule you can apply without thinking:**

* The commit has left your machine, or anyone else might have it: **revert**. No exceptions.
* The commit is local, unpushed, and you want to reshape it before anyone sees it: **reset** (or interactive rebase). This is good practice, not a sin.
* You need to undo a merge that has been pushed: `git revert -m 1 <merge-sha>`, and understand that re-merging that branch later needs care.

### What you say to a colleague who just force pushed to main

This is the professional-communication half of the lab, and it is assessed as such: it maps to **ABET Student Outcome 3, the ability to communicate effectively with a range of audiences.** The technical fix is only half of an incident; the message that contains it, assigns no blame, and keeps a teammate willing to report the next mistake is the other half. Write the message as a graded artifact, not an afterthought.

Not "you idiot." The behaviour is the target, and the process is the actual defendant. Something like this:

> "Heads up, `main` got force pushed about ten minutes ago, so anyone who pulled before that now has a diverged history. Nobody pull or push to main until we sort it. I have the old SHA from my reflog, so I can restore it. Can you tell me what you were trying to undo? If it was that bad migration commit, we should revert it instead, and I will help you do that now."

Structure of that message, and it generalises to every incident you will ever handle:

1. **Contain first.** Tell people to stop pushing before anything else, because every additional push makes recovery harder.
2. **State the effect factually, not the blame.** "History diverged" is a fact. "You broke main" is an accusation, and it makes the next person hide their mistake instead of reporting it.
3. **Say that recovery is possible,** because it almost always is, from any reflog on any clone that had the old commit.
4. **Ask what they were trying to achieve.** Force push is usually the symptom of a legitimate goal reached by the wrong route.
5. **Fix the process, not the person.** The real defect is that `main` accepted a force push at all. That is a missing ruleset, and you fix it in Lab 4C today, not in a retrospective next month.

And one habit that prevents most of this: when you must force push your **own** branch after a rebase, use

```bash
git push --force-with-lease
```

which refuses to overwrite the remote if someone else has pushed since you last fetched. It is the difference between a scalpel and a shotgun. Configure it as a default reflex.

**Deliverables:** terminal transcripts showing (a) the rejected push after `reset`, (b) the successful push after `revert`, (c) `git reflog` output and the recovery, and (d) a `git log --graph` of the final history with your written explanation of which commits are still present in each case and why; plus (e) the reset-versus-revert comparison in your own words, and (f) the message you would send to the colleague who force pushed to `main`.

---

## Lab 4C. A Real Repository: Hooks, Protection, Enforced Commits, Automated Releases

This is the lab that matters. Everything before it was mechanics. This produces a repository that a professional team could actually work in, and the last step is the payoff for all of section B4.

### 1. Create the repository

```bash
gh repo create module4-release-demo --public --clone --add-readme
```
```bash
cd module4-release-demo
```

### 2. A sane .gitignore

Do not write one from memory. Generate it from the canonical source and then add your own entries.

```bash
curl -L -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore
```

Or write one deliberately:

```gitignore
# Build output and dependencies
node_modules/
target/
dist/
build/
*.class

# Environment and secrets. If a secret is ever committed, ignoring it later does nothing.
.env
.env.*
*.pem
*.key
credentials.json

# Editor and OS
.idea/
.vscode/
*.iml
.DS_Store
Thumbs.db

# Logs and local state
*.log
*.tfstate
*.tfstate.backup
.terraform/
```

Two rules that people learn the hard way:

* `.gitignore` only affects **untracked** files. A file already tracked stays tracked. To stop tracking it: `git rm --cached <file>` and commit.
* Ignoring a secret does not unpublish it. If it was ever pushed, **rotate the credential**, then purge it from history with `git filter-repo`. Ignoring it afterwards protects nobody.

```bash
git add .gitignore && git commit -m "chore: add gitignore"
```

### 3. Pre-commit hooks: whitespace, YAML validity, secrets

Install the framework:

```bash
sudo dnf install pre-commit -y      # or: pip install --user pre-commit
```
```bash
pre-commit --version
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict      # blocks committing "<<<<<<<" markers
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: detect-private-key

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

Install the hook into this clone. Note that this step is per clone, because `.git/hooks` is not cloned. Every teammate runs it once.

```bash
pre-commit install                     # writes .git/hooks/pre-commit
```
```bash
pre-commit install --hook-type commit-msg
```
```bash
pre-commit run --all-files             # run everything once, now
```
```bash
git add .pre-commit-config.yaml && git commit -m "ci: add pre-commit hooks"
```

**Prove each hook fires.** A hook you have not seen fail is a hook you do not know works.

Trailing whitespace:
```bash
printf 'hello   \n' > demo.txt && git add demo.txt && git commit -m "test: whitespace"
```
The hook fails, **and fixes the file in place**. Re-add and commit again. That is the normal loop for fixer hooks.

Broken YAML:
```bash
printf 'key: [unclosed\n' > bad.yaml && git add bad.yaml && git commit -m "test: yaml"
```

A secret:
```bash
echo 'aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"' > creds.txt
git add creds.txt && git commit -m "test: secret"
```
Gitleaks blocks the commit. Delete the file, do not try to make it pass.

Then remind yourself of the limit:
```bash
git commit --no-verify -m "test: bypassed"     # every hook skipped
```
That command is why CI has to run the same checks. Mirror them:

```yaml
# .github/workflows/checks.yml
name: checks
on:
  pull_request:
  push:
    branches: [main]
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pre-commit
      - run: pre-commit run --all-files
```

### 4. Conventional commits enforced with commitlint

```bash
npm init -y
```
```bash
npm install --save-dev husky @commitlint/cli @commitlint/config-conventional
```
```bash
npx husky init
```
```bash
echo "module.exports = { extends: ['@commitlint/config-conventional'] };" > commitlint.config.js
```
```bash
echo 'npx --no -- commitlint --edit "$1"' > .husky/commit-msg
```
```bash
chmod +x .husky/commit-msg
```

Note for husky v9: `npx husky add` was removed. You write the hook file yourself, as above, and `npx husky init` adds the `"prepare": "husky"` script to `package.json` so that hooks install automatically for everyone who runs `npm install`.

Prove it works:

```bash
git commit --allow-empty -m "updated stuff"
```
```
✖   subject may not be empty [subject-empty]
✖   type may not be empty [type-empty]
✖   found 2 problems, 0 warnings
```
```bash
git commit --allow-empty -m "chore: verify commitlint"     # passes
```
```bash
git add -A && git commit -m "ci: enforce conventional commits with commitlint"
```

If your team squash merges, also lint the PR title, because that title is what becomes the commit on `main`.

### 5. Branch protection with a ruleset

Do it in the UI once so you see the options (Settings, Rules, Rulesets, New branch ruleset), then learn the API call, because in a platform role you will be creating these across dozens of repositories and clicking does not scale.

Required for this lab, targeting `main`:

* Require a pull request before merging, 1 approval.
* Dismiss stale pull request approvals when new commits are pushed.
* Require status checks to pass, select the `pre-commit` check, and require the branch to be up to date.
* Require linear history.
* Block force pushes.
* Restrict deletions.
* Bypass list: empty.

The same thing as code:

```bash
gh api -X POST repos/:owner/:repo/rulesets \
  -f name='main protection' \
  -f target='branch' \
  -f enforcement='active' \
  -f 'conditions[ref_name][include][]=~DEFAULT_BRANCH' \
  -f 'rules[][type]=deletion' \
  -f 'rules[][type]=non_fast_forward' \
  -f 'rules[][type]=required_linear_history' \
  -f 'rules[][type]=pull_request' \
  -F 'rules[][parameters][required_approving_review_count]=1' \
  -F 'rules[][parameters][dismiss_stale_reviews_on_push]=true'
```
```bash
gh api repos/:owner/:repo/rulesets | jq '.[].name'
```

Now prove the protection is real:

```bash
git switch main
```
```bash
git commit --allow-empty -m "chore: try to push straight to main"
```
```bash
git push origin main
```
```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - Changes must be made through a pull request.
```

That rejection is the deliverable. A protection you have not tried to violate is a protection you have not tested.

### 6. Wire up release-please

Create `.github/workflows/release-please.yml`:

```yaml
name: release-please
on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node       # or: simple, python, java, terraform-module, and others
```

`release-type: simple` is the right choice if you have no language manifest to bump and you just want a `CHANGELOG.md`, a version file, and a tag.

Commit it through a pull request, because you just made direct pushes to `main` impossible:

```bash
git switch -c ci/release-please
```
```bash
git add .github/workflows/release-please.yml
```
```bash
git commit -m "ci: add release-please"
```
```bash
git push -u origin ci/release-please
```
```bash
gh pr create --fill
```
```bash
gh pr merge --squash --auto        # merges once the checks pass and a review lands
```

### 7. Cash it in

This step is the point of the entire lab. Ship a feature, using a conventional commit, and change nothing else.

```bash
git switch main && git pull
```
```bash
git switch -c feat/greeting
```
```bash
echo 'module.exports = () => "hello";' > index.js
```
```bash
git add index.js
```
```bash
git commit -m "feat: add greeting module"
```
```bash
git push -u origin feat/greeting
```
```bash
gh pr create --fill && gh pr merge --squash --auto
```

Within a minute of that merge, release-please opens a **Release PR** on its own. Look at what it wrote without being asked:

* `CHANGELOG.md`, with a `### Features` heading and your commit under it, linked to the commit and the PR.
* The version bumped from `0.1.0` to `0.2.0`, because `feat:` maps to a minor bump.
* A title such as `chore(main): release 0.2.0`.

Merge the Release PR:

```bash
gh pr list
```
```bash
gh pr merge <release-pr-number> --squash
```
```bash
git pull && git tag --list
```
```bash
gh release list
```

A git tag `v0.2.0` and a GitHub Release with generated notes now exist. Nobody typed a version number. Nobody wrote a changelog. Nobody remembered to tag.

Now prove the mapping in the other direction:

```bash
git switch -c fix/typo && echo '// fix' >> index.js
git commit -am "fix: correct greeting output"
```
Merge that, and the Release PR proposes **0.2.1**, a patch.

```bash
git switch -c feat/breaking
git commit --allow-empty -m "feat!: rename greeting export

BREAKING CHANGE: consumers must import { greet } instead of the default export."
```
Merge that, and the Release PR proposes **1.0.0**, a major.

**That is the payoff.** The commit format was never bureaucracy. It was the input to a machine that now does version management, changelog writing, tagging, and release notes for free, forever, and never forgets.

**Deliverables:** the repository URL, a screenshot of the failed direct push to `main`, a screenshot of gitleaks blocking a commit, a screenshot of commitlint rejecting a bad message, the auto generated `CHANGELOG.md`, and the release list showing 0.2.0, 0.2.1, and 1.0.0.

---

## Lab 4D. One Feature from Backlog to Production

**Goal:** build the traceability chain from section B7 and then verify every link in it.

Work in the `module4-release-demo` repository from Lab 4C. This lab depends on the branch protection and the release-please automation you wired up there, because the last link in the chain is the changelog entry that release-please generates on merge. The project board you create below sits at your account level, but every issue, branch, and pull request lives in that repository.

### 1. Create a project board

```bash
gh project create --owner "@me" --title "Module 4 Sprint Board"
```
```bash
gh project list --owner "@me"
```

In the browser, open the project and configure it as a working board rather than a decorative one:

* Add a **Status** field with Todo, In Progress, In Review, Done.
* Add an **Iteration** field named Sprint, two week duration. This is your sprint.
* Add an **Estimate** number field.
* Switch to the Board layout, grouped by Status.
* Under Workflows, enable **Item added to project** set to Todo, **Item closed** set to Done, and **Pull request merged** set to Done. Now the board maintains itself, which is the only kind of board that stays accurate.

### 2. Write the epic

Create an issue with the Feature issue type (Issues, New issue, then set Type):

**Title:** Users can check out with a saved payment card

**Body:**
```markdown
## Outcome
A returning user completes a purchase without re-entering card details.

## Why
Card re-entry is the largest drop-off step in the funnel.

## Scope
In: saved card selection, CVV re-verification, receipt email.
Out: new payment providers, refunds, subscriptions.

## Done when
All sub-issues are closed and a user can complete a purchase in staging
using a saved card, with the receipt delivered.
```

### 3. Break it into stories as sub-issues

Open the epic, find the **Sub-issues** section, and create three. Do not use the old tasklist syntax, it was retired in April 2025 and will render as plain text.

Story 1:
```markdown
As a returning user, I want to select a saved card at checkout,
so that I do not re-enter my card number.

## Acceptance criteria
- [ ] Saved cards are listed, showing brand and last four digits only.
- [ ] Selecting a card populates the payment step.
- [ ] A user with no saved cards sees the existing manual entry form.
- [ ] No full PAN is ever sent to the client or written to a log.
```

Story 2: CVV re-verification on a saved card.
Story 3: Receipt email after a saved card purchase.

The epic now shows a progress bar, 0 of 3, and it rolls up automatically as the children close. Add all four issues to the project board, put the three stories into the current Sprint iteration, and estimate them.

From the terminal, if you prefer. Save each story's body to a file first (for example, paste Story 1's text into `story1.md`), or replace `--body-file story1.md` with an inline `--body "..."`:

```bash
gh issue create --title "Select a saved card at checkout" --body-file story1.md --label enhancement
```
```bash
gh issue list
```
```bash
gh project item-add <project-number> --owner "@me" --url <issue-url>
```

### 4. Start the sprint and take a story

Move story 1 to In Progress. Assign it to yourself. Note its number, say `#4`.

Now build the chain. Every link is deliberate.

**Link one, the branch carries the issue number:**
```bash
git switch main && git pull
```
```bash
git switch -c feat/4-saved-card-selection
```

**Link two, the commit references the issue:**
```bash
echo "// saved card selector" > checkout.js
```
```bash
git add checkout.js
```
```bash
git commit -m "feat(checkout): list saved cards at payment step

Shows brand and last four digits only. Full PAN never leaves the vault.

Refs: #4"
```
```bash
git push -u origin feat/4-saved-card-selection
```

Open the issue in the browser. The commit already appears in the issue timeline, because Git referenced it. No manual linking.

**Link three, the pull request closes the issue:**
```bash
gh pr create --title "feat(checkout): list saved cards at payment step" \
  --body "Implements the saved card selector.

Closes #4"
```

The keyword `Closes #4` matters. A bare `#4` links but does not close. Open the PR and confirm the sidebar now reads **Linked issues: #4**, and the board card for the PR appeared in In Review if you configured that workflow.

### 5. Review, merge, and watch the chain complete

```bash
gh pr view --web
```

Get a review (a classmate, or a second account, since a ruleset requiring one approval means you cannot approve your own PR, which is exactly the point). Then:

```bash
gh pr merge --squash
```

Now verify, one link at a time. This verification **is** the lab. Anyone can build the chain, an engineer proves it.

| Link | How you verify it |
|---|---|
| Issue closed automatically | Open issue #4. It is Closed, and the timeline says the PR closed it. Nobody clicked Close. |
| Board updated automatically | The card for #4 moved to Done. Nobody dragged it. |
| Epic progress rolled up | The epic now reads 1 of 3 complete. |
| Commit points to the issue | `git log --oneline` on main, then open the commit. The `Refs: #4` links back. |
| Issue points to the commit | The issue timeline lists the commit and the PR. |
| Release notes point to both | Merge the release-please Release PR from Lab 4C. The changelog entry for this feature links to the PR, which links to the issue, which links to the epic and its acceptance criteria. |

### 6. The point of all of it

Six months from now, a production incident traces back to one line in `checkout.js`. You run:

```bash
git blame checkout.js
```
```bash
gh pr list --search <commit-sha>
```

Commit, then PR, then issue, then acceptance criteria, then the discussion where somebody explained why the CVV is re-verified. Ninety seconds, no archaeology, no interviewing people who have left the company.

That is the deliverable of this entire module, and it is the difference between a repository and an engineering organisation.

**Deliverables:** the project board URL, the epic showing 1 of 3 sub-issues complete, the closed issue with the auto-close event visible in the timeline, the merged PR, and the changelog entry that links back to it.

---

## Submission checklist

Bundle the following into a single markdown file or PDF, with your repository URLs at the top.

**Lab 4A**
- [ ] `git log --oneline --graph --all` from both clones, showing the merge commit
- [ ] The conflicted `pricing.md` with the markers still in it
- [ ] Two sentences on why the push in step 5 was rejected

**Lab 4B**
- [ ] Transcript of the rejected push after `git reset --hard`
- [ ] Transcript of the successful, non forced push after `git revert`
- [ ] `git reflog` output and the recovery command that restored the lost commit
- [ ] The reset versus revert comparison in your own words
- [ ] The message you would send to a colleague who force pushed to `main`

**Lab 4C**
- [ ] Repository URL
- [ ] Gitleaks blocking a commit
- [ ] commitlint rejecting a malformed commit message
- [ ] The ruleset rejecting a direct push to `main` (`GH013`)
- [ ] The release-please Release PR
- [ ] The generated `CHANGELOG.md`
- [ ] `gh release list` showing 0.2.0 (feat), 0.2.1 (fix), and 1.0.0 (feat!)

**Lab 4D**
- [ ] Project board URL, with the Iteration field configured
- [ ] The epic showing 1 of 3 sub-issues complete
- [ ] The merged pull request
- [ ] The issue closed by the merge, with the auto close event visible in its timeline
- [ ] The changelog entry that links back through the PR to the issue
