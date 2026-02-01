"""
Tests for validate_data.py
"""
import pytest
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class TestValidateData:
    """Test data validation"""

    def test_validate_valid_bot(self, tmp_path, monkeypatch, sample_bot):
        """Test that valid bots pass validation"""
        monkeypatch.chdir(tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        db_file = data_dir / "bots.json"
        db_data = {
            "meta": {
                "generated_at": "2025-01-01T00:00:00Z",
                "version": "1.0",
                "total_bots": 1
            },
            "bots": [sample_bot]
        }
        db_file.write_text(json.dumps(db_data, indent=2))

        from validate_data import validate_bot_database
        result = validate_bot_database()
        assert result is True

    def test_validate_missing_required_field(self, tmp_path, monkeypatch):
        """Test that bots missing required fields fail validation"""
        monkeypatch.chdir(tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        invalid_bot = {
            # Missing user_agent
            "operator": "Test",
            "sources": ["manual"]
        }

        db_file = data_dir / "bots.json"
        db_data = {
            "meta": {
                "generated_at": "2025-01-01T00:00:00Z",
                "version": "1.0",
                "total_bots": 1
            },
            "bots": [invalid_bot]
        }
        db_file.write_text(json.dumps(db_data, indent=2))

        from validate_data import validate_bot_database
        result = validate_bot_database()
        assert result is False

    def test_validate_invalid_category_rating(self, tmp_path, monkeypatch, sample_bot):
        """Test that invalid category ratings fail validation"""
        monkeypatch.chdir(tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        invalid_bot = sample_bot.copy()
        invalid_bot["categories"] = {"ecommerce": "invalid_rating"}

        db_file = data_dir / "bots.json"
        db_data = {
            "meta": {
                "generated_at": "2025-01-01T00:00:00Z",
                "version": "1.0",
                "total_bots": 1
            },
            "bots": [invalid_bot]
        }
        db_file.write_text(json.dumps(db_data, indent=2))

        from validate_data import validate_bot_database
        result = validate_bot_database()
        assert result is False

    def test_validate_no_database_file(self, tmp_path, monkeypatch):
        """Test validation handles missing database file"""
        monkeypatch.chdir(tmp_path)

        from validate_data import validate_bot_database
        result = validate_bot_database()
        assert result is False
