"""Interactions with Git repo."""
import os

def commit(basedir):
    try:
        return get_commit_id(basedir)
    except FileNotFoundError:
        return os.environ.get('GIT_REV', 'main')


def get_commit_id(base_dir):
    """Return commit ID of this repo."""
    git_head = os.path.join(base_dir, ".git", "HEAD")
    # https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script#21901260
    # Open .git\HEAD file:
    with open(git_head, "r") as git_head_file:
        # Contains e.g. ref: ref/heads/master if on "master"
        git_head_data = str(git_head_file.read()).strip()

    # Open the correct file in .git\ref\heads\[branch]
    if " " in git_head_data:
        git_head_ref = os.path.join(
            base_dir,
            ".git",
            git_head_data.split(" ")[1],
        )
    else:
        # When pinned to a specific commit
        git_head_ref = os.path.join(base_dir, ".git", git_head_data)

    # Get the commit hash ([:7] used to get "--short")
    with open(git_head_ref, "r") as f:
        return f.read().strip()
