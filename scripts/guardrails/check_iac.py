#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent
    return current


def run(cmd: list[str], cwd: Path) -> bool:
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode == 0


def run_env_checks(env_dir: Path) -> bool:
    ok = True
    ok &= run(["terraform", "init", "-backend=false"], env_dir)
    ok &= run(["terraform", "validate"], env_dir)
    return ok


def main() -> int:
    repo_root = find_repo_root(Path(__file__).parent)
    terraform_dir = repo_root / "infra" / "terraform"
    if not terraform_dir.exists():
        print("No infra/terraform directory found; skipping IaC checks.")
        return 0

    terraform = shutil.which("terraform")
    if not terraform:
        print("terraform not installed; skipping IaC checks.")
        return 0

    ok = True
    ok &= run(["terraform", "fmt", "-check", "-recursive"], terraform_dir)
    ok &= run(["terraform", "init", "-backend=false"], terraform_dir)
    ok &= run(["terraform", "validate"], terraform_dir)

    dev_env = terraform_dir / "envs" / "dev"
    if dev_env.exists():
        ok &= run_env_checks(dev_env)
    else:
        print("infra/terraform/envs/dev missing; skipping env checks.")

    tflint = shutil.which("tflint")
    if tflint:
        ok &= run(["tflint", "--init"], terraform_dir)
        ok &= run(["tflint"], terraform_dir)
    else:
        print("tflint not installed; skipping.")

    tfsec = shutil.which("tfsec")
    if tfsec:
        ok &= run(["tfsec", "."], terraform_dir)
    else:
        print("tfsec not installed; skipping.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
