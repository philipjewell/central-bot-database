"""
Fetch bot definitions from ai.robots.txt repository
"""
import json
import requests
from pathlib import Path

def fetch_ai_robots():
    """Fetch the robots.txt data from ai.robots.txt repo"""
    
    # URL to the raw ai.robots.txt data
    # Try the main file first
    url = "https://raw.githubusercontent.com/ai-robots-txt/ai.robots.txt/main/robots.json"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Transform to our internal format
        bots = []
        
        # Handle different data formats
        if isinstance(data, list):
            # If it's a list, iterate through entries
            for entry in data:
                if isinstance(entry, str):
                    # Simple string format - just user agent
                    bot = {
                        "user_agent": entry,
                        "operator": "",
                        "description": "",
                        "website": "",
                        "sources": ["ai-robots-txt"],
                        "raw_data": {
                            "ip_ranges": [],
                            "asn": "",
                            "asn_list": [],
                            "verification_method": "",
                            "original": entry
                        }
                    }
                    bots.append(bot)
                elif isinstance(entry, dict):
                    # Dictionary format with more details
                    bot = {
                        "user_agent": entry.get("user_agent", entry.get("agent", entry.get("name", ""))),
                        "operator": "",  # This will get replaced once we get more data
                        "owner": entry.get("owner", ""),
                        "description": entry.get("description", ""),
                        "website": entry.get("website", entry.get("url", "")),
                        "sources": ["ai-robots-txt"],
                        "raw_data": {
                            "ip_ranges": entry.get("ip_ranges", []),
                            "asn": entry.get("asn", ""),
                            "asn_list": entry.get("asn_list", []),
                            "verification_method": entry.get("verification_method", ""),
                            "original": entry
                        }
                    }
                    bots.append(bot)
        elif isinstance(data, dict):
            # If it's a dict, check for different structures
            if "bots" in data:
                # Data has a 'bots' key
                for entry in data["bots"]:
                    if isinstance(entry, str):
                        bot = {
                            "user_agent": entry,
                            "operator": "",
                            "description": "",
                            "website": "",
                            "sources": ["ai-robots-txt"],
                            "raw_data": {
                                "ip_ranges": [],
                                "asn": "",
                                "asn_list": [],
                                "verification_method": "",
                                "original": entry
                            }
                        }
                        bots.append(bot)
                    elif isinstance(entry, dict):
                        bot = {
                            "user_agent": entry.get("user_agent", entry.get("agent", entry.get("name", ""))),
                            "operator": entry.get("company", entry.get("operator", entry.get("owner", ""))),
                            "description": entry.get("description", ""),
                            "website": entry.get("website", entry.get("url", "")),
                            "sources": ["ai-robots-txt"],
                            "raw_data": {
                                "ip_ranges": entry.get("ip_ranges", []),
                                "asn": entry.get("asn", ""),
                                "asn_list": entry.get("asn_list", []),
                                "verification_method": entry.get("verification_method", ""),
                                "original": entry
                            }
                        }
                        bots.append(bot)
            else:
                # Dict where keys might be bot names
                for key, value in data.items():
                    if isinstance(value, dict):
                        bot = {
                            "user_agent": value.get("user_agent", key),
                            "operator": value.get("company", value.get("operator", "")),
                            "description": value.get("description", ""),
                            "website": value.get("website", ""),
                            "sources": ["ai-robots-txt"],
                            "raw_data": {
                                "ip_ranges": value.get("ip_ranges", []),
                                "asn": value.get("asn", ""),
                                "asn_list": value.get("asn_list", []),
                                "verification_method": value.get("verification_method", ""),
                                "original": value
                            }
                        }
                        bots.append(bot)
        
        # Save to staging area
        staging_dir = Path("staging")
        staging_dir.mkdir(exist_ok=True)
        
        output_file = staging_dir / "ai_robots_bots.json"
        with open(output_file, 'w') as f:
            json.dump(bots, f, indent=2)
        
        print(f"✓ Fetched {len(bots)} bots from ai.robots.txt")
        return bots
        
    except requests.RequestException as e:
        print(f"✗ Error fetching from ai.robots.txt: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON from ai.robots.txt: {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []

if __name__ == "__main__":
    fetch_ai_robots()
