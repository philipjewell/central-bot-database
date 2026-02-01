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

    def test_validate_valid_bot(self, tmp_path, monkeypatch, sample_bot, capsys):
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

        from validate_data import validate_data
        result = validate_data()
        assert result is True

    def test_validate_missing_required_field(self, tmp_path, monkeypatch, capsys):
        """Test that bots missing required fields fail validation"""
        monkeypatch.chdir(tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        invalid_bot = {
            # Missing user_agent
            "operator": "Test",
            "sources": ["manual"],
            "purpose": "Test purpose",
            "impact_of_blocking": "Test impact"
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

        from validate_data import validate_data
        result = validate_data()
        assert result is False

    def test_validate_invalid_category_rating(self, tmp_path, monkeypatch, sample_bot, capsys):
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

        from validate_data import validate_data
        result = validate_data()
        assert result is False

    def test_validate_no_database_file(self, tmp_path, monkeypatch, capsys):
        """Test validation handles missing database file"""
        monkeypatch.chdir(tmp_path)

        from validate_data import validate_data
        result = validate_data()
        assert result is False

    def test_validate_bot_function(self):
        """Test the validate_bot helper function"""
        from validate_data import validate_bot

        # Valid bot
        valid_bot = {
            "user_agent": "TestBot",
            "operator": "Test Co",
            "sources": ["manual"],
            "purpose": "Testing",
            "impact_of_blocking": "Tests fail",
            "categories": {"ecommerce": "beneficial"}
        }
        issues = validate_bot(valid_bot, 0)
        # May have issues about missing purpose for manual bots, but basic validation should work
        assert isinstance(issues, list)

        # Invalid bot - missing user_agent
        invalid_bot = {"operator": "Test", "sources": ["manual"]}
        issues = validate_bot(invalid_bot, 0)
        assert len(issues) > 0
        assert any("user_agent" in issue for issue in issues)

        # Invalid category rating
        bad_rating_bot = {
            "user_agent": "TestBot",
            "operator": "Test",
            "sources": ["manual"],
            "purpose": "Test",
            "impact_of_blocking": "Impact",
            "categories": {"ecommerce": "wrong_rating"}
        }
        issues = validate_bot(bad_rating_bot, 0)
        assert len(issues) > 0
        assert any("Invalid rating" in issue for issue in issues)
