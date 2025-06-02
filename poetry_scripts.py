"""
Poetry scripts for the stonkwise project.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_format():
    """Run code formatters."""
    print("Running black...")
    subprocess.run(["black", "stonkwise", "tests"], check=True)
    print("Running isort...")
    subprocess.run(["isort", "stonkwise", "tests"], check=True)
    print("Running autoflake...")
    subprocess.run(
        [
            "autoflake",
            "--in-place",
            "--recursive",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "stonkwise",
            "tests",
        ],
        check=True,
    )
    print("Code formatting complete.")


def run_lint():
    """Run linters."""
    print("Running flake8...")
    subprocess.run(["flake8", "stonkwise", "tests"], check=True)
    print("Running mypy...")
    subprocess.run(["mypy", "stonkwise"], check=True)
    print("Linting complete.")


def run_test():
    """Run tests."""
    print("Running pytest...")
    subprocess.run(["pytest", "-xvs", "tests"], check=True)
    print("Tests complete.")


def run_clean():
    """Clean up temporary files."""
    print("Cleaning up temporary files...")
    # Clean up __pycache__ directories
    for path in Path(".").glob("**/__pycache__"):
        for file in path.glob("*"):
            file.unlink()
        path.rmdir()
    
    # Clean up .pytest_cache
    if Path(".pytest_cache").exists():
        for file in Path(".pytest_cache").glob("**/*"):
            if file.is_file():
                file.unlink()
        for path in sorted(Path(".pytest_cache").glob("**/*"), key=lambda p: len(str(p)), reverse=True):
            if path.is_dir():
                path.rmdir()
        Path(".pytest_cache").rmdir()
    
    # Clean up .mypy_cache
    if Path(".mypy_cache").exists():
        for file in Path(".mypy_cache").glob("**/*"):
            if file.is_file():
                file.unlink()
        for path in sorted(Path(".mypy_cache").glob("**/*"), key=lambda p: len(str(p)), reverse=True):
            if path.is_dir():
                path.rmdir()
        Path(".mypy_cache").rmdir()
    
    print("Cleanup complete.")


def run_example():
    """Run the example script."""
    print("Running example...")
    from stonkwise.cli import cli
    sys.argv = ["stonkwise", "analyze", "--ticker", "MSFT"]
    cli()


def run_build():
    """Run the build process (format, lint, test)."""
    print("Running build process...")
    try:
        run_format()
        run_lint()
        run_test()
        print("Build successful!")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)
