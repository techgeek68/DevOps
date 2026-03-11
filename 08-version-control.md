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

Undo changes
```
git checkout paymentgatewaycode
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
<h1> select iteam </h1>
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
git revert --no-commit <commit_hash>    #This creates a new commit that undoes the effects of the previous one.
```

Example:
```
git revert --no-commit 4e772d533db53efec66f03a37e3cdfeda31787cd
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

- Pre-commit: The pre-push hook is a script that runs before you push commits to a remote repository. It allows you to automate checks, tests, or other actions to ensure code quality or enforce policies before the push completes. location: .git/hooks/pre-push
  
- Post-receive: Runs on the remote repository after a push is received. Often used to trigger deployment, notifications, or CI jobs.

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
<type>:<subject>            #e.g. Feat: Add user registration
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
````
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
