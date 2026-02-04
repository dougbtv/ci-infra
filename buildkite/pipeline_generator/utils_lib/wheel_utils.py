import requests
from typing import Optional

WHEEL_BASE_URL = "https://wheels.vllm.ai"
WHEEL_CHECK_TIMEOUT = 3  # seconds


def check_wheel_exists(commit: str, timeout: int = WHEEL_CHECK_TIMEOUT) -> bool:
    """
    Check if a precompiled wheel exists for the given commit.

    Args:
        commit: Git commit SHA
        timeout: HTTP request timeout in seconds

    Returns:
        True if wheel metadata exists, False otherwise
    """
    wheel_metadata_url = f"{WHEEL_BASE_URL}/{commit}/vllm/metadata.json"
    try:
        response = requests.head(wheel_metadata_url, timeout=timeout)
        return response.status_code == 200
    except (requests.RequestException, requests.Timeout):
        return False


def find_nearest_wheel_commit(
    merge_base: str,
    max_ancestors: int = 20
) -> Optional[str]:
    """
    Find the nearest ancestor commit with a precompiled wheel.

    Walks back through git history starting from merge_base to find
    the first commit that has a precompiled wheel available.

    Args:
        merge_base: Starting commit (usually from git merge-base)
        max_ancestors: Maximum commits to check

    Returns:
        Commit SHA with available wheel, or None if not found
    """
    from .git_utils import get_ancestors

    # First try merge_base itself
    if check_wheel_exists(merge_base):
        return merge_base

    # Walk back through ancestors
    ancestors = get_ancestors(merge_base, max_ancestors)
    for ancestor in ancestors:
        if check_wheel_exists(ancestor):
            return ancestor

    return None
