# Module 4: Git, GitHub, and Team Engineering Workflows

**Structure of this chapter**

* **Part A: Git Fundamentals.** The original chapter, retained in full: concepts, the object model in practice, core commands, history, undoing changes, hooks, `.gitignore`, collaboration, GitHub setup, SSH and HTTPS authentication, branching, cloning, troubleshooting.
* **Part B: Team Engineering Workflows.** New theory: the distributed mental model, branching strategies and their trade offs, pull requests and code review (including review of generated code), conventional commits and the release automation they unlock, pre-commit hooks, signed commits and rulesets, issue tracking and traceability.
* **Part C: Labs 4A to 4D.** Merge conflicts across two clones; log, diff, stash, rebase, revert, reset, with evidence; a fully configured real repository ending in automated releases; and one feature traced from backlog to production.
* **Appendix A: Complete Git and GitHub Worked Example.** The original end to end walkthrough, retained in full.
* **Appendix B: Fact Check and Corrections.** What has changed upstream, and the errata to apply when teaching Part A and Appendix A.

---

# Part A: Git Fundamentals

# Git - Version Control System (with GitHub)

This note consolidates core Git concepts, practical workflows, and GitHub usage with clear commands and examples. Code and command snippets are in triple fences.

---

## Core Git Concepts

- Repository (Repo)
  - A database storing project files with complete version history (commits, branches, tags).
  - Example: A photo album with every picture plus a logbook of all edits.

- Commit
  - A unique snapshot of the repo at a point in time (hash ID, author, timestamp, message).
  - Example: A dated logbook entry: “Added 3 beach photos, cropped group shot.”

- Branch
  - A movable pointer to a commit; the default branch is typically main (formerly master).
  - Example: A bookmark labeled “Wedding Experiment edits.”

- Merge
  - Combines histories by creating a new merge commit (or fast-forward when possible).
  - Example: Paste the best experimental photos into the main album and note the merge.

- Clone
  - Copies the entire repository database (files, history, branches) to your machine.
  - Example: Duplicating the album and its full edit history at home.

- Remote
  - Named reference (e.g., origin) to a shared repo URL (GitHub/GitLab/Bitbucket).
  - Example: Address label for the family’s cloud album.

- Push
  - Uploads local commits to a remote repo branch; can fail if remote has new commits.
  - Example: Shipping new prints to update the cloud album.

- Pull
  - Downloads remote changes and merges into your local branch (git pull = fetch + merge).
  - Example: Getting Aunt Lisa’s new photos and adding them locally.

- Pull Request (PR) / Merge Request (MR)
  - Platform feature (not Git) for review, tests, discussion, and merging.
  - Example: “Merge my beach-photos branch into main (see diffs here).”

- Fork
  - Server-side copy of another user’s repository under your account (platform feature).
  - Example: Your own cloud album copied from Grandma’s recipe book to tweak safely.

- Conflict
  - Happens during merge/rebase when the same lines change incompatibly.
  - Example: You and your brother wrote different captions on the same photo.

- .gitignore
  - Plain text patterns for files/dirs Git should ignore permanently.
  - Example: “Do not include blurry photos or receipts.”


**Platform-Specific Terms**

- Issue/Ticket:
    A trackable discussion unit for bugs, tasks, or enhancements (with labels/assignees).
- Example:
    A shared to-do list: "Task #12: Scan Mom's wedding photos (priority: high)".
- README.md:
- Fact:
    The first file displayed in a repo (supports Markdown formatting).
- Example:
    Album cover + table of contents: "Summer 2025 - Beach Trip (Pages 1-20)".

---

## Introduction to Git & GitHub

