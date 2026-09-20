"""Recognize explicit platform failures to capture the game container's logs."""
import re


def capture_failed(log):
    return log.startswith('Pod logs were not captured:') or bool(re.search(
        r"(?m)^===== container: game =====\r?\n[bB]?(['\"])unable to retrieve container logs for containerd://[0-9a-f]{64}\1(?:\r?\n|$)", log))
