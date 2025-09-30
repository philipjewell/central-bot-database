"""
Fetch bot definitions from ai.robots.txt repository
"""
import json
import requests
from pathlib import Path

def fetch_ai_robots():
    """Fetch the robots.txt data from ai.robots.txt repo"""
    
    # URL to the raw ai.robots.txt data
    url = "https://raw.githubusercontent.com/ai-robots-txt/ai.robots.txt/main/robots.json"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Transform to our internal format
        bots = []
        for entry in data:
            bot = {
                "user_agent": entry.get("user_agent", ""),
                "operator": entry.get("company", entry.get("operator", "")),
                "description": entry.get("description", ""),
                "website": entry.get("website", ""),
                "sources": ["ai-robots-txt"],
                "raw_data": {
                    "ip_ranges": entry.get("ip_ranges", []),
                    "asn": entry.get("asn", ""),
                    "asn_list": entry.get("asn_list", []),
                    "verification_method": entry.get("verification_method", ""),
                    "original": entry  # Keep full original for reference
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

if __name__ == "__main__":
    fetch_ai_robots()
