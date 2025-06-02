"""
Task definitions for development workflows.
"""

from invoke import task


@task
def clean(c):
    """Remove build artifacts."""
    c.run("rm -rf build/")
    c.run("rm -rf dist/")
    c.run("rm -rf *.egg-info")
    c.run("rm -rf .pytest_cache/")
    c.run("rm -rf .coverage")
    c.run("rm -rf htmlcov/")
    c.run("find . -type d -name __pycache__ -exec rm -rf {} +")
    c.run("find . -type f -name '*.pyc' -delete")


@task
def format(c):
    """Format code with black and isort."""
    c.run("black stonkwise tests")
    c.run("isort stonkwise tests")


@task
def lint(c):
    """Run linters: flake8 and mypy."""
    c.run("flake8 stonkwise tests")
    c.run("mypy stonkwise")


@task
def test(c):
    """Run tests."""
    c.run("pytest tests/")


@task
def coverage(c):
    """Run tests with coverage."""
    c.run("pytest --cov=stonkwise tests/")
    c.run("coverage html")


@task
def install(c):
    """Install the package in development mode."""
    c.run("pip install -e .")


@task
def build(c):
    """Build the package."""
    c.run("poetry build")


@task
def run_example(c, ticker="MSFT", period="day", strategy="simple"):
    """Run an example analysis."""
    c.run(f"python -m stonkwise analyze --ticker {ticker} --period {period} --strategy {strategy}")
