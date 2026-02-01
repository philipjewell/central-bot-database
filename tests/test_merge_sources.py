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

    def test_adds_missing_description(self):
        """Test that description gets added when missing"""
        existing = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "description": ""
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["ai-robots-txt"],
            "description": "New description"
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=True)
        assert merged["description"] == "New description"

    def test_preserves_existing_description(self):
        """Test that existing description is preserved"""
        existing = {
            "user_agent": "TestBot",
            "sources": ["manual"],
            "description": "Existing description"
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["ai-robots-txt"],
            "description": "New description"
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=True)
        assert merged["description"] == "Existing description"

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

        # Timestamp should NOT be updated when nothing changed
        assert merged["last_updated"] == "2025-01-01T00:00:00Z"

    def test_no_timestamp_update_for_reordered_sources(self):
        """Test that reordering sources doesn't trigger timestamp update"""
        existing = {
            "user_agent": "TestBot",
            "sources": ["cloudflare-radar", "ai-robots-txt"],  # Different order
            "description": "Same description",
            "last_updated": "2025-01-01T00:00:00Z"
        }
        new = {
            "user_agent": "TestBot",
            "sources": ["ai-robots-txt", "cloudflare-radar"],  # Different order
            "description": "Same description"
        }

        merged = merge_bot_entries(existing, new, preserve_enrichment=False)

        # Timestamp should NOT be updated - sources are the same, just different order
        assert merged["last_updated"] == "2025-01-01T00:00:00Z"
        # Sources should remain unchanged (same as existing, not re-sorted)
        assert merged["sources"] == ["cloudflare-radar", "ai-robots-txt"]


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

    def test_load_existing_database_invalid_json(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        db_file = data_dir / "bots.json"
        db_file.write_text("invalid json {")

        bots = load_existing_database()
        assert bots == []
        captured = capsys.readouterr()
        assert "Error loading" in captured.out

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

    def test_load_manual_bots_single_object(self, tmp_path, monkeypatch, sample_bot):
        """Test loading a single bot object (not array)"""
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        manual_file = sources_dir / "single_bot.json"
        manual_file.write_text(json.dumps(sample_bot))

        bots = load_manual_bots()
        assert len(bots) == 1
        assert "manual" in bots[0]["sources"]

    def test_load_manual_bots_no_operator(self, tmp_path, monkeypatch):
        """Test that bots without operator get 'Other' as default"""
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        bot_without_operator = {
            "user_agent": "TestBot",
            "sources": ["manual"]
        }

        manual_file = sources_dir / "bot.json"
        manual_file.write_text(json.dumps([bot_without_operator]))

        bots = load_manual_bots()
        assert bots[0]["operator"] == "Other"

    def test_load_manual_bots_invalid_json(self, tmp_path, monkeypatch, capsys):
        """Test handling of invalid JSON files"""
        monkeypatch.chdir(tmp_path)
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        bad_file = sources_dir / "bad.json"
        bad_file.write_text("invalid json {")

        bots = load_manual_bots()
        assert bots == []
        captured = capsys.readouterr()
        assert "Error parsing" in captured.out

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

    def test_load_staging_bots_adds_default_operator(self, tmp_path, monkeypatch):
        """Test that staging bots without operator get 'Other'"""
        monkeypatch.chdir(tmp_path)
        staging_dir = tmp_path / "staging"
        staging_dir.mkdir()

        bot_without_operator = {
            "user_agent": "StagingBot",
            "sources": ["cloudflare-radar"]
        }

        staging_file = staging_dir / "cloudflare_bots.json"
        staging_file.write_text(json.dumps([bot_without_operator]))

        bots = load_staging_bots()
        assert bots[0]["operator"] == "Other"


class TestCloudflarFieldProtection:
    """Test that CF-specific fields are protected from manual overwrites"""

    def test_cf_traffic_percentage_protected_from_manual(self):
        """Test that manual sources cannot overwrite cf_traffic_percentage"""
        # Existing bot from Cloudflare with traffic data
        existing = {
            "user_agent": "TestBot",
            "operator": "Testing",
            "sources": ["cloudflare-radar"],
            "raw_data": {
                "cf_traffic_percentage": "0.05",
                "bot_name": "TestBot"
            }
        }

        # Manual submission trying to overwrite CF data
        manual = {
            "user_agent": "TestBot",
            "operator": "Testing",
            "sources": ["manual"],
            "raw_data": {
                "cf_traffic_percentage": "0.99",  # Trying to inflate traffic
                "asn": "AS12345"
            }
        }

        merged = merge_bot_entries(existing, manual)

        # Should preserve CF traffic percentage, ignore manual attempt
        assert merged["raw_data"]["cf_traffic_percentage"] == "0.05"
        # Should still merge other fields
        assert merged["raw_data"]["asn"] == "AS12345"
        assert "cloudflare-radar" in merged["sources"]
        assert "manual" in merged["sources"]

    def test_cf_traffic_percentage_updated_by_cloudflare(self):
        """Test that Cloudflare sources CAN update cf_traffic_percentage"""
        # Existing bot from Cloudflare
        existing = {
            "user_agent": "TestBot",
            "operator": "Testing",
            "sources": ["cloudflare-radar"],
            "raw_data": {
                "cf_traffic_percentage": "0.05",
                "bot_name": "TestBot"
            }
        }

        # New Cloudflare data with updated traffic
        new_cf = {
            "user_agent": "TestBot",
            "operator": "Testing",
            "sources": ["cloudflare-radar"],
            "raw_data": {
                "cf_traffic_percentage": "0.10",  # Traffic increased
                "bot_name": "TestBot"
            }
        }

        merged = merge_bot_entries(existing, new_cf)

        # Should update CF traffic percentage from CF source
        assert merged["raw_data"]["cf_traffic_percentage"] == "0.10"

    def test_manual_bot_with_cf_traffic_ignored(self):
        """Test that manual submissions with cf_traffic_percentage are ignored"""
        # No existing bot
        existing = {
            "user_agent": "NewBot",
            "operator": "Testing",
            "sources": [],
            "raw_data": {}
        }

        # Manual submission trying to set CF-specific field
        manual = {
            "user_agent": "NewBot",
            "operator": "Testing",
            "sources": ["manual"],
            "raw_data": {
                "cf_traffic_percentage": "0.99",  # Invalid - manual can't set this
                "asn": "AS12345"
            }
        }

        merged = merge_bot_entries(existing, manual)

        # Should NOT have cf_traffic_percentage (manual can't set it)
        assert "cf_traffic_percentage" not in merged["raw_data"]
        # Should still have other fields
        assert merged["raw_data"]["asn"] == "AS12345"

    def test_mixed_sources_preserves_cf_data(self):
        """Test that merging manual into CF bot preserves CF-specific data"""
        # Bot from both Cloudflare and manual
        existing = {
            "user_agent": "TestBot",
            "operator": "Testing",
            "sources": ["cloudflare-radar", "manual"],
            "raw_data": {
                "cf_traffic_percentage": "0.05",
                "bot_name": "TestBot",
                "asn": "AS12345"
            }
        }

        # Manual update trying to change CF data
        manual = {
            "user_agent": "TestBot",
            "operator": "Testing",
            "sources": ["manual"],
            "raw_data": {
                "cf_traffic_percentage": "0.99",  # Should be ignored
                "ip_ranges": ["192.0.2.0/24"]
            }
        }

        merged = merge_bot_entries(existing, manual)

        # CF data should be preserved
        assert merged["raw_data"]["cf_traffic_percentage"] == "0.05"
        # Other fields should merge
        assert merged["raw_data"]["ip_ranges"] == ["192.0.2.0/24"]
