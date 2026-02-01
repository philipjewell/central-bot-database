"""
Tests for fetch_ai_robots.py
"""
import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from fetch_ai_robots import (
    clean_markdown_links,
    get_category_from_entry
)


class TestCleanMarkdownLinks:
    """Test markdown link cleaning"""

    def test_cleans_simple_link(self):
        assert clean_markdown_links("[Amazon](https://amazon.com)") == "Amazon"

    def test_cleans_multiple_links(self):
        assert clean_markdown_links("[Link1](url1) and [Link2](url2)") == "Link1 and Link2"

    def test_handles_no_links(self):
        assert clean_markdown_links("Plain text") == "Plain text"

    def test_handles_empty_string(self):
        assert clean_markdown_links("") == ""

    def test_handles_none(self):
        assert clean_markdown_links(None) == ""

    def test_preserves_spaces(self):
        assert clean_markdown_links("[Google Bot](https://google.com)") == "Google Bot"


class TestGetCategoryFromEntry:
    """Test category extraction from ai.robots.txt entries"""

    def test_prefers_function_field(self):
        entry = {
            "function": "AI Agents",
            "operator": "Amazon"
        }
        assert get_category_from_entry(entry) == "AI Agents"

    def test_falls_back_to_operator(self):
        entry = {
            "function": "No information provided.",
            "operator": "Test Company"
        }
        assert get_category_from_entry(entry) == "Test Company"

    def test_cleans_markdown_from_operator(self):
        entry = {
            "operator": "[Amazon](https://amazon.com)"
        }
        assert get_category_from_entry(entry) == "Amazon"

    def test_handles_company_field(self):
        entry = {
            "company": "Test Company"
        }
        assert get_category_from_entry(entry) == "Test Company"

    def test_handles_owner_field(self):
        entry = {
            "owner": "Test Owner"
        }
        assert get_category_from_entry(entry) == "Test Owner"

    def test_returns_empty_string_if_nothing_found(self):
        entry = {}
        assert get_category_from_entry(entry) == ""

    def test_ignores_unknown_function(self):
        entry = {
            "function": "Unknown",
            "operator": "Real Category"
        }
        assert get_category_from_entry(entry) == "Real Category"

    def test_strips_whitespace(self):
        entry = {
            "function": "  AI Crawler  "
        }
        assert get_category_from_entry(entry) == "AI Crawler"


class TestFetchAiRobots:
    """Test the main fetch function"""

    @patch('fetch_ai_robots.requests.get')
    def test_fetch_handles_list_format(self, mock_get, sample_ai_robots_response, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ai_robots_response
        mock_get.return_value = mock_response

        from fetch_ai_robots import fetch_ai_robots
        bots = fetch_ai_robots()

        assert len(bots) == 2
        assert bots[0]["user_agent"] == "ExampleBot"
        # Should use function field as operator
        assert bots[0]["operator"] == "AI Crawler"
        # Should clean markdown from operator
        assert bots[1]["operator"] == "SEO"

    @patch('fetch_ai_robots.requests.get')
    def test_fetch_handles_connection_error(self, mock_get, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        # Mock connection error
        mock_get.side_effect = Exception("Connection failed")

        from fetch_ai_robots import fetch_ai_robots
        bots = fetch_ai_robots()

        assert bots == []

    @patch('fetch_ai_robots.requests.get')
    def test_fetch_saves_to_staging(self, mock_get, sample_ai_robots_response, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_ai_robots_response
        mock_get.return_value = mock_response

        from fetch_ai_robots import fetch_ai_robots
        fetch_ai_robots()

        output_file = staging_dir / "ai_robots_bots.json"
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)
            assert len(data) == 2
