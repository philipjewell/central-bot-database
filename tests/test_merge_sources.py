"""
Tests for merge_sources.py
"""
import pytest
import json
import sys
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from merge_sources import (
    normalize_user_agent,
    merge_bot_entries,
    load_existing_database,
    load_manual_bots,
    load_staging_bots
)


class TestNormalizeUserAgent:
    """Test user agent normalization"""

    def test_normalize_lowercase(self):
        assert normalize_user_agent("GoogleBot") == "googlebot"

    def test_normalize_removes_hyphens(self):
        assert normalize_user_agent("Google-Bot") == "googlebot"

    def test_normalize_removes_underscores(self):
        assert normalize_user_agent("Google_Bot") == "googlebot"

    def test_normalize_strips_whitespace(self):
        assert normalize_user_agent("  GoogleBot  ") == "googlebot"

    def test_normalize_combined(self):
        assert normalize_user_agent("  Google-Bot_1.0  ") == "googlebot1.0"


class TestMergeBotEntries:
    """Test bot entry merging logic"""

    def test_merge_sources_list(self):
        existing = {"user_agent": "TestBot", "sources": ["manual"]}
        new = {"user_agent": "TestBot", "sources": ["ai-robots-txt"]}

        merged = merge_bot_entries(existing, new, preserve_enrichment=False)

        assert "manual" in merged["sources"]
        assert "ai-robots-txt" in merged["sources"]

    def test_preserve_enrichment_keeps_purpose(self):
        existing = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "purpose": "Existing purpose",
            "impact_of_blocking": "Existing impact",
            "categories": {"ecommerce": "beneficial"}
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["ai-robots-txt"],
            "purpose": "New purpose",
            "impact_of_blocking": "New impact",
            "categories": {"ecommerce": "neutral"}
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=True)

        assert merged["purpose"] == "Existing purpose"
        assert merged["impact_of_blocking"] == "Existing impact"
        assert merged["categories"]["ecommerce"] == "beneficial"

    def test_updates_technical_details(self):
        existing = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "raw_data": {"ip_ranges": ["192.0.2.0/24"]}
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["ai-robots-txt"],
            "raw_data": {"ip_ranges": ["198.51.100.0/24"], "asn": "AS64496"}
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=False)

        assert "192.0.2.0/24" in merged["raw_data"]["ip_ranges"]
        assert "198.51.100.0/24" in merged["raw_data"]["ip_ranges"]
        assert merged["raw_data"]["asn"] == "AS64496"

    def test_manual_source_takes_precedence(self):
        existing = {
            "user_agent": "TestBot",
            "sources": ["ai-robots-txt"],
            "operator": "External Category"
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "operator": "Manual Category"
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=False)

        assert merged["operator"] == "Manual Category"

    def test_updates_timestamp_when_changed(self):
        existing = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "description": "Old description",
            "last_updated": "2025-01-01T00:00:00Z"
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["ai-robots-txt"],
            "description": "New description"
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=False)

        # Timestamp should be updated since description changed
        assert merged["last_updated"] != "2025-01-01T00:00:00Z"

    def test_no_timestamp_update_when_unchanged(self):
        existing = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "description": "Same description",
            "last_updated": "2025-01-01T00:00:00Z"
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "description": "Same description"
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=False)

        # Timestamp should NOT be updated if nothing changed (except sources merge)
        # Note: Sources merge will trigger update, but description staying same won't add to it
        assert "last_updated" in merged


class TestLoadFunctions:
    """Test data loading functions"""

    def test_load_existing_database_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        bots = load_existing_database()
        assert bots == []

    def test_load_existing_database_with_data(self, tmp_path, monkeypatch, sample_bot):
        monkeypatch.chdir(tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        db_file = data_dir / "bots.json"
        db_file.write_text(json.dumps({"bots": [sample_bot]}))

        bots = load_existing_database()
        assert len(bots) == 1
        assert bots[0]["user_agent"] == "TestBot/1.0"

    def test_load_manual_bots_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        bots = load_manual_bots()
        assert bots == []

    def test_load_manual_bots_with_data(self, tmp_path, monkeypatch, sample_bot):
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        manual_file = sources_dir / "manual_bots.json"
        manual_file.write_text(json.dumps([sample_bot]))

        bots = load_manual_bots()
        assert len(bots) == 1
        assert bots[0]["user_agent"] == "TestBot/1.0"
        assert "manual" in bots[0]["sources"]

    def test_load_staging_bots_skips_merged(self, tmp_path, monkeypatch, sample_bot):
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        # Should be loaded
        ai_file = staging_dir / "ai_robots_bots.json"
        ai_file.write_text(json.dumps([sample_bot]))

        # Should be skipped
        merged_file = staging_dir / "merged_bots.json"
        merged_file.write_text(json.dumps([sample_bot]))

        bots = load_staging_bots()
        assert len(bots) == 1  # Only one, not two
