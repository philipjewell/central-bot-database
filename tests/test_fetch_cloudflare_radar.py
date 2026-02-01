"""
Tests for fetch_cloudflare_radar.py
"""
import pytest
import json
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestFetchCloudflareRadar:
    """Test Cloudflare Radar API fetching"""

    @patch('fetch_cloudflare_radar.requests.get')
    def test_fetch_with_user_agent_patterns_array(self, mock_get, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        # Set API token
        monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'test-token')

        # Mock successful response with userAgentPatterns as array
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "top": [
                    {
                        "botName": "TestBot",
                        "botCategory": "Testing",
                        "botOwner": "TestCo",
                        "value": "0.123",
                        "userAgentPatterns": ["TestBot/1.0", "TestBot/2.0"]
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        from fetch_cloudflare_radar import fetch_cloudflare_bots
        bots = fetch_cloudflare_bots()

        assert len(bots) == 1
        # Should use first pattern as user_agent
        assert bots[0]["user_agent"] == "TestBot/1.0"
        # Should store traffic percentage and bot name
        assert bots[0]["raw_data"]["cf_traffic_percentage"] == "0.123"
        assert bots[0]["raw_data"]["bot_name"] == "TestBot"
        # user_agent_patterns should NOT be stored
        assert "user_agent_patterns" not in bots[0]["raw_data"]

    @patch('fetch_cloudflare_radar.requests.get')
    def test_fetch_with_user_agent_patterns_string(self, mock_get, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'test-token')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "top": [
                    {
                        "botName": "TestBot",
                        "botCategory": "Testing",
                        "userAgentPatterns": "TestBot/1.0",
                        "value": "0.05"
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        from fetch_cloudflare_radar import fetch_cloudflare_bots
        bots = fetch_cloudflare_bots()

        assert bots[0]["user_agent"] == "TestBot/1.0"
        assert bots[0]["raw_data"]["cf_traffic_percentage"] == "0.05"
        # user_agent_patterns should NOT be stored
        assert "user_agent_patterns" not in bots[0]["raw_data"]

    @patch('fetch_cloudflare_radar.requests.get')
    def test_fetch_fallback_to_bot_name(self, mock_get, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'test-token')

        # Response without userAgentPatterns
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "top": [
                    {
                        "botName": "TestBot",
                        "botCategory": "Testing",
                        "value": "0.02"
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        from fetch_cloudflare_radar import fetch_cloudflare_bots
        bots = fetch_cloudflare_bots()

        # Should fall back to botName
        assert bots[0]["user_agent"] == "TestBot"
        assert bots[0]["raw_data"]["cf_traffic_percentage"] == "0.02"
        # user_agent_patterns should NOT be in raw_data
        assert "user_agent_patterns" not in bots[0]["raw_data"]

    def test_fetch_without_api_token(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        # No API token set
        monkeypatch.delenv('CLOUDFLARE_API_TOKEN', raising=False)

        from fetch_cloudflare_radar import fetch_cloudflare_bots
        bots = fetch_cloudflare_bots()

        # Should return empty list and create empty file
        assert bots == []
        output_file = staging_dir / "cloudflare_bots.json"
        assert output_file.exists()

    @patch('fetch_cloudflare_radar.requests.get')
    def test_fetch_handles_api_error(self, mock_get, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'test-token')

        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        from fetch_cloudflare_radar import fetch_cloudflare_bots
        bots = fetch_cloudflare_bots()

        assert bots == []

    @patch('fetch_cloudflare_radar.requests.get')
    def test_fetch_includes_cloudflare_source(self, mock_get, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'test-token')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "top": [{"botName": "TestBot", "botCategory": "Testing"}]
            }
        }
        mock_get.return_value = mock_response

        from fetch_cloudflare_radar import fetch_cloudflare_bots
        bots = fetch_cloudflare_bots()

        assert "cloudflare-radar" in bots[0]["sources"]
        assert bots[0]["raw_data"]["verification_method"] == "cloudflare-verified"
