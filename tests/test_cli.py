"""
Tests for the CLI module.
"""

import os
import tempfile
from pathlib import Path

import pytest
from assertpy import assert_that
from click.testing import CliRunner

from stonkwise.cli import cli


class TestCLI:
    """Test cases for the CLI module."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_cli_version(self, runner):
        """Test the CLI version option."""
        result = runner.invoke(cli, ["--version"])
        assert_that(result.exit_code).is_equal_to(0)
        assert_that(result.output).contains("0.1.0")

    def test_cli_help(self, runner):
        """Test the CLI help option."""
        result = runner.invoke(cli, ["--help"])
        assert_that(result.exit_code).is_equal_to(0)
        assert_that(result.output).contains("Stonkwise")
        assert_that(result.output).contains("analyze")

    def test_analyze_help(self, runner):
        """Test the analyze command help option."""
        result = runner.invoke(cli, ["analyze", "--help"])
        assert_that(result.exit_code).is_equal_to(0)
        assert_that(result.output).contains("ticker")
        assert_that(result.output).contains("period")
        assert_that(result.output).contains("backtest")

    def test_analyze_missing_ticker(self, runner):
        """Test the analyze command with missing ticker."""
        result = runner.invoke(cli, ["analyze"])
        assert_that(result.exit_code).is_not_equal_to(0)
        assert_that(result.output).contains("Error")
        assert_that(result.output).contains("ticker")

    @pytest.mark.skip(reason="Requires network access to Yahoo Finance")
    def test_analyze_with_ticker(self, runner):
        """Test the analyze command with a ticker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_output.png")
            result = runner.invoke(
                cli, ["analyze", "--ticker", "MSFT", "--output", output_path]
            )
            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("Plotting MSFT")
            assert_that(Path(output_path).exists()).is_true()

    @pytest.mark.skip(reason="Requires network access to Yahoo Finance")
    def test_analyze_with_backtest(self, runner):
        """Test the analyze command with backtest mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_output.csv")
            result = runner.invoke(
                cli,
                [
                    "analyze",
                    "--ticker",
                    "MSFT",
                    "--backtest",
                    "--output",
                    output_path,
                ],
            )
            assert_that(result.exit_code).is_equal_to(0)
            assert_that(result.output).contains("Backtesting MSFT")
            assert_that(Path(output_path).exists()).is_true()

    @pytest.mark.skip(reason="Requires network access to Yahoo Finance")
    def test_analyze_with_trend_detection(self, runner):
        """Test the analyze command with trend detection."""
        result = runner.invoke(
            cli,
            [
                "analyze",
                "--ticker",
                "MSFT",
                "--show-trend",
                "--start-date",
                "2020-01-01",
            ],
        )
        assert_that(result.exit_code).is_equal_to(0)
        assert_that(result.output).contains("Detected market structure")

    @pytest.mark.skip(reason="Requires network access to Yahoo Finance")
    def test_analyze_with_zones_detection(self, runner):
        """Test the analyze command with supply/demand zones detection."""
        result = runner.invoke(
            cli,
            [
                "analyze",
                "--ticker",
                "MSFT",
                "--show-zones",
                "--start-date",
                "2020-01-01",
            ],
        )
        assert_that(result.exit_code).is_equal_to(0)
        assert_that(result.output).contains("Detected")
        assert_that(result.output).contains("supply zones")
        assert_that(result.output).contains("demand zones")
