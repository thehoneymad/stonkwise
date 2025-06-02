"""
Task definitions for development workflows.
"""

import os
import shutil
import sys
from invoke import task


@task
def clean(c):
    """Remove build artifacts."""
    c.run("rm -rf build/")
    c.run("rm -rf dist/")
    c.run("rm -rf *.egg-info")
    c.run("rm -rf .pytest_cache/")
    c.run("rm -rf .mypy_cache/")
    c.run("rm -rf .coverage")
    c.run("rm -rf htmlcov/")
    c.run("find . -type d -name __pycache__ -exec rm -rf {} +")
    c.run("find . -type f -name '*.pyc' -delete")


@task
def clean_venv(c):
    """Remove virtual environment."""
    if os.path.exists(".venv"):
        shutil.rmtree(".venv")
        print("Removed .venv directory")


@task
def setup_venv(c):
    """Set up a virtual environment."""
    if not os.path.exists(".venv"):
        c.run("python -m venv .venv")
        print("Created .venv directory")
    
    # Determine the activate script based on the OS
    if sys.platform == "win32":
        activate_script = ".venv\\Scripts\\activate"
    else:
        activate_script = ".venv/bin/activate"
    
    print(f"To activate the virtual environment, run: source {activate_script}")


@task
def install_deps(c):
    """Install dependencies using Poetry."""
    c.run("pip install poetry")
    c.run("poetry config virtualenvs.in-project true")  # Create .venv in project directory
    c.run("poetry install")


@task
def format(c):
    """Format code with black and isort."""
    c.run("poetry run black stonkwise tests")
    c.run("poetry run isort stonkwise tests")


@task
def lint(c):
    """Run linters: flake8 and mypy."""
    c.run("poetry run flake8 stonkwise tests")
    c.run("poetry run mypy stonkwise")


@task
def test(c):
    """Run tests."""
    c.run("poetry run pytest tests/")


@task
def coverage(c):
    """Run tests with coverage."""
    c.run("poetry run pytest --cov=stonkwise tests/")
    c.run("poetry run coverage html")


@task
def build(c):
    """Build the package."""
    c.run("poetry build")


@task
def run_example(c, ticker="MSFT", period="day", strategy="simple"):
    """Run an example analysis."""
    c.run(f"poetry run python -m stonkwise analyze --ticker {ticker} --period {period} --strategy {strategy}")


@task
def setup_dev(c):
    """Set up the complete development environment."""
    setup_venv(c)
    install_deps(c)
    print("\nDevelopment environment setup complete!")
    print("\nYou can now run the following commands:")
    print("  invoke format      - Format code")
    print("  invoke lint        - Lint code")
    print("  invoke test        - Run tests")
    print("  invoke run-example - Run an example analysis")
    print("  invoke clean       - Clean build artifacts")
    print("  invoke clean-venv  - Remove virtual environment")
