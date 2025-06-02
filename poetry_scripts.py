"""
Script functions for Poetry commands.
"""

import os
import shutil
import subprocess
from typing import List, Optional


def run_format(args: Optional[List[str]] = None) -> None:
    """Format code with black and isort."""
    print("Formatting code with black...")
    subprocess.run(["black", "stonkwise", "tests"], check=True)

    print("Sorting imports with isort...")
    subprocess.run(["isort", "stonkwise", "tests"], check=True)

    print("✅ Code formatting complete")


def run_lint(args: Optional[List[str]] = None) -> None:
    """Run linters: flake8 and mypy."""
    print("Running flake8...")
    subprocess.run(["flake8", "stonkwise", "tests"], check=False)

    print("\nRunning mypy...")
    subprocess.run(["mypy", "stonkwise"], check=False)

    print("✅ Linting complete")


def run_test(args: Optional[List[str]] = None) -> None:
    """Run tests."""
    cmd = ["pytest", "tests/"]
    if args:
        cmd.extend(args)

    print(f"Running tests: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)


def run_clean(args: Optional[List[str]] = None) -> None:
    """Remove build artifacts."""
    dirs_to_remove = [
        "build/",
        "dist/",
        ".pytest_cache/",
        ".mypy_cache/",
        "htmlcov/",
        ".coverage",
    ]

    # Add *.egg-info directories
    for item in os.listdir("."):
        if item.endswith(".egg-info") and os.path.isdir(item):
            dirs_to_remove.append(item)

    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
            else:
                os.remove(dir_path)
            print(f"Removed {dir_path}")

    # Remove __pycache__ directories and .pyc files
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dir = os.path.join(root, dir_name)
                shutil.rmtree(cache_dir)
                print(f"Removed {cache_dir}")

        for file_name in files:
            if file_name.endswith(".pyc"):
                pyc_file = os.path.join(root, file_name)
                os.remove(pyc_file)
                print(f"Removed {pyc_file}")

    print("✅ Clean complete")


def run_example(args: Optional[List[str]] = None) -> None:
    """Run an example analysis."""
    ticker = "MSFT"
    period = "day"
    strategy = "simple"

    if args:
        # Parse args in format: --ticker=MSFT --period=day --strategy=simple
        for arg in args:
            if arg.startswith("--ticker="):
                ticker = arg.split("=")[1]
            elif arg.startswith("--period="):
                period = arg.split("=")[1]
            elif arg.startswith("--strategy="):
                strategy = arg.split("=")[1]

    cmd = [
        "python",
        "-m",
        "stonkwise",
        "analyze",
        "--ticker",
        ticker,
        "--period",
        period,
        "--strategy",
        strategy,
    ]

    print(f"Running example: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)
