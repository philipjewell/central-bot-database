"""
Tests for bot comparison logic (bot_has_changed function)
"""
import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from merge_sources import bot_has_changed


class TestBotHasChanged:
    """Test bot change detection"""

    def test_no_changes(self):
        """Test that identical bots show no changes"""
        bot1 = {
            "user_agent": "TestBot",
            "operator": "Test Co",
            "description": "A test bot",
            "sources": ["manual"],
            "raw_data": {"asn": "AS123"},
            "purpose": "Testing",
            "impact_of_blocking": "Tests fail",
            "categories": {"ecommerce": "beneficial"}
        }
        bot2 = bot1.copy()
        bot2["raw_data"] = bot1["raw_data"].copy()
        bot2["categories"] = bot1["categories"].copy()

        assert bot_has_changed(bot1, bot2) is False

    def test_user_agent_changed(self):
        """Test that user_agent change is detected"""
        bot1 = {"user_agent": "TestBot"}
        bot2 = {"user_agent": "NewBot"}

        assert bot_has_changed(bot1, bot2) is True

    def test_operator_changed(self):
        """Test that operator change is detected"""
        bot1 = {"operator": "Old Company"}
        bot2 = {"operator": "New Company"}

        assert bot_has_changed(bot1, bot2) is True

    def test_description_changed(self):
        """Test that description change is detected"""
        bot1 = {"description": "Old description"}
        bot2 = {"description": "New description"}

        assert bot_has_changed(bot1, bot2) is True

    def test_purpose_changed(self):
        """Test that purpose change is detected"""
        bot1 = {"purpose": "Old purpose"}
        bot2 = {"purpose": "New purpose"}

        assert bot_has_changed(bot1, bot2) is True

    def test_impact_changed(self):
        """Test that impact_of_blocking change is detected"""
        bot1 = {"impact_of_blocking": "Old impact"}
        bot2 = {"impact_of_blocking": "New impact"}

        assert bot_has_changed(bot1, bot2) is True

    def test_sources_added(self):
        """Test that adding a source is detected"""
        bot1 = {"sources": ["manual"]}
        bot2 = {"sources": ["manual", "cloudflare-radar"]}

        assert bot_has_changed(bot1, bot2) is True

    def test_sources_reordered(self):
        """Test that reordering sources is NOT detected as change"""
        bot1 = {"sources": ["cloudflare-radar", "ai-robots-txt"]}
        bot2 = {"sources": ["ai-robots-txt", "cloudflare-radar"]}

        assert bot_has_changed(bot1, bot2) is False

    def test_categories_changed(self):
        """Test that category change is detected"""
        bot1 = {"categories": {"ecommerce": "beneficial"}}
        bot2 = {"categories": {"ecommerce": "harmful"}}

        assert bot_has_changed(bot1, bot2) is True

    def test_categories_added(self):
        """Test that adding a category is detected"""
        bot1 = {"categories": {"ecommerce": "beneficial"}}
        bot2 = {"categories": {"ecommerce": "beneficial", "news": "neutral"}}

        assert bot_has_changed(bot1, bot2) is True

    def test_raw_data_changed(self):
        """Test that raw_data change is detected"""
        bot1 = {"raw_data": {"asn": "AS123"}}
        bot2 = {"raw_data": {"asn": "AS456"}}

        assert bot_has_changed(bot1, bot2) is True

    def test_raw_data_field_added(self):
        """Test that adding a field to raw_data is detected"""
        bot1 = {"raw_data": {"asn": "AS123"}}
        bot2 = {"raw_data": {"asn": "AS123", "verification_method": "DNS"}}

        assert bot_has_changed(bot1, bot2) is True

    def test_ip_ranges_added(self):
        """Test that adding IP ranges is detected"""
        bot1 = {"raw_data": {"ip_ranges": ["192.0.2.0/24"]}}
        bot2 = {"raw_data": {"ip_ranges": ["192.0.2.0/24", "198.51.100.0/24"]}}

        assert bot_has_changed(bot1, bot2) is True

    def test_ip_ranges_reordered(self):
        """Test that reordering IP ranges is NOT detected as change"""
        bot1 = {"raw_data": {"ip_ranges": ["198.51.100.0/24", "192.0.2.0/24"]}}
        bot2 = {"raw_data": {"ip_ranges": ["192.0.2.0/24", "198.51.100.0/24"]}}

        assert bot_has_changed(bot1, bot2) is False

    def test_last_updated_ignored(self):
        """Test that last_updated is not compared"""
        bot1 = {"user_agent": "TestBot", "last_updated": "2025-01-01T00:00:00Z"}
        bot2 = {"user_agent": "TestBot", "last_updated": "2025-12-31T23:59:59Z"}

        assert bot_has_changed(bot1, bot2) is False

    def test_empty_to_populated(self):
        """Test that going from empty to populated is detected"""
        bot1 = {"purpose": ""}
        bot2 = {"purpose": "New purpose"}

        assert bot_has_changed(bot1, bot2) is True

    def test_none_to_value(self):
        """Test that going from None to value is detected"""
        bot1 = {"purpose": None}
        bot2 = {"purpose": "New purpose"}

        assert bot_has_changed(bot1, bot2) is True

    def test_missing_to_present(self):
        """Test that adding a new field is detected"""
        bot1 = {}
        bot2 = {"purpose": "New purpose"}

        assert bot_has_changed(bot1, bot2) is True
