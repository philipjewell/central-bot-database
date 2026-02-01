"""
Tests for category_mapper.py
"""
import pytest
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from category_mapper import CategoryMapper


class TestCategoryMapper:
    """Test category mapping functionality"""

    def test_cloudflare_category_not_mapped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        mapper = CategoryMapper()

        bot = {
            "operator": "AI Crawler",
            "sources": ["cloudflare-radar"]
        }

        # Cloudflare categories should be used as-is
        category = mapper.get_category_for_bot(bot)
        assert category == "AI Crawler"

    def test_manual_category_not_mapped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        mapper = CategoryMapper()

        bot = {
            "operator": "Custom Category",
            "sources": ["manual"]
        }

        # Manual categories should be used as-is
        category = mapper.get_category_for_bot(bot)
        assert category == "Custom Category"

    def test_external_category_gets_mapped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        # Create mapping file
        mappings = {
            "SEO Bot": "SEO Crawler"
        }
        mapping_file = schemas_dir / "category_mappings.json"
        mapping_file.write_text(json.dumps(mappings))

        mapper = CategoryMapper()

        bot = {
            "operator": "SEO Bot",
            "sources": ["ai-robots-txt"]
        }

        category = mapper.get_category_for_bot(bot)
        assert category == "SEO Crawler"

    def test_empty_category_returns_other(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        mapper = CategoryMapper()

        bot = {
            "operator": "",
            "sources": ["ai-robots-txt"]
        }

        category = mapper.get_category_for_bot(bot)
        assert category == "Other"

    def test_merge_categories_prefers_cloudflare(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        mapper = CategoryMapper()

        # Cloudflare should win over manual
        result = mapper.merge_categories(
            "Cloudflare Category", ["cloudflare-radar"],
            "Manual Category", ["manual"]
        )
        assert result == "Cloudflare Category"

        # Manual should win over other
        result = mapper.merge_categories(
            "External Category", ["ai-robots-txt"],
            "Manual Category", ["manual"]
        )
        assert result == "Manual Category"

    def test_normalize_category_applies_mapping(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        mappings = {
            "AI Bot": "AI Crawler"
        }
        mapping_file = schemas_dir / "category_mappings.json"
        mapping_file.write_text(json.dumps(mappings))

        mapper = CategoryMapper()
        normalized = mapper.normalize_category("AI Bot")
        assert normalized == "AI Crawler"

    def test_save_mappings_creates_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        mapper = CategoryMapper()
        mapper.mappings["Test"] = "Mapped"
        mapper.save_mappings()

        mapping_file = schemas_dir / "category_mappings.json"
        assert mapping_file.exists()

        with open(mapping_file) as f:
            data = json.load(f)
            assert data["Test"] == "Mapped"

    def test_default_mappings_exist(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        schemas_dir = tmp_path / "schemas"
        schemas_dir.mkdir()

        mapper = CategoryMapper()

        # Default mappings should exist
        assert mapper.mappings[""] == "Other"
        assert mapper.mappings["Other"] == "Other"
        assert mapper.mappings["Unknown"] == "Other"
