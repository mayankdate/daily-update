# Git recipes

Both recipes are global VS Code tasks ("Git: re-apply .gitignore" and
"Git: DANGER wipe all history and start over"; see GUIDE.md). This page shows
the commands behind them, for running in a terminal inside the project folder.

## Re-apply .gitignore to files that were committed before it ignored them

Safe: files stay on disk, git just stops tracking the ones now ignored.

```
git rm -r --cached .
git add .
git commit -m "Reapply .gitignore to project files"
git push
```

## Destructive: these throw away history

Only for a repo whose history you truly don't need, e.g. one where a secret
was committed. Even then, rotate the secret first: GitHub may still hold it.

Wipe local history and start over (replace `REPO` with the repo name):

```
Remove-Item -Recurse -Force .git
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/mayankdate/REPO.git
git push -u origin main --force
```

`--force` overwrites everything on GitHub with your local copy. Anything
pushed from another machine and not on this one is lost.
