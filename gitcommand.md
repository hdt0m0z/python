# Common Git Commands

This is a quick reference for the most frequently used Git commands.

---

### 1. Setup & Configuration

Configure your Git installation.

| Command                                      | Description                                                  |
| :------------------------------------------- | :----------------------------------------------------------- |
| `git config --global user.name "[name]"`     | Sets the name you want attached to your commit transactions.   |
| `git config --global user.email "[email]"` | Sets the email you want attached to your commit transactions.  |
| `git config --list`                          | Lists all Git configurations.                                |

---

### 2. Creating a Repository

Start a new repository or get one from an existing URL.

| Command                     | Description                                                          |
| :-------------------------- | :------------------------------------------------------------------- |
| `git init [project-name]`   | Creates a new local repository with a specified name.                |
| `git clone [url]`           | Downloads a project and its entire version history from a remote repository. |

---

### 3. Staging & Snapshots (The Staging Area)

Manage changes before committing them.

| Command                | Description                                                          |
| :--------------------- | :------------------------------------------------------------------- |
| `git status`           | Lists all new or modified files to be committed.                     |
| `git add [file]`       | Adds a file to the staging area, preparing it for a commit.          |
| `git add .`            | Adds all new and modified files in the current directory to the staging area. |
| `git diff`             | Shows file differences that are not yet staged.                      |
| `git diff --staged`    | Shows file differences between the staging area and the last commit. |
| `git reset [file]`     | Unstages a file, but preserves its contents.                         |

---

### 4. Committing Changes

Save your staged changes to the project history.

| Command                               | Description                                                                    |
| :------------------------------------ | :----------------------------------------------------------------------------- |
| `git commit -m "[commit message]"`    | Records the staged snapshot to the project history with a descriptive message. |
| `git commit --amend`                  | Combines staged changes with the previous commit, or lets you edit the previous commit message. |

---

### 5. Branching & Merging

Work on different features or versions of your project in isolation.

| Command                             | Description                                                          |
| :---------------------------------- | :------------------------------------------------------------------- |
| `git branch`                        | Lists all of the branches in your repository.                        |
| `git branch [branch-name]`          | Creates a new branch.                                                |
| `git checkout [branch-name]`        | Switches to the specified branch and updates the working directory.  |
| `git checkout -b [new-branch-name]` | Creates a new branch and immediately switches to it.                 |
| `git merge [branch-name]`           | Combines the specified branch’s history into the current branch.     |
| `git rebase [branch-name]`          | Re-applies commits from the current branch onto the tip of another branch. |
| `git branch -d [branch-name]`       | Deletes the specified branch.                                        |

---

### 6. Inspecting History

Browse and inspect the evolution of your project files.

| Command                                   | Description                                                          |
| :---------------------------------------- | :------------------------------------------------------------------- |
| `git log`                                 | Shows the commit history for the current branch.                     |
| `git log --oneline`                       | Shows the commit history in a condensed, single-line format.         |
| `git log --graph --oneline --decorate`    | A useful command to visualize the commit history as a graph.         |
| `git show [commit]`                       | Shows the metadata and content changes of a specific commit.         |

---

### 7. Syncing with Remote Repositories

Manage connections to remote repositories and synchronize your work.

| Command                                  | Description                                                                    |
| :--------------------------------------- | :----------------------------------------------------------------------------- |
| `git remote -v`                          | Lists all your currently configured remote repositories.                       |
| `git remote add [name] [url]`            | Adds a new remote repository.                                                  |
| `git fetch [remote-name]`                | Downloads all history from the remote repository but doesn't integrate it.     |
| `git pull [remote-name] [branch-name]`   | Fetches and merges the remote branch into your current local branch.           |
| `git push [remote-name] [branch-name]`   | Uploads all local branch commits to the remote repository.                     |
| `git push -u [remote-name] [branch-name]`| Pushes the branch and sets it up to track the remote branch.                   |

---

### 8. Undoing Changes

Revert changes and clean your working directory.

| Command                   | Description                                                                    |
| :------------------------ | :----------------------------------------------------------------------------- |
| `git revert [commit]`     | Creates a new commit that undoes all of the changes made in a specific commit. |
| `git reset --hard [commit]` | **(Use with caution!)** Discards all changes and resets the branch tip back to a specified commit. |
| `git clean -n`            | Shows which files would be removed from the working directory.                 |
| `git clean -f`            | **(Use with caution!)** Deletes all untracked files from the working directory.  |