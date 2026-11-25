"""Small jobs for the project this file sits in (one folder up from utilities/).

Copied into every project by RepoManager, so it works without RepoManager.
The project's VS Code tasks run it; nothing here needs a terminal.

    python utilities/project_tools.py reignore       stop tracking files .gitignore now covers
    python utilities/project_tools.py restart YES    DESTRUCTIVE: wipe git history, push one fresh commit
    python utilities/project_tools.py tree           print the folder tree (needs R)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def git(*cmd):
    r = subprocess.run(["git", "-C", str(PROJECT), *cmd], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def checked_git(*cmd):
    print("git " + " ".join(cmd))
    code = subprocess.run(["git", "-C", str(PROJECT), *cmd]).returncode
    if code != 0:
        sys.exit(code)


def reignore():
    # For files committed before .gitignore covered them. Files stay on disk; git stops tracking them.
    if git("status", "--porcelain")[1]:
        # Otherwise the commit below would sweep your unfinished edits in with it.
        sys.exit("This project has uncommitted changes. Commit or discard them in Source Control first.")
    checked_git("rm", "-r", "--cached", "--quiet", ".")
    checked_git("add", ".")
    if git("diff", "--cached", "--quiet")[0] == 0:
        print("Nothing to change: every ignored file was already untracked.")
        return
    checked_git("commit", "-m", "Reapply .gitignore to project files")
    print("\nDone. Click Sync Changes in Source Control to send it to GitHub.")


def remove_tree(path):
    # Git marks some of its files read-only, which stops Windows from deleting them.
    def make_writable_and_retry(func, target, _exc):
        os.chmod(target, 0o700)
        func(target)
    shutil.rmtree(path, onexc=make_writable_and_retry)


def restart(confirm):
    if confirm != "YES":
        sys.exit("Cancelled. Nothing was changed.")
    code, url = git("remote", "get-url", "origin")
    if code != 0:
        sys.exit(f"{PROJECT.name} has no GitHub remote, so there is nothing to restart.")
    # Keep the project's own git settings (account, name, email) across the wipe.
    keep = {}
    for name in git("config", "--local", "--list", "--name-only")[1].splitlines():
        if name.startswith(("user.", "credential.")):
            keep[name] = git("config", "--local", "--get", name)[1]
    print(f"Wiping the history of {PROJECT.name} and replacing {url} with this folder as it is now.")
    remove_tree(PROJECT / ".git")
    checked_git("init", "--quiet", "-b", "main")
    for name, value in keep.items():
        checked_git("config", "--local", name, value)
    checked_git("add", "-A")
    checked_git("commit", "--quiet", "-m", "Initial commit")
    checked_git("remote", "add", "origin", url)
    checked_git("push", "-u", "origin", "main", "--force")
    print("\nDone. GitHub now holds only this one commit.")


def find_rscript():
    found = shutil.which("Rscript")
    if found:
        return found
    # R on Windows is rarely on PATH; take the newest installed version.
    installs = sorted(Path("C:/Program Files/R").glob("R-*/bin/Rscript.exe"))
    if installs:
        return str(installs[-1])
    sys.exit("Could not find R. Install R, or source utilities/folder_tree_builder.R in RStudio instead.")


def tree():
    script = Path(__file__).with_name("folder_tree_builder.R")
    sys.exit(subprocess.run([find_rscript(), str(script), str(PROJECT)]).returncode)


def main():
    job = sys.argv[1] if len(sys.argv) > 1 else ""
    if job == "reignore":
        reignore()
    elif job == "restart":
        restart(sys.argv[2] if len(sys.argv) > 2 else "")
    elif job == "tree":
        tree()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
