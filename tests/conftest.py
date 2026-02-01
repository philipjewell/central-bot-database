"""
Pytest configuration and shared fixtures
"""
import pytest
import json
from pathlib import Path
from datetime import datetime


@pytest.fixture
def sample_bot():
    """Sample bot entry for testing"""
    return {
        "user_agent": "TestBot/1.0",
        "operator": "Test Company",
        "description": "A test bot for testing",
        "purpose": "Testing purposes",
        "impact_of_blocking": "Tests will fail",
        "website": "https://example.com/testbot",
        "categories": {
            "ecommerce": "beneficial",
            "news": "neutral",
            "media": "beneficial",
            "blog": "beneficial",
            "saas": "neutral",
            "corporate": "beneficial",
            "documentation": "beneficial",
            "social": "not_applicable",
            "portfolio": "beneficial",
            "government": "neutral"
        },
        "sources": ["manual"],
        "raw_data": {
            "ip_ranges": ["192.0.2.0/24"],
            "asn": "AS64496",
            "verification_method": "DNS reverse lookup"
        },
        "last_updated": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_ai_robots_response():
    """Sample response from ai.robots.txt"""
    return {
        "bots": [
            {
                "user_agent": "ExampleBot",
                "operator": "Example Company",
                "function": "AI Crawler",
                "description": "Example bot description",
                "respect": "Yes",
                "frequency": "Daily"
            },
            {
                "user_agent": "TestCrawler",
                "operator": "[TestCompany](https://test.com)",
                "function": "SEO",
                "description": "SEO crawler",
                "respect": "Yes",
                "frequency": "Weekly"
            }
        ]
    }


@pytest.fixture
def sample_cloudflare_response():
    """Sample response from Cloudflare Radar API"""
    return {
        "success": True,
        "result": {
            "top": [
                {
                    "botName": "CloudBot",
                    "botCategory": "Monitoring & Analytics",
                    "botOwner": "Cloudflare",
                    "value": "0.123",
                    "userAgentPatterns": ["CloudBot/1.0", "CloudBot/2.0"]
                },
                {
                    "botName": "VerifiedBot",
                    "botCategory": "Search Engine Crawler",
                    "botOwner": "SearchCo",
                    "value": "0.456",
                    "userAgentPatterns": "VerifiedBot/1.0"
                }
            ]
        }
    }


@pytest.fixture
def temp_staging_dir(tmp_path):
    """Create temporary staging directory"""
    staging = tmp_path / "staging"
    staging.mkdir()
    return staging


@pytest.fixture
def temp_sources_dir(tmp_path):
    """Create temporary sources directory"""
    sources = tmp_path / "sources"
    sources.mkdir()
    return sources


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory"""
    data = tmp_path / "data"
    data.mkdir()
    return data