- What is Git?
  - Distributed version control system to track changes, enable collaboration, and work offline.
  - Tracks code changes (history, authorship, timelines).
  - Enables conflict-free collaboration (no overwriting others' work).
  - Runs locally (commit, branch, merge offline).

- What is GitHub?
  - Cloud platform hosting Git repositories and providing:
    - Pull Requests (code review + merge)
    - Issues (bug/feature tracking)
    - CI/CD integrations (e.g., Actions)
    - Project boards, wikis, automation


### Git vs. GitHub

| Aspect            | Git (VCS)                                   | GitHub (Platform)                              |
|-------------------|----------------------------------------------|------------------------------------------------|
| Type              | Distributed Version Control System           | Cloud-based Git hosting platform               |
| Function          | Tracks code changes locally                  | Hosts remote repositories                      |
| Installation      | Required (local CLI)                         | Not required (web UI), optional CLI            |
| Internet Needed?  | No (for local work)                          | Yes (for collaboration)                        |
| Core Features     | Commits, branches, merging, history          | PRs, Issues, CI/CD, Wikis, Actions             |
| Ownership         | Open-source (Linus Torvalds)                 | Microsoft-owned                                |
| Analogy           | Personal notebook (drafts)                   | Shared library (publishing/collaboration)      |

---

## How Git Works (with GitHub)

```
+---------------+    +---------------+    +--------------------+    +---------------------+
| Working Tree  |    | Staging Area  |    | Local Repository   |    | Remote Repository   |
+---------------+    +---------------+    +--------------------+    +---------------------+
       |                    |                    |                          |
       | git add/mv/rm      |                    |                          |
       +------------------->|                    |                          |
       |                    | git commit         |                          |
       |                    +------------------->|                          |
       |                    |                    | git push                 |
       |                    |                    +------------------------->|
       |                    |                    |                          |
       |                    |                    |<-------------------------+
       | git reset <file>   |                    |          git fetch       |
       |<-------------------+                    |                          |
       | git reset <commit> |                    |                          |
       |<----------------------------------------+                          |
       | git diff           |                    |                          |
       |<------------------>|                    |                          |
       | git diff HEAD      |                    |                          |
       |<--------------------------------------->|                          |
       |                    |                    |                          |
       |<------------------------------------------------------------------+|
       |  git clone/pull                                                    |

```

- Working Directory (Your Project Workspace)
  - Your local project folder where files are edited.
  - Changes are untracked or modified until staged.
  - Example:
      Editing index.html
        → Git sees this as an "unsaved draft"

- Staging Area (Preparation Zone)
  - Loading dock between working directory and repository.
  - Selectively choose which changes to include in the next commit.
  - Use git add <file> to move changes here
  - Analogy:
      Like packing selected items into a box before shipping (committing)

- .git Directory (Git’s Database)
  - Hidden folder storing committed snapshots, history, branches, tags, and configs.
  - Analogy:
      A vault storing all versions of your project

- Remote Repositories (Team Collaboration Hub)
  - Centralized versions hosted online (GitHub, GitLab).
  - Used for syncing via push/pull; enables collaboration and backups.
  - Acts as a backup in case of local failure.
  - Analogy:
      A shared cloud drive for the team’s project versions.

---

## Core Workflows: Committing changes, Branching, Merging, and Remotes

### Committing Changes (Saving Revisions)
- Creates a revision snapshot with metadata (author, timestamp, message).
- Analogy: Like saving game progress → each commit is a restore point
- Two-step process:
  - git add: Stages changes from the working directory to the staging area
  - git commit: Permanently saves staged changes to the local repository
    
  - Stage changes
```
  git add <file>         #stage a file
```
```
  git add .              #stage everything
```

- Commit staged changes
```
  git commit -m "feat: add price range filter"
```

### Branching (Parallel Development)
- Creates independent lines of development without affecting the main code
- Commands:
  - git branch <name>           #Creates new branch
  - git switch <branch>         #Moves between branches
- Example:
    Create a new-feature branch
        Develop freely
          Switch back to the main anytime
          
- Why use?:
    Test ideas/fixes safely in isolation

```
  git branch <name>      # Create branch
```
```
  git switch <name>      # Switch to branch (modern)
```
  or
```
  git checkout <name>    # Older equivalent
```

Example:
```
git switch -c new-feature
```

...edit files...

```
git commit -m "feat: implement new feature"
```
```
git switch main
```

### Merging (Combining Work)
  - Integrates changes from one branch into another
  - Workflow:
    - git switch main (move to target branch)
    - git merge new-feature (pull changes into target)
  - Preserves the full history of both branches
  - Analogy:
        Merging highway lanes
          Combining separate development paths

- Move to the target branch and merge the source branch:
```
  git switch main
```
```
  git merge new-feature
```

### Remotes (Team Collaboration)
- Shared repositories hosted online (GitHub/GitLab/Bitbucket)
- Operations:
  - git push
      Uploads local commits to remote
  - git pull
      Downloads remote changes to the local
- Enables distributed version control
- Backup against local data loss
- Real-time team synchronization
- Analogy: Central cloud storage for team projects

- Push and pull:
```
  git push origin main
```
```
  git pull origin main
```

- Set default pull behavior (optional):
```
  git config --global pull.rebase true             #or false, or 'only'
```

---

## Common Git Commands

git init (Initialize Repository)
- Sets up a new Git repository in your current directory
- Creates a hidden .git folder to store version history/config
- When to use: Starting a brand-new project from scratch
- Example: 
```
  git init                                            #Ready for version control
```

git clone (Copy Repository)
- Creates a full local copy of a remote repository
- Copies all code, branches, and commit history
- Automatically sets up remote tracking (origin)
- When to use: Joining an existing project hosted online
- Example:
```
  git clone https://github.com/user/project.git
```
```
  git clone git@github.com:user/project.git
```

git add (Stage Changes):
- Moves file changes from the working directory to → staging area
- Selects which modifications to include in the next commit
- Options:
  - git add file.txt (specific file)
  - git add . (all changed files)
- Analogy: Putting items in a "shopping cart" before checkout (commit)

git commit (Save Snapshot):
 - Permanently saves staged changes to the local repository
 - Creates a new commit with ID, message, author, and timestamp
 - Essential flag: -m "Message" (e.g., git commit -m "Fix login bug")
 - Why: Creates restore points in project history

git push (Upload Changes):
 - Sends local commits to remote repository (e.g., GitHub)
 - Updates remote with your latest work
     Syntax: git push <remote> <branch> (e.g., git push origin main)
 - Critical for: Sharing code with team/backing up work

git pull (Download Updates)
- Fetches latest changes from remote → merges into local branch
- Equivalent to git fetch + git merge
     Syntax: git pull <remote> <branch> (e.g., git pull origin dev)
- Critical for: Staying synced with team changes

Status and diff:
```
  git status
```
```
  git diff
```
```
  git diff --staged
```

Branch management:
```
git branch
```
```
git branch -vv
```
```
git switch -c feature/login
```
```
git switch main
```
```
git branch -d feature/login
```

Remote management:
```
git remote -v
```
```
git remote add origin git@github.com:techgeek68/JavaApp.git
```
```
git remote remove origin
```

Log/history:
```
git log --oneline --graph --decorate --all
```
```
git log -- filename                                    #File-specific history
```
```
git log --author="Name"                                #Commits by specific person
```
```
git log --since="2024-01-01" --until="2024-12-31"      #Date range
```
```
git log --grep="search term"                          #Commits containing keywords
```

Tagging (releases):
```
git tag v1.0.0
```
```
git push origin v1.0.0
```

Stash (shelve work-in-progress):
```
git stash push -m "WIP: refactor service"
```
```
git stash list
```
```
git stash pop
```

Cleanup local stale remote branches:
```
git fetch --prune
```

---

## History & Version Tracking

View history:
```
git log --oneline
```

Compare versions:
```
  git diff                                      #Unstaged vs. last commit
```
```
  git diff --staged                             #Staged vs. last commit
```
```
  git diff branch1..branch2                     #Compare two branches
```
```
  git diff commitA..commitB                     #Compare historical snapshots
```

---

## Undoing / Reverting Changes

**Case 1: Edited but NOT staged**:
Changes made in a code but not added into the staging area.

Syntax:
```
  git restore <file>                        #Modern, safer
```
```
git checkout -- <file>                      #Older syntax
```

Example:
```
cd ~/javaapp/sample-app
```
```
mkdir paymentgateway && cd paymentgateway
```
```
vim paymentgatewaycode
```
```
<h1> Select Payment System </h1>        #Integrating multiple payment system
```
```
cd ..
```
```
git status
```
```
git add paymentgatewaycode
```
```
cd paymentgateway
```
```
vim paymentgatewaycode
```
```
<h1> You are selecting Esewa </h1>          #Integrating Esewa
```

Undo changes (modern, unambiguous even if a branch shares the name):
```
git restore paymentgatewaycode
```
```
git checkout -- paymentgatewaycode        #Older equivalent; the -- avoids branch ambiguity
```

Verify:
```
cd paymentgateway
```
```
cat paymentgatewaycode
```

**Case 2: Staged but NOT committed**:
Changes made in a code & added into the staging area.

Syntax: 

**Older:**
Unstage changes for <file_name> from the index (staging area), but keep the changes in your working directory.
```
  git reset HEAD <file_name>
```

Restore <file_name> in your working directory to its last committed state (from HEAD).
Note: In newer versions of Git, git restore <file> is preferred.
```
  git checkout <file_name>
```

**Newer**
Unstage <file>: Removes <file> from the staging area, but keeps your local changes.
```
  git restore --staged <file>     #Unstage (keep working copy)
```

Discard changes in <file> in your working directory and restore it to the latest committed version (HEAD).
```
  git restore <file>              #Discard working changes if desired
```

Example:
```
cd ~/javaapp/sample-app
```
```
mkdir cart && cd cart
```
```
vim cart
```
```
<h1> Select item</h1>            #Cart management
```
```
→ cd ..
→ git add cart
→ git commit -m “cart management system deployed”
```

Edit and add again:
```
vim cart
#Cart management
<h1> select item </h1>
<h2> select paymentgateway </h2>
```

```
cd ..
git status
git add cart
```

```
git reset HEAD cart
git checkout cart
```

Verify:
```
cat cart/cart
```

**Case 3: Already committed**
Changes made in a file and added to the staging area are also committed
to the local repository. (File already in the local repository)

- Method A: Soft reset (keep changes staged)
```
git reset --soft HEAD~1
```

- Method B: Mixed reset (default; keep changes in working copy, unstaged)
```
git reset --mixed HEAD~1
```

- Method C: Hard reset (discard commit and changes; destructive)
```
git reset --hard HEAD~1                            #Warning: Permanently removes work
```

- Method D: Revert (safe on shared branches; creates an “anti-commit”)
```
git log                                            #find commit hash
```
```
git revert --no-commit <commit_hash>
```
```
git commit -m "revert: undo <short-hash> <original subject>"
```

Example:
1. Commit a file
```
mkdir shipping && cd shipping && touch shipping
```
```
echo "Express Delivery" > shipping
cd ..
git add shipping
git commit -m "Added Shipping Module"
```

2. Make unwanted changes and commit
```
echo "Priority Shipping" >> shipping/shipping
git add shipping
git commit -m "Update Shipping Options"
```

3. Undo the commit (two methods)
Method A: Soft reset (keep changes in staging)
```
git reset --soft HEAD~1 #Undo last commit, keep changes staged
```

Method B: Undo the last commit (and also unstage the changes)
```
git reset --mixed HEAD~1
```

Method C: Hard reset (completely discard commit)
```
git reset --hard HEAD~1                     #Permanently remove last commit
```
Warning: This deletes your latest commit and file changes

Method D: Revert the commit by creating a new opposite commit (Recommended)
To view the last few commit hashes:
→ git log
→ Identify the commit

<img width="416" height="221" alt="Screenshot 2025-09-27 at 1 21 39 PM" src="https://github.com/user-attachments/assets/15d16941-95d9-4751-add2-8bb748bc5e67" />

- Copy the <commit_hash>

Syntax
```
git revert --no-commit <commit_hash>    #Stages the inverse of the commit but does NOT commit yet
```
```
git commit -m "revert: undo <short-hash> <original subject>"   #Mandatory follow-up to finish the revert
```
Note: plain `git revert <commit_hash>` (without `--no-commit`) stages and commits the inverse in one step, and is what most people want.

Example:
```
git revert --no-commit 4e772d533db53efec66f03a37e3cdfeda31787cd
```
```
git commit -m "revert: undo 4e772d5 express delivery"
```

Verify:
  ```
  git log                    #Last commit removed
  ```
  ```
  cat shipping/shipping      #Shows only "Express Delivery"
  ```
---

**Customizing Git**

Configuration levels:
```
git config --local          #repo-specific (.git/config)
```
```
git config --global         #user-wide (~/.gitconfig)
```
```
git config --system         #machine-wide
```

Common settings:
```
git config --global user.name "techgeek68"
```
```
git config --global user.email "pyakurelelx@gmail.com"
```
```
git config --global core.editor "vim"
```
```
git config --list
```

Aliases (append to ~/.gitconfig):

Visual history
```
  lol = log --oneline --graph --decorate --all
```
Delete merged local branches (except main)
```
  cleanup = "!git branch --merged | egrep -v '\\*|main|master' | xargs -r git branch -d"
```

**Hooks**:

Hooks are scripts that run at specific points in the Git workflow, allowing automation. Common hooks are:

- pre-commit: Runs when you execute `git commit`, before the commit message editor opens. It lets you automate checks (formatting, linting, secret scanning, tests) so problems are caught before the commit is created. Aborting it aborts the commit. location: .git/hooks/pre-commit

- pre-push: Runs when you execute `git push`, before objects are sent to the remote. Useful for a fast test subset or build check before your work leaves the machine. location: .git/hooks/pre-push

- post-receive: Runs on the remote repository after a push is received. Often used to trigger deployment, notifications, or CI jobs.

Summary:
- automation triggers in .git/hooks/
- pre-commit: run linters/test
- pre-push: run smoke tests
- post-receive: deploy on server

---

## Ignoring Files (.gitignore)

- Exclude temporary files, dependencies, secrets.

Example .gitignore:
```
# Dependencies
node_modules/
.venv/
venv/
target/
dist/
*.class
```
```
# OS
.DS_Store
Thumbs.db
```
```
# IDE
.idea/
*.iml
.vscode/
```
```
# Logs and env
*.log
.env
.env.*
```

---

## Git Best Practices

- Descriptive commit messages (Conventional Commits style)
```
<type>:<subject>            #e.g. feat: add user registration
<Blank Line>
<body>                      #Explain why, not what(if complex)
```
Rules:
- Imperative mood (“Fix bug”, not “Fixed bug”)
- One logical change per commit
- Reference issues/PRs when relevant (e.g., “fix: resolve NPE (#42)”)

- Frequent, small commits
- Regular synchronization
  - Pull before work; push after meaningful commits
  - Resolve conflicts promptly
- Strategic branching
  - main: production-ready
  - develop: integration (if using GitFlow)
  - feature/*, bugfix/*, hotfix/*
  - Delete merged branches (git branch -d featureX)

---

## Collaboration Example (3 Developers)
The diagram illustrates the core workflow of version control systems (VCS) like Git, emphasizing how changes move between three key areas: the Working Copy, Local Repository, and Remote Repository.

Scenario: Alice (frontend), Bob (backend), Carol (UI) collaborate on an e-commerce site.

```
                  +------------------+
User 1:           |  Working Copy    |  
Alice             +------------------+
                        | ^ 
               Commit   | | Update
                        v |
                +------------------+
                | Local Repository |
                +------------------+
                        | ^
                 Push   | | Pull
                        v |
          +---------------------------------------+
          |   Remote Repository                   |
          |      (git)                            |
          +---------------------------------------+
                ^ |                       ^ |
          Push  | | Pull                  | | Push/Pull
                | v                       | v 
            +------------------+      +------------------+
            | Local Repository |      | Local Repository |  
            +------------------+      +------------------+
                   ^ |                          ^ |
            Commit | | Update            Commit | | Update
                   | v                          | v
            +------------------+      +------------------+
User 2:     |  Working Copy    |      |  Working Copy    |  User 3:
Bob         +------------------+      +------------------+  Carol

```

**Workflow & Key Components:**

Working Copy
- Your local project files (editable directly).
- Example: Editing code in Visual Studio Code on your laptop.

Commit Update → Local Repository
- Save changes from the Working Copy to your Local Repository as a versioned "snapshot."
- Example: After fixing a bug, you run git commit -m "Fix login error" to save it
locally.

Push Pull → Remote Repository
- Push: Upload commits from Local Repository to a shared Remote Repository (e.g., GitHub).
- Example: Use git push to share your bug fix with teammates.
- Pull: Download changes from Remote Repository to Local Repository + Working Copy.
- Example: Use git pull to get a teammate's latest feature from GitHub.

Remote Repository
 - Central cloud-hosted storage (e.g., GitHub/GitLab).
 - Example: A GitHub repo like https://github.com/yourteam/project.

Synchronization Cycle
- Changes loop between developers' local environments and the shared remote
repo.


**Developer 1: Alice (Frontend Developer)**
• Task: Add product filtering feature
Workflow:
```
git pull origin main                              #Syncs with remote
```
*Edits product-list.js (Working Copy)*
```
git add product-list.js                           #Stages changes
```
```
git commit -m "feat: add price range filter"      #Saves to local repository
```
```
git push origin main                              #Uploads to remote repository
```

**Developer 2: Carol (UI Designer)**
• Task: Improve cart styling
Workflow:
```
git fetch origin                                  #Checks remote changes
```
*Edits styles.css* (Working Copy)
```
git add styles.css
```
```
git commit -m "feat: redesign cart UI"            #Local Repository
```
```
git push origin main                              #Remote Repository (Pushes before Bob)
```

**Developer 3: Bob (Backend Developer)**
• Task: Implement coupon code validation
Workflow:
```
git pull origin main                              #Gets Alice's updates
```
*Edits checkout.php*  (Working Copy)
```
git add checkout.php
```
```
git commit -m "feat: add coupon validation"       #Local Repository
```
```
git push origin main                              #Remote Repository
```
**Push fails (remote has newer commits)**         #⚠️ Push fails! (Carol pushed first)
```
git pull --rebase origin main                      #Integrates Carol's changes
```
**resolve conflicts (e.g., styles.css), then:**
```
git add styles.css
```
```
git rebase --continue                               #Complete rebase
```
```
git push origin main                                #Success!
```

Why this works:
- Parallel development on separate files

- Conflict managed explicitly via rebase
  - Carol pushes first → Creates new base version
  - Bob uses rebase to replay his changes on top
  - Explicit conflict resolution ensures code integrity
  
- Clear audit trail: v1 (Alice) → v2 (Carol) → v3 (Bob)
  - GitHub shows the exact conflict resolution point

---

## Sign Up for GitHub

- Visit [Visit GitHub](https://github.com) → “Sign up”
- Enter email, password, username, and follow prompts.

---

## Create a Repository on GitHub

- Click “New”
- Name: JavaApp                 (Optionally PythonApp, PHPapp as your required)
- Choose Public/Private
- Add README
- Default branch: main (GitHub default)
- Create repository

---

## Install Git and Perform Core Operations (On Developer's Machine)

Install Git (RHEL/Fedora/CentOS):
```
  sudo dnf install git -y
```

Configure global identity:
```
  git config --global user.name "techgeek68"
```
```
  git config --global user.email "pyakurelelx@gmail.com"
```
```
  git config --global core.editor "vim"
```
Verify:
```
  git config --list
```

**Create a local repo:**
```
  mkdir -p ~/javaapp && cd ~/javaapp
```
```
  git init
```

If you already have a Maven sample app:
```
cd ~/javaapp/sample-app
```

If not, create your Maven project:
```
mvn archetype:generate -DgroupId=com.example -DartifactId=sample-app -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false
cd sample-app
```

*Remove unnecessary build artifacts (#Delete unnecessary directory like target created by 'maven' package’*

```
rm -rf target
```

*Then, you can initialize Git and start tracking files as needed:*
```
git init
```
```
ls -a
```
```
git add .
```
```
git commit -m "Initial commit"
```

**Stage and commit:**
```
git status
```
It will give us about:
  - Staged (ready to commit)
  - Modified but not staged
  - Untracked (new files Git doesn’t know about)
  - In conflict after a merge
    
*Stage a single file*
```
git add README.md
```
```
git add pom.xml
```

*Stage multiple files at once*
```
git add pom.xml README.md
```

*Stage all files/dirs*
```
git add .
```
       or
```
git add -A
```
```
git status
```
```
git commit -m "chore: initial deployment"                #Commits staged changes
```
```
git status                                               #Verify
```
```
git log                                                  #View logs
```

---

## Linking Local Git Repository with Remote GitHub Repository 

**SSH Key-based Authentication to GitHub**

Generate SSH key:
```
ssh-keygen
```
or
```
  ssh-keygen -t ed25519 -C "pyakurelelx@gmail.com"
```
```
cd ~/.ssh
```
```
vim config
```
```
Host github.com
  HostName github.com
  User git
  ServerAliveInterval 60
  ServerAliveCountMax 5
  TCPKeepAlive yes
  IPQoS throughput
```

Set permissions and start the agent:
```
chmod 600 ~/.ssh/config
```
```
eval "$(ssh-agent -s)"                #Start background process of ssh
```
```
ssh-add ~/.ssh/id_ed25519             #Handover private key to the background process of ssh 
```

Add public key to GitHub:
```
cat ~/.ssh/id_ed25519.pub              #Copy output
```
Log in to your GitHub account:
GitHub 
  → Settings 
    → SSH and GPG keys 
      → New SSH key

Test:
```
ssh -T git@github.com
```

Log in to your GitHub account and navigate to the desired repository:

----
Using SSH

1. Log in to your GitHub account and open the desired repository.
2. Click the Code button.
3. Select SSH.
4. Copy the SSH repository link
5. Open your terminal and run:
  ```bash
    git clone git@github.com:OWNER/REPO.git
  ```

---

Using HTTPS

1. Log in to your GitHub account and open the desired repository.
2. Click the **Code** button.
3. Select **HTTPS**.
4. Copy the HTTPS link.
5. Open your terminal and run:
   ```bash
     git clone https://github.com/OWNER/REPO.git
   ```

---

Using GitHub CLI (`gh`)

1. Make sure you have [GitHub CLI](https://cli.github.com/) installed and authenticated.
   ```bash
   gh auth login
   ```
   
2. In your terminal, run:
   ```bash
   gh repo clone OWNER/REPO
   ```

---

Replace `OWNER/REPO` with your repository’s path (e.g., `techgeek68/cafe-website-on aws-s3`).  

---
**Link local to remote:**

```
cd ~/javaapp/sample-app
```
```
git remote add origin git@github.com:techgeek68/JavaApp.git
```
```
git remote -v
```

*Remove origin (if needed):*
```
git remote remove origin
```

Pull (configure and fetch):
Pulling files from the remote repository into the local repository.
```
git config pull.rebase true     #Optional preference
```
```
git pull origin main            #Use 'master' if your repo uses that
```

Push:
Pushing files in the local repository to the remote GitHub repository.
```
git push origin main
```

**Unlink remote (if needed):**
```
git remote rm origin
```
```
git config --list
```

---

## Branching:
A branch in Git is a lightweight, movable pointer to a specific commit in your
repository's history. It represents an independent line of development, allowing you to
work on features, bug fixes, or experiments without altering the main
codebase (e.g., main or master branch). Branches are created to:
  - Isolate work
  - Enable parallel development
  - Experiment safely
  - Organize workflow

**Merging Branch**
- Merging integrates changes from one branch (e.g., a feature branch) into another
(e.g., main). It’s necessary because:

Consolidate completed work:
- Merge a stable feature/bugfix into main to include it in production.
  
Share progress:
- Combine work from multiple branches (e.g., merge a teammate’s branch).

Preserve history:
- Git records the merge commit, maintaining context about when/why changes
were combined.

Avoid code duplication:
- Without merging, branches drift apart, leading to redundant code and conflicts.
      Syntax:
          git merge <branch_name>
          
**Branch: Create, Switch example & Merge:**
```
git branch productreview
```
```
git switch productreview
```
```
git branch
```

Make changes:
```
echo "<h1>Rate our service</h1>" > userreview
```
```
git status
```
```
git add userreview
```
```
git commit -m "feat(productreview): add user review prompt"
```
```
git status
```

Return to the main and compare:
```
git switch main
```
```
git diff main..productreview              #Inspect differences
```

Merge productreview into main:
```
git merge productreview
```

Push:
```
git push origin main
```

---
**Cloning a Remote Repository**
Cloning copies a remote repository (e.g., from GitHub, GitLab) to your local
machine, including all files, branches, and commit history.

Syntax:
```
git clone <repository-url> [destination-directory]
```

Examples:
```
git clone https://github.com/user/repo.git                #HTTPS Clone
```
```
git clone https://github.com/user/repo.git my-project      #Clone into a specific directory 
```
```
git clone git@github.com:user/repo.git                     #Clone via SSH
```
```
git clone --branch develop https://github.com/user/repo.git #Clone a specific branch
```
```
git clone --depth 1 https://github.com/user/repo.git        #Shallow Clone (Latest Commit Only)
```

---

**Example: Initialize a PHP Website Repo**
```
sudo dnf install git -y
```
```
mkdir phpproject && cd phpproject
```
```
git init
```
```
git add .
```
```
git commit -m "chore: initial commit"
```
```
git remote add origin https://github.com/techgeek68/my-project.git
```
```
git push -u origin main
```

---

## Troubleshooting

- “mvn” or other build artifacts tracked by mistake
```
echo -e "target/\n*.class" >> .gitignore
```
```
git rm -r --cached target
```
```
git commit -m "build: ignore target directory"
```

- Push rejected (non-fast-forward)
```
git pull --rebase origin main
```
*resolve conflicts, then:*
```
git push origin main
```

- Wrong email in commits
```
git config --global user.email "correct@example.com"
```
*For past commits (advanced):*
*git filter-repo ...            or           git filter-branch (legacy)*

- Accidentally committed secrets
```
#Remove from code and history; rotate the secret immediately.
#Use git filter-repo to purge, then force-push (coordination required).
```

- Large repo sluggish:
Over time, a big Git repository can become slow due to accumulated loose objects, old pack files, and unnecessary data.
```
git gc --aggressive --prune=now    #Performs thorough cleanup and removes all unreachable objects to optimize repository size and speed.
```
```
git repack -ad           #Repack all objects into a single pack and delete redundant packs to optimize repository storage.    
```
---
# Part B: Team Engineering Workflows (Module 4)

Part A above is the mechanics of Git. Part B is the part that gets you hired and keeps you employed: how a team of people who disagree with each other ships software through a shared repository without breaking production.

---

## B1. Distributed Version Control Is a Mental Model, Not a History Log

Most people learn Git as a list of commands that produce a list of commits. That model works until the first rebase, then it collapses. The model that survives is the object model.

### The four object types

Git is a content addressable key value store. Everything is stored under the SHA of its own content.

| Object | What it holds |
|--------|---------------|
| blob   | The bytes of a file. No name, no path, no permissions. |
| tree   | A directory listing: names, modes, and the SHAs of blobs and other trees. |
| commit | One tree SHA, zero or more parent commit SHAs, author, committer, message. |
| tag    | An annotated pointer to an object, with its own message and optional signature. |

A branch is not a container of commits. A branch is a 41 byte file containing one SHA. Look at it:

```bash
cat .git/refs/heads/main
```
```bash
git cat-file -p HEAD              # show the commit object: tree, parent, author, message
```
```bash
git cat-file -p HEAD^{tree}       # show the directory listing that commit points at
```
```bash
git rev-parse HEAD                # the SHA that "HEAD" currently resolves to
```

Three consequences follow immediately, and they explain most Git behaviour that beginners find arbitrary.

1. **A commit is a full snapshot, not a diff.** Diffs are computed on demand between two snapshots. This is why `git checkout` of an old commit is instant and why history rewriting is cheap.
2. **History is a directed acyclic graph, not a line.** `git log` prints a linearised view of a graph. Merges have two parents. Rebase does not move commits, it creates new commit objects with new SHAs and new parents, and abandons the old ones.
3. **Nothing is deleted when you "delete" it.** `git reset --hard` moves a pointer. The old commits stay in the object database, unreferenced, until garbage collection removes them. That is why `git reflog` can save you, and why it is your first response to any Git accident.

```bash
git reflog                        # every position HEAD has held, including the ones you "lost"
git log --oneline --graph --decorate --all
```

### What "distributed" actually means

Every clone contains the complete object database and the full history. There is no privileged copy at the protocol level. `origin` is privileged only because your team agreed it is. The remote is a social convention enforced by server side permissions, not a property of Git.

This gives you:

* Offline work, including branching, committing, merging, blaming, and bisecting.
* No single point of failure. Any clone can reconstitute the project.
* Cheap branches, because a branch costs one file with one SHA in it.
* Merges that use a merge base. Git finds the common ancestor of two branches and performs a three way merge. Conflicts occur only where both sides changed the same region relative to that base.

### The three trees

Every Git command you run is moving data between three places. Memorise this and `reset` stops being frightening.

| Tree | Meaning | Inspect with |
|------|---------|--------------|
| HEAD | The last commit on the current branch | `git show HEAD` |
| Index (staging area) | The proposed next commit | `git diff --staged` |
| Working tree | The files on disk | `git diff` |

`git reset` takes a commit and optionally rewrites these three trees:

* `--soft` moves HEAD only.
* `--mixed` (default) moves HEAD and the index.
* `--hard` moves HEAD, the index, and the working tree. Only this one destroys uncommitted work.

Once this table is internalised, the rest of the chapter is bookkeeping.

---

## B2. Branching Strategies and Their Trade Offs

There are only four models in wide use, and the correct answer depends on team size, release cadence, and whether you support multiple versions in the field at once.

### Feature branching

Branch from `main`, work, open a pull request, merge back, delete the branch. This is the substrate that every other model builds on. It says nothing about how long the branch lives, which is the only variable that actually matters.

### GitHub Flow

One long lived branch, `main`, which is always deployable. Every change is a short lived branch plus a pull request. Merge to `main` triggers deployment. No release branches, no develop branch.

Good for: web services with continuous deployment, one production version, small to mid size teams.
Weak for: shipping software that customers install and pin to a version.

### Git Flow

Published by Vincent Driessen in 2010. Two permanent branches (`main` for released code, `develop` for integration) plus three transient types (`feature/*`, `release/*`, `hotfix/*`).

```
main     o-----------------o---------o        (tagged releases only)
          \               /         /
release    \        o----o         /          (stabilise, bugfix only)
            \      /              /
develop  o---o----o------o-------o            (integration)
          \       /       \     /
feature    o--o--o         o---o
```

Note the honest caveat the author himself added years later: Git Flow was designed for versioned software with several supported releases in the wild, and it is a poor fit for a continuously delivered web application. Teams that adopt it by default usually inherit the ceremony without the requirement.

Good for: installed software, firmware, mobile apps with store review cycles, anything supporting multiple live versions.
Weak for: continuous delivery. `develop` becomes a second integration bottleneck, merges get large, and conflicts pile up in release branches.

### Trunk based development

Everyone commits to one trunk. Branches, if they exist at all, live for hours and never more than a day. Incomplete work ships behind feature flags rather than sitting on a branch. Releases are cut as tags on trunk, or as short lived release branches that only take cherry picked fixes.

This is the model correlated with high delivery performance in the DORA research programme, and it is what large engineering organisations converge on. The reason is arithmetic: merge pain grows with the square of branch lifetime and the number of parallel branches. Shrink the lifetime to a day and merge pain approaches zero.

Prerequisites, and they are not optional:

* Fast, trustworthy CI on every commit. If the pipeline takes forty minutes, trunk based development becomes trunk based breakage.
* Feature flags, so that unfinished code can be merged and disabled.
* Expand and contract migrations, so that schema changes are backward compatible across a deploy.
* A culture where breaking trunk is fixed within minutes and is nobody's shame.

### Choosing

| Team size | Reasonable default | Why |
|-----------|--------------------|-----|
| 1 to 3 | Trunk with short branches, or trunk directly | Ceremony costs more than it returns. Still protect `main` and still use PRs, because the reviewer may be future you. |
| 4 to 15 | GitHub Flow or trunk based with short lived feature branches | One deployable branch, PR review, CI gate. This is the sweet spot for most product teams. |
| 15 to 50 | Trunk based, feature flags, merge queue | Parallel PRs start racing each other. A merge queue serialises them and tests each candidate against the head it will actually land on. |
| Multiple supported versions in the field | Git Flow, or trunk plus long lived release branches | You need somewhere to backport a security fix to version 3.2 while trunk is on 5.0. |

Rules of thumb that hold at every size:

* Branch lifetime is the metric. Optimise it downward. Everything else is derived.
* Long lived branches are a debt instrument. You borrow speed today and repay it, with interest, in conflict resolution.
* Never create a branch you cannot describe in one sentence, and never create one whose merge you cannot imagine.

---

## B3. Pull Requests and Code Review

A pull request is not a Git feature. Git has no concept of a PR. It is a platform object: a request to merge branch A into branch B, plus a comment thread, plus a set of status checks, plus policy. The Git operation underneath is an ordinary merge.

### Why review exists

Review has four jobs, in descending order of value:

1. **Correctness against intent.** Does this do what the issue asked, and is what the issue asked actually the right thing?
2. **Risk detection.** What happens on the error path, under concurrency, under load, on rollback, with a partially applied migration?
3. **Knowledge distribution.** After merge, at least two people understand this code. This is the quiet reason review survives audits and staff turnover.
4. **Shared standards.** Consistency of design, not of whitespace.

### What makes a review useful rather than a rubber stamp

A rubber stamp is an approval issued without a model of what the code does. It is worse than no review, because it launders risk into a signed audit trail.

Useful reviews have observable properties:

* **The diff is small.** Effectiveness collapses beyond a few hundred changed lines. If the PR is large, the correct review comment is "split this."
* **The reviewer runs it, or at least reads the tests as a specification.** Ask: if this code were subtly wrong, which of these tests would fail? If the answer is none, the tests are decoration.
* **Comments are specific and actionable, and separate blocking from taste.** Use conventional comment prefixes so intent is unambiguous:

  ```
  blocking: this drops the transaction if the retry fires. Wrap in the same tx.
  question: why 3 retries and not the module default of 5?
  nit: name this `userID` for consistency with the rest of the package.
  praise: nice, this removes the whole special case in the caller.
  ```
* **Formatting is never discussed.** Formatters and linters run in pre-commit and in CI. A human arguing about a trailing comma is a process failure, not a diligent reviewer.
* **The security and operability questions are asked every time.** Authorisation checks, input validation, injection surfaces, secrets, logging of sensitive fields, new dependencies and their provenance, backward compatibility, metrics and rollback path.
* **Review latency is measured.** A perfect review delivered in three days is worse for the organisation than a good review delivered in three hours, because the author has context switched and the branch has drifted. Treat review as an interrupt, not as backlog.

`CODEOWNERS` routes reviews automatically to the people who own the touched paths:

```
# .github/CODEOWNERS
/infra/            @platform-team
/services/billing/ @billing-team @security-guild
*.tf               @platform-team
```

### Reviewing generated code

This deserves its own treatment, because it is becoming the majority of the reviewing you will do, and it fails differently from human code.

Human code fails where the human was confused, and the confusion is usually visible in the code. Generated code fails where the model was confident, and confidence is invisible. The specific failure modes:

* **Plausible but wrong.** The code compiles, reads beautifully, follows house style, and quietly does the wrong thing at the boundary. Review the boundaries first: empty input, zero, nil, off by one, timezone, currency rounding, partial failure.
* **Invented APIs.** A function that does not exist, a flag that was removed two versions ago, a config key that was never real. Verify every unfamiliar call against the actual documentation, not against how reasonable it sounds.
* **Silent scope creep.** The model refactored three files it was not asked to touch. Every hunk in the diff must be justified by the issue, and hunks that are not are removed or split into their own PR.
* **Tests generated from the same wrong assumption.** If the same tool wrote the code and the tests, the tests confirm the bug. Read the tests before the implementation and ask whether they would catch a real regression.
* **Provenance and licence.** Large verbatim blocks that look like they came from somewhere probably did. Your organisation's policy, not your comfort level, decides what is acceptable.
* **Volume.** Generation makes it trivially cheap to produce a 900 line PR. The reviewer, not the generator, absorbs that cost. Push back on size, hard.

The professional standard: **the author owns the diff, regardless of who or what typed it.** "The model wrote it" is not an explanation, it is an abdication. In review, ask the author to explain a non obvious hunk in their own words. If they cannot, that is your finding, and it is a blocking one.

---

## B4. Conventional Commits and the Payoff

We do not enforce a commit format because we enjoy bureaucracy. We enforce it because a machine readable commit history is an input to automation. We enforce the format here in section B4, and cash it in during Lab 4C.

### The format

```
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

Types in common use: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

```
feat(auth): add TOTP second factor

Adds a TOTP enrolment endpoint and verification on login. Codes are
30 second windows with one step of clock skew allowed.

Refs: #142
```

Breaking changes are marked with `!` after the type or scope, or with a `BREAKING CHANGE:` footer:

```
feat(api)!: return 404 instead of 200 with empty body for missing users

BREAKING CHANGE: clients that relied on the empty 200 must handle 404.
```

### The mapping to Semantic Versioning

This is the whole point. The commit type is a machine readable declaration of release impact.

| Commit | SemVer effect | 1.4.2 becomes |
|--------|---------------|---------------|
| `fix:` | patch | 1.4.3 |
| `feat:` | minor | 1.5.0 |
| `feat!:` or `BREAKING CHANGE:` footer | major | 2.0.0 |
| `docs:`, `chore:`, `test:`, `ci:`, `style:` | none | 1.4.2 |

### What you get once the format is enforced

* **Automated version bumps.** Nobody edits a version string by hand, so nobody forgets.
* **Automated changelogs.** `CHANGELOG.md` is generated from the commits, grouped by type, with links to the commits and issues.
* **Automated releases.** Tag, GitHub Release, release notes, and optionally a package publish, all triggered by a merge.
* **Automated blame at the release level.** "Which release introduced this?" becomes a lookup rather than an investigation.

### The two tools you will meet

* **semantic-release**: releases immediately on merge to the release branch. It computes the version, tags, publishes, writes the changelog, all in the pipeline. Aggressive and excellent for libraries.
* **release-please** (`googleapis/release-please-action@v4`): does not release on merge. It maintains a standing **Release PR** that accumulates changes and shows you the next version and the proposed changelog. You release by merging that PR. Safer for services, because a human still chooses the moment. We use this in Lab 4C.

**The squash merge trap.** If your repository squashes PRs, the commit that lands on `main` carries the **PR title**, not the individual commit messages. Lint the PR title as well, otherwise every landed commit is `Update stuff (#42)` and the automation produces nothing. Enforce it with a PR title linter in CI, or require merge commits.

---

## B5. Pre-Commit Hooks: Catch It on the Laptop, Not in the Pipeline

A CI failure costs you a context switch, a pipeline minute, and a public red cross on the PR. A pre-commit hook costs you two seconds. The cheapest defect is the one that never becomes a commit.

### How hooks actually work

Git looks in `.git/hooks/` for executable scripts named after lifecycle events. That directory is **not versioned and not cloned**, so raw hooks cannot be shared with the team. This is the single most important fact about hooks, and it is why frameworks exist. A framework versions a config file, and each developer runs one install command that writes the actual hook, usually by pointing `core.hooksPath` at a tracked directory.

| Hook | Fires | Typical use |
|------|-------|-------------|
| `pre-commit` | Before the commit message editor opens | Format, lint, secret scan, validate YAML |
| `commit-msg` | After the message is written | Enforce conventional commits with commitlint |
| `pre-push` | Before objects are sent to the remote | Fast test subset, build check |
| `pre-receive`, `update` | On the **server**, before refs are updated | Non bypassable policy. On GitHub this is expressed as rulesets. |

### The three frameworks

* **pre-commit** (`pre-commit.com`), Python based but language agnostic, the de facto standard for polyglot and infrastructure repositories. This is what we use.
* **husky**, Node ecosystem, pairs with `lint-staged` and `commitlint`.
* **lefthook**, Go binary, parallel execution, no runtime dependency, popular in monorepos.

### The correction to the old note

The old notes describe `pre-commit` with the text for `pre-push`. To be precise: `pre-commit` runs on `git commit`, before the message is composed, and aborting it aborts the commit. `pre-push` runs on `git push`.

### The rule you must not forget

**Hooks are advisory. `git commit --no-verify` skips all of them.** A hook is a courtesy to the developer, never a control. Anything that genuinely must not enter the repository has to be enforced server side, in CI and in rulesets. In practice you run the same checks twice: locally for speed, in CI for authority.

```bash
pre-commit run --all-files      # what CI will do
pre-commit autoupdate           # bump pinned hook revisions
```

---

## B6. Signed Commits and Branch Protection as Baseline Hygiene

### Why signing

The author and committer fields on a commit are self asserted strings. Nothing stops anyone with push access from doing this:

```bash
git config user.name "Linus Torvalds"
git config user.email "torvalds@linux-foundation.org"
git commit -m "fix: totally legitimate change"
```

That commit will show Linus in `git log` and, if he has a GitHub account with that email, his avatar next to it. Signing is what converts an assertion into evidence.

### SSH signing, the modern default

GPG still works, but since Git 2.34 you can sign with an SSH key, which almost every developer already has. It is a two minute setup instead of a twenty minute one.

```bash
ssh-keygen -t ed25519 -C "signing key" -f ~/.ssh/id_signing
```
```bash
git config --global gpg.format ssh
```
```bash
git config --global user.signingkey ~/.ssh/id_signing.pub
```
```bash
git config --global commit.gpgsign true
```
```bash
git config --global tag.gpgsign true
```

Then upload the **public** key to GitHub under Settings, SSH and GPG keys, New SSH key, and set the key type to **Signing key**, not Authentication key. Uploading it as an authentication key will not produce the Verified badge.

For local verification, tell Git which keys you trust:

```bash
mkdir -p ~/.config/git
echo "you@example.com $(cat ~/.ssh/id_signing.pub)" >> ~/.config/git/allowed_signers
git config --global gpg.ssh.allowedSignersFile ~/.config/git/allowed_signers
```
```bash
git log --show-signature -1
git verify-commit HEAD
```

Sigstore's `gitsign` is worth knowing by name: it signs with a short lived certificate tied to an OIDC identity and logs to a transparency log, which removes long lived key management entirely. It appears in supply chain hardened pipelines.

### Branch protection, and the shift to rulesets

Classic branch protection rules (Settings, Branches) still exist and still work. GitHub now steers new configuration toward **repository rulesets** (Settings, Rules, Rulesets), and rulesets are what you should reach for. What they add over the classic rules:

* Definable at organisation level and applied across many repositories.
* Multiple rulesets **layer**, and the most restrictive combination wins, rather than one rule per branch pattern.
* Explicit **bypass lists** per ruleset, with an audit trail, instead of a single "include administrators" checkbox.
* An **evaluate** enforcement status, so you can see what a rule would have blocked before you turn it on.
* Import and export as JSON, so protection is reviewable configuration rather than remembered clicks.
* **Push rulesets**, which can block pushes by file path, block oversized files, and enforce secret push protection.

The baseline for any branch that reaches production:

| Setting | Value | Why |
|---------|-------|-----|
| Require a pull request | On, 1 approval minimum | No unreviewed code on the deployable branch |
| Dismiss stale approvals on new commits | On | Otherwise: get approval, push anything, merge |
| Require status checks to pass | On, and require branches to be up to date | A green check against a stale base proves nothing |
| Require signed commits | On | Identity is evidence, not assertion |
| Require linear history | On, if you squash or rebase merge | Keeps `git bisect` and changelog generation sane |
| Block force pushes | On | See Lab 4B |
| Restrict deletions | On | People delete `main`. It happens. |
| Bypass list | Empty on production branches | A rule that admins can bypass is a suggestion |

---

## B7. Issue Tracking and Traceability

The question every audit, every incident review, and every new team member eventually asks is: **why is this line of code here?** A team with traceability answers it in ninety seconds. A team without it never answers it.

The chain you are building is:

```
Epic  ->  Story (issue)  ->  branch  ->  commit  ->  PR  ->  merge  ->  release  ->  deploy
```

Every arrow in that chain must be a link a machine can follow.

### The vocabulary, without the consultancy

* **Epic**: a body of work too large for one sprint, expressed as an outcome. "Users can pay with a saved card."
* **Story**: a unit of user visible value, small enough to finish in a sprint. Written as: as a `<role>`, I want `<capability>`, so that `<benefit>`. It carries **acceptance criteria**, which are the only part that matters, because they are what makes the story testable and reviewable.
* **Task**: an engineering step with no independent user value. "Add the migration."
* **Bug**: observed behaviour differs from intended behaviour.
* **Spike**: a timeboxed investigation whose deliverable is a decision, not code.
* **Sprint**: a fixed length iteration, usually two weeks, with a committed scope.
* **Backlog**: the ordered list of everything not yet done. Ordered, not a set. If it is not ordered it is a wish list.
* **Board**: the visualisation of state, typically Todo, In Progress, In Review, Done.
* **WIP limit**: a cap on items in a column. This is the single highest leverage practice in Kanban, because throughput is destroyed by parallelism, not by laziness.

### GitHub Issues and Projects

We use GitHub because it is free, it is already where the code is, and the links between issue, branch, PR, and release are automatic rather than manual. The relevant current capabilities:

* **Issue types** (Bug, Task, Feature, and organisation defined types) classify issues consistently across repositories. Generally available since 2025.
* **Sub-issues** create a real parent and child hierarchy, up to eight levels, with progress rolled up in Projects. This is how you model an epic: one issue with the Feature type, and its stories as sub-issues. Note that the older **tasklist** blocks were retired in April 2025, and any note or tutorial still telling you to write ` ```[tasklist] ` blocks is out of date.
* **Projects** (the current version, not Projects Classic, which has been sunset) is a table, board, and roadmap view over issues and PRs, with custom fields. An **iteration** field is how you express a sprint. Built in workflows auto add items and move them between columns on events.
* **Closing keywords** in a PR description or a commit on the default branch close the issue automatically: `closes #12`, `fixes #12`, `resolves #12`. A bare `#12` links without closing, which is what you want on a commit that is part of a larger story.
* **Milestones** group issues by release or date. **Labels** carry orthogonal metadata such as `area/api` or `good first issue`.

The `gh` CLI now covers this from the terminal, including issue types, sub-issue relationships, and dependencies, so board maintenance does not require a browser.

### Jira, for recognition only

You will meet Jira in industry, so recognise the mapping: Jira **project** is roughly a repository or product, **board** is scrum or kanban, **issue types** are Epic, Story, Task, Sub-task, Bug, **workflow** is a configurable state machine (this is where organisations do their worst damage), **JQL** is the query language, and **smart commits** let a commit message transition an issue with syntax such as `PROJ-123 #close`. Jira integrates with GitHub through an app that links commits and PRs by issue key in the branch name or commit message. You will not be asked to run a Jira instance in this course.

### Traceability in practice

Adopt these conventions and the chain links itself:

* Branch name carries the issue: `feat/142-totp-enrolment`.
* Commit body carries a trailer: `Refs: #142`.
* PR description carries the closing keyword: `Closes #142`.
* Conventional commit type drives the changelog entry that ships in the release notes.

Result: from a line in production, `git blame` gives the commit, the commit gives the PR, the PR gives the issue, the issue gives the epic and the acceptance criteria and the discussion where somebody explained why. Ninety seconds.
---

# Part C: Labs

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
git log --author="Alice" --since="2 weeks ago"
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

**Deliverables:** terminal transcripts showing (a) the rejected push after `reset`, (b) the successful push after `revert`, (c) `git reflog` output and the recovery, and (d) a `git log --graph` of the final history with your written explanation of which commits are still present in each case and why.

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

From the terminal, if you prefer:

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

# Appendix A: Complete Git and GitHub Worked Example

*(Retained in full from the original notes. See Appendix B for corrections to apply when teaching from it.)*

# Complete Git & GitHub Example:

---
---
Sign up for [GitHub](https://github.com/) and create an account by providing your email, username, and password.

Create a new repository

   * After signing in, click the **“+”** icon at the top-right corner and select **“New repository.”**
   * Enter a repository name — for example:

     * `PHPwebsite`
     * `Javaapp`
   * Choose visibility (Public or Private) and click **“Create repository.”**

---
---

**Install git**:
```bash
  sudo dnf install git -y
```

---
---
**Setup SSH Authentication**:

Generates a new SSH key pair using the Ed25519 algorithm, labeling it with the provided email address.
```bash
  ssh-keygen -t ed25519 -C "your_email_ID"
```

  Or
  
Generates a new SSH key pair using the RSA algorithm, labeling it with the provided email address.
```
  ssh-keygen -t rsa -b 4096 -C "your_email_ID"
```

Verify
```bash
  ls -a
```
```bash
  ls .ssh
```

Starts the SSH agent in the background and sets up environment variables for SSH authentication.
```
  eval "$(ssh-agent -s)"
```

Adds your Ed25519 private SSH key to the SSH agent for authentication.
```
  ssh-add ~/.ssh/id_ed25519
```

Displays your public Ed25519 SSH key.
```
  cat ~/.ssh/id_ed25519.pub
```
Copy this output to add it to your GitHub>Settings>SSH and GPG keys>New SSH key.

You can test your SSH connection to GitHub; it should return a success message if keys are set up correctly.
```bash
  ssh -T git@github.com
```
>Are you sure you want to continue connecting (yes/no/[fingerprint])? yes


---
---

**Setup HTTPS Authentication**

Create a Personal Access Token (PAT) on GitHub:
  - Go to GitHub > Settings > Developer settings > Personal access tokens.
  - Click **"Generate new token"** (classic is fine for simple use).
  - Give your token a name, select the required scopes (e.g., `repo` for repository access), and set an expiration date.
  - Click **"Generate token"** and **copy the token**. You won’t be able to view it again!

**Clone a Repository Using HTTPS**
  - Replace `<username>` and `<repo>` below:
```bash
  git clone https://github.com/<username>/<repo>.git
```

Clone Example:
```bash
  mkdir PHPwebsite
```
```bash
  cd PHPwebsite
```
```bash
  git clone https://github.com/codepoet21/PHPwebsite.git
```
```bash
  ls PHPwebsite
```
```bash
  cd
```

**Global configuration git identity**
```bash
  git config --global user.name "Your Name"
```
```bash
  git config --global user.email "your_email@example.com"
```
```bash
  git config --list
```

>---
>**(Optional)**
>**Set Up Git Credential Helper:**
>
>This securely stores your credentials, so you don’t need to enter your PAT every time.
>
> - **Store temporarily (in memory):**
>  ```bash
>     git config --global credential.helper cache
>  ```
> - **Store permanently (plain text, not recommended for shared systems):**
>   ```bash
>     git config --global credential.helper store
>   ```
>
>Authenticate with Your PAT When you push, pull, or perform any write operation, Git will prompt for your username and password.
>
>---

  - **Username:** Your GitHub username
  - **Password:** Paste your Personal Access Token (PAT)


**Push example:**

```bash
mkdir JavaApp
```

```bash
cd JavaApp
```

```
git init
```

```bash
vim myApp
```

Write Code and then save and exit.
```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

```bash
  git add .
```
```bash
  git commit -m "Initial commit"
```
```bash
  git remote add origin https://github.com/codepoet21/JavaApp.git
```
```bash
 git push origin master
```
```
Username: your-github-username
Password: <paste your personal access token here>
```
Verify Setup
Try pushing/pulling. If successful, your HTTPS authentication is complete!

---

**Troubleshoot:**

  1. **Pull Remote Changes:**
     - `git pull origin master`
     - If asked, specify merge/rebase:
       - Merge: `git pull origin master --no-rebase`
       - Rebase: `git pull origin master --rebase`
       - Fast-forward only: `git pull origin master --ff-only`

  2. **Resolve Conflicts (if any):**
     - Edit conflicted files.
     - `git add <file>`
     - `git commit -m "Resolve merge conflict"`

  3. **Push Again:**
     - `git push origin master`

- **Force Push (Dangerous):**
  - Overwrites remote history:  
    `git push --force origin master`
  - Use only if you are sure.

---
---

**Install & Configure Git**

Configure:
```bash
git config --global user.name "Your_GitHub_Username"
git config --global user.email "Your_Email_ID"
git config --global core.editor "vim"      # or nano
git config --list
```

Verify:
```bash
git config --list
```

**Additional Global Configuration (Optional)**

Change Default Branch Name for New Repositories:
```bash
git config --global init.defaultBranch main
```

Enable Colored Output:
```bash
git config --global color.ui auto
```

Set Up Credential Helper:
- Cache credentials (store in memory for 15 minutes by default):
  ```bash
  git config --global credential.helper cache
  ```
- Store credentials (plaintext, not recommended for shared systems):
  ```bash
  git config --global credential.helper store
  ```

Set Merge or Rebase Strategy for Pulls:
- Always merge:
  ```bash
  git config --global pull.rebase false
  ```
- Always rebase:
  ```bash
  git config --global pull.rebase true
  ```

---

**Initialize Local Repository & Add .gitignore**:
To start tracking your project with Git, create a new directory for your code and initialize a Git repository using `git init`. This sets up version control and creates a hidden `.git` folder. It's important to add a `.gitignore` file, which lists files and directories that Git should not track—such as build artifacts, dependencies, or sensitive data. This keeps your repository clean and secure.

Example: Simple Java App.

```bash
mkdir -p ~/JavaApp
cd ~/JavaApp/
```

Create your Maven project:
```bash
mvn archetype:generate -DgroupId=com.example -DartifactId=sample-app -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false
```
```bash
cd sample-app
```

```bash
git init
```
```bash
echo -e "target/\n*.class\n.env\nnode_modules/" > .gitignore
```

**Stage & Commit Initial Files**

```bash
echo "# JavaApp" > README.md
```
```
vim product-list.js
```
```js
const products = ["Laptop", "Phone", "Tablet"];
console.log(products);
```
```
git status
```
```
git add .
```
```
git commit -m "chore: initial project setup"
```
```
git status
```

**Create Remote Repo on GitHub & Link Local**

- On GitHub: Create `JavaApp` repo (public, README, default branch: master).
- Copy SSH link: `git@github.com:techgeek68/JavaApp.git`

```bash
git remote add origin git@github.com:techgeek68/JavaApp.git
```
```bash
git push -u origin master
```

---
---

**Create three users, Alice, Bob, and Carol**
 - Adds three users (Alice, Bob, Carol) with 'devops' password and gives them sudo privileges.
```bash
sudo useradd -m -p $(openssl passwd -1 devops) Alice && \
sudo useradd -m -p $(openssl passwd -1 devops) Bob && \
sudo useradd -m -p $(openssl passwd -1 devops) Carol && \
sudo usermod -aG wheel Alice && \
sudo usermod -aG wheel Bob && \
sudo usermod -aG wheel Carol
```
```
cat /etc/passwd
```
---

**6. Clone Repository (for Bob & Carol)**

```bash
git clone https://github.com/codepoet21/JavaApp.git
```
```bash
cd JavaApp
```

---

**7. Standard Git Workflow**

**Stage & Commit Changes**

```bash
vim pricerangefilter
```
```java
System.out.println("Price Range Filter");
```
```bash
git add pricerangefilter
```
```bash
git commit -m "feat: add price range filter"
```
```bash
git status
```

**Branching**

```bash
git branch feature/product-filter
git switch feature/product-filter
# or modern: git switch -c feature/product-filter
```
Edit files, then:
```bash
git add product-list.js
git commit -m "feat: add price range filter"
git switch main
```

**Merging**

```bash
git switch main
git merge feature/product-filter
```

**Remotes**

```bash
git push origin main
git pull origin main
git remote -v
```

---

**8. Collaboration: Three Developers**

**Alice (frontend):**

```bash
git pull origin main
# Edit product-list.js
git add product-list.js
git commit -m "feat: add price range filter"
git push origin main
```

**Carol (UI):**
```bash
git fetch origin
# Edit styles.css
git add styles.css
git commit -m "feat: redesign cart UI"
git push origin main
```

**Bob (backend):**
```bash
git pull origin main
# Edit checkout.php
git add checkout.php
git commit -m "feat: add coupon validation"
git push origin main
# If push fails (Carol pushed first):
git pull --rebase origin main
# Resolve conflicts, then:
git add styles.css
git rebase --continue
git push origin main
```

---

**9. Common Commands**

**Status, Diff, Logs**

```bash
git status
git diff
git diff --staged
git log --oneline --graph --decorate --all
```

**Branch Management**

```bash
git branch
git branch -vv
git switch -c feature/login
git switch main
git branch -d feature/login
```

**Remote Management**

```bash
git remote -v
git remote add origin git@github.com:techgeek68/JavaApp.git
git remote remove origin
```

**History & Tagging**

```bash
git log -- filename
git log --author="Alice"
git tag v1.0.0
git push origin v1.0.0
```

**Stash**

```bash
git stash push -m "WIP: refactor service"
git stash list
git stash pop
```

---

**10. Undoing Changes**

**Edited Not Staged**

```bash
git restore <file>       # Modern, safer
git checkout -- <file>   # Older syntax
```

**Staged Not Committed**

```bash
git reset HEAD <file>
git restore --staged <file>
git restore <file>
```

**Already Committed**

```bash
git reset --soft HEAD~1      # Undo last commit, keep staged
git reset --mixed HEAD~1     # Undo, keep changes in working directory
git reset --hard HEAD~1      # WARNING: Discards changes!
git log                      # Find commit hash
git revert --no-commit <commit_hash>
git commit -m "revert: undo <short-hash> <subject>"
```

---

**11. Ignore Files (.gitignore)**

Example:

```gitignore
# Dependencies
node_modules/
.venv/
venv/
target/
dist/
*.class

# OS
.DS_Store
Thumbs.db

# IDE
.idea/
*.iml
.vscode/

# Logs and env
*.log
.env
.env.*
```

---

**12. Customizing Git**

**Configuration**

```bash
git config --local
git config --global
git config --system
git config --global user.name "techgeek68"
git config --global user.email "pyakurelelx@gmail.com"
git config --global core.editor "vim"
git config --list
```

**Aliases (~/.gitconfig)**

```ini
[lol]
    log --oneline --graph --decorate --all
[cleanup]
    "!git branch --merged | egrep -v '\\*|main|master' | xargs -r git branch -d"
```

**Hooks (.git/hooks/)**
- pre-commit: run linter/tests
- pre-push: run smoke tests
- post-receive: deploy on server

---

**13. Best Practices**
- Descriptive commit messages:
  ```
  feat: add user registration
  fix: resolve NPE (#42)
  ```
- Use imperative mood, small logical commits
- Pull before work; push after meaningful commits
- Strategic branching (`main`, `develop`, `feature/*`, `bugfix/*`, `hotfix/*`)
- Delete merged branches

---

**14. Example: Branch, Edit, Merge**

```bash
git branch productreview
git switch productreview
echo "<h1>Rate our service</h1>" > userreview
git add userreview
git commit -m "feat(productreview): add user review prompt"
git switch main
git diff main..productreview
git merge productreview
git push origin main
```

---

**15. Cloning Remote Repo (Various Methods)**

```bash
git clone https://github.com/techgeek68/JavaApp.git
git clone git@github.com:techgeek68/JavaApp.git
git clone --branch develop https://github.com/techgeek68/JavaApp.git
git clone --depth 1 https://github.com/techgeek68/JavaApp.git
```

---

**16. Initialize PHP Repo Example**

```bash
sudo dnf install git -y
mkdir phpproject && cd phpproject
git init
git add .
git commit -m "chore: initial commit"
git remote add origin https://github.com/techgeek68/my-project.git
git push -u origin main
```

---

**17. Troubleshooting**

- Tracked build artifacts by mistake:
  ```bash
  echo -e "target/\n*.class" >> .gitignore
  git rm -r --cached target
  git commit -m "build: ignore target directory"
  ```

- Push rejected:
  ```bash
  git pull --rebase origin main
  # Resolve conflicts, then:
  git push origin main
  ```

- Wrong email in commits:
  ```bash
  git config --global user.email "correct@example.com"
  ```

- Accidentally committed secrets:
  ```
  # Remove secret, use git filter-repo, then force-push (coordinate with team)
  ```

- Large repo sluggish:
  ```bash
  git gc --aggressive --prune=now
  git repack -ad
  ```

---


Use this as a reference for any real-world Git & GitHub workflow!
---

# Appendix B: Fact Check and Corrections to Earlier Material

Everything in Part A and Appendix A above is retained as written. This appendix records what has changed in the upstream tools and platforms since those notes were drafted, and the places where the original commands do not do what the surrounding text says they do. Read it as errata, and apply it when teaching.

## Platform changes

| Topic | What the old notes say or imply | Current state |
|---|---|---|
| Branch protection | Settings, Branches, Add rule | Still functional, but GitHub now steers configuration toward **repository rulesets** (Settings, Rules). Rulesets add organisation level scope, layering, per ruleset bypass lists with an audit trail, an evaluate mode, JSON import and export, and push rules. Teach rulesets, mention classic rules so students recognise them. |
| Task lists inside issues | Not covered, but common in older material | The ` ```[tasklist] ` block was **retired in April 2025**. The replacement is **sub-issues**, which give a real parent and child hierarchy up to eight levels, with progress roll up in Projects. |
| Issue classification | Labels only | **Issue types** (Bug, Task, Feature, plus organisation defined) went generally available in 2025 and are the correct way to mark an epic. |
| Project boards | Not covered | **Projects Classic has been sunset.** Use Projects (the current version), where a sprint is an **Iteration** field. |
| GitHub CLI | Not covered | `gh` now manages issue types, sub-issue relationships, and issue dependencies from the terminal (shipped June 2026), so board work no longer requires the browser. |
| Default branch | Notes mix `master` and `main`, and push to `master` | GitHub has created new repositories with `main` since October 2020. Set `git config --global init.defaultBranch main` and use `main` consistently. Keep the `master` examples only where you are teaching against an existing legacy repository. |
| Personal Access Tokens | Classic PAT with the `repo` scope | Classic PATs still work, but **fine grained PATs** are the recommended default: per repository, per permission, mandatory expiry. Better still, use `gh auth login`, which handles the credential for you. |
| Secrets in repositories | "Use git filter-repo, then force push" | Still correct, and now add: GitHub **secret scanning with push protection** is free on public repositories and blocks the push before the secret lands. Enable it. And always rotate the credential first. Purging history without rotating is theatre. |
| `git filter-branch` | Mentioned as legacy | It is effectively deprecated and Git itself recommends `git filter-repo`. Do not teach `filter-branch` as an option. |
| SSH keys | `ssh-keygen` with RSA or Ed25519 | Ed25519 is the default recommendation. GitHub removed support for the legacy `ssh-rsa` (SHA-1) signature algorithm in 2022, so very old RSA keys and old clients fail. Ed25519 avoids the issue entirely. |
| Commit signing | Not covered | SSH signing (`gpg.format ssh`) has been available since Git 2.34 and is now the pragmatic default. GPG remains valid. Upload the key to GitHub as a **Signing key**, not an Authentication key. |
| Credential helper `store` | Offered as an option | It writes the token to `~/.git-credentials` **in plaintext**. Do not teach it as acceptable outside a throwaway VM. Prefer `gh auth login`, `libsecret` on Linux, or `osxkeychain` on macOS. |
| `git gc --aggressive` | Offered as routine maintenance | It is expensive and almost never what you want. Modern Git runs maintenance automatically, and `git maintenance start` schedules it properly. Reserve `--aggressive` for a genuinely pathological repository. |

## Tool versions used in Lab 4C, as of July 2026

* `pre-commit/pre-commit-hooks`: `rev: v6.0.0`
* `gitleaks/gitleaks`: `rev: v8.30.1`
* `googleapis/release-please-action@v4`. Note the older `google-github-actions/release-please-action` is archived and redirects here.
* `husky` v9. `npx husky add` was **removed**. Run `npx husky init` and then write the hook file yourself, for example `echo 'npx --no -- commitlint --edit "$1"' > .husky/commit-msg`. Any tutorial still using `husky install` plus `husky add` predates v9.
* `@commitlint/cli` with `@commitlint/config-conventional`.

Pin these revisions, and let `pre-commit autoupdate` and Dependabot move them forward under review, rather than floating on `latest`.

## Command level corrections in the existing material

These are small, but students copy notes verbatim, so they matter. Items 1 to 7 have been **applied to the body in this edition**; they are kept here as a changelog so anyone comparing against an older copy can see what moved. Items 8 and 9 are teaching notes, not text edits, and still apply.

1. `la -a` corrected to `ls -a`. *(applied)*
2. The duplicated `git clone git clone https://...` reduced to a single `git clone`. *(applied)*
3. The undo example created `pricefilter` but staged `pricerangefilter`; the created file is now `pricerangefilter` so the names match. *(applied)*
4. `git checkout paymentgatewaycode` was ambiguous if a branch of that name exists; the note now teaches `git restore paymentgatewaycode`, with `git checkout -- paymentgatewaycode` as the older equivalent. *(applied)*
5. `git revert --no-commit <hash>` stages the inverse but does **not** commit; the mandatory follow-up `git commit` has been added, and the note now points out that plain `git revert <hash>` does both in one step. *(applied)*
6. `git config --global color.ui auto` sat inside an unclosed code fence, which swallowed the following section when rendered; the fence is now closed. *(applied)*
7. The hooks prose labelled `pre-commit` with the description of `pre-push`; it now correctly states that `pre-commit` runs on `git commit`, before the message editor opens, and `pre-push` runs on `git push`. *(applied)*
8. The three user creation exercise gives Alice, Bob, and Carol the same password and full sudo. Fine in a disposable lab VM, and worth saying out loud that it would be a finding in any real environment. *(teaching note)*
9. The collaboration example has all three developers pushing directly to `main`. That is realistic only in a repository with no protection. Once Lab 4C is done, the same exercise must run through pull requests, and it is worth running it both ways so students feel the difference. *(teaching note)*
