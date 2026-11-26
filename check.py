"""Verify the synthetic component and profile can run together."""

import json
import os
from pathlib import Path
import subprocess
import time


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def main():
    component = Path("component.txt").read_text().strip()
    profile = Path("profile.txt").read_text().strip()
    event_name = os.environ.get("GITHUB_EVENT_NAME", "local")
    head, tree = git("rev-parse", "HEAD", "HEAD^{tree}").splitlines()
    group = None
    if event_name == "merge_group":
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
        group = event["merge_group"]
        assert head == group["head_sha"]
    print(json.dumps({"event": event_name, "head": head, "tree": tree, "group": group,
                      "component": component, "profile": profile}, sort_keys=True), flush=True)
    if group is not None:
        # Make the queue's waiting state observable in this disposable fixture.
        time.sleep(26)
    if component not in {"local", "remote"} or profile not in {"standard", "legacy", "modern"}:
        raise SystemExit("Unknown component or profile")
    if component == "remote" and profile == "legacy":
        raise SystemExit("The remote component does not support the legacy profile")
    print("The component and profile are compatible")


if __name__ == "__main__":
    main()
