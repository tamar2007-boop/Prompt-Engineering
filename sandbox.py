"""Bonus: run a command inside a throwaway Docker container.

Only for a Linux target (the container is Linux, so Windows cmd commands cannot
run in it). Refused/forbidden commands are never sent to Docker.
usage: uv run python sandbox.py "ls -la"
"""
import subprocess
import sys

from safety import danger_leak, parse


def run_in_sandbox(output: str, timeout: int = 10) -> dict:
    status, cmd = parse(output)
    if status == "refused" or danger_leak(output):
        return {"ran": False, "reason": "refused or forbidden"}
    docker = [
        "docker", "run", "--rm",
        "--network", "none",       # no network
        "--read-only",             # read-only root filesystem
        "--tmpfs", "/tmp",
        "--memory", "128m", "--cpus", "0.5", "--pids-limit", "64",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "alpine:3.20", "sh", "-c", cmd,
    ]
    try:
        p = subprocess.run(docker, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ran": True, "ok": False, "stderr": "timeout"}
    return {"ran": True, "ok": p.returncode == 0, "returncode": p.returncode,
            "stdout": p.stdout[:500], "stderr": p.stderr[:500]}


if __name__ == "__main__":
    print(run_in_sandbox(" ".join(sys.argv[1:])))
