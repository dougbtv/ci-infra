import subprocess
import os
from typing import List, Optional
import requests


def get_merge_base_commit() -> Optional[str]:
    """Get merge base commit from env var or compute it via git."""
    merge_base = os.getenv("MERGE_BASE_COMMIT")
    if merge_base:
        return merge_base
    # Compute merge base if not provided
    try:
        result = subprocess.run(
            ["git", "merge-base", "origin/main", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_list_file_diff(branch: str, merge_base_commit: Optional[str]) -> List[str]:
    """Get list of file paths that get changed between current branch and origin/main."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        if branch == "main":
            output = subprocess.check_output(
                ["git", "diff", "--name-only", "--diff-filter=ACMDR", "HEAD~1"],
                universal_newlines=True,
            )
        else:
            merge_base = merge_base_commit
            if not merge_base:
                pass
            output = subprocess.check_output(
                [
                    "git",
                    "diff",
                    "--name-only",
                    "--diff-filter=ACMDR",
                    merge_base.strip(),
                ],
                universal_newlines=True,
            )
        return [line for line in output.split("\n") if line.strip()]
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get git diff: {e}")
    except AttributeError:
        # Case where merge_base_commit is None
        raise RuntimeError("Failed to determine merge base commit for git diff.")


def get_ancestors(commit: str, max_count: int = 50) -> List[str]:
    """
    Get ancestor commits starting from the given commit.

    Args:
        commit: Starting commit SHA
        max_count: Maximum number of ancestors to return

    Returns:
        List of commit SHAs in chronological order (newest first)
    """
    try:
        result = subprocess.run(
            ["git", "rev-list", "--max-count", str(max_count), commit],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError:
        return []


def has_cpp_changes_between(old_commit: str, new_commit: str) -> bool:
    """
    Check if any C++ related files changed between two commits.

    Args:
        old_commit: Older commit SHA
        new_commit: Newer commit SHA (or HEAD)

    Returns:
        True if C++ files changed, False otherwise
    """
    cpp_patterns = [
        "csrc/",
        "cmake/",
        "CMakeLists.txt",
        "setup.py",
        "requirements/build.txt",
    ]

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{old_commit}..{new_commit}"],
            capture_output=True,
            text=True,
            check=True,
        )
        changed_files = result.stdout.strip().split('\n')

        for file in changed_files:
            for pattern in cpp_patterns:
                if file.startswith(pattern) or file == pattern:
                    return True
        return False
    except subprocess.CalledProcessError:
        # If git diff fails, be conservative and assume C++ changed
        return True


def get_pr_labels(pull_request: str, repo_name: str) -> List[str]:
    if not pull_request or pull_request == "false":
        return []
    request_url = f"https://api.github.com/repos/{repo_name}/pulls/{pull_request}"
    response = requests.get(request_url)
    response.raise_for_status()
    return [label["name"] for label in response.json()["labels"]]
