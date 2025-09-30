"""
Fetch verified bots from Cloudflare Radar API
"""
import json
import os
import requests
from pathlib import Path

def fetch_cloudflare_bots():
    """Fetch top verified bots from Cloudflare Radar"""
    
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    if not api_token:
        print("✗ CLOUDFLARE_API_TOKEN not set, skipping Cloudflare fetch")
        return []
    
    # Cloudflare Radar API endpoint for verified bots
    url = "https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "limit": 200,
        "format": "json"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Transform to our internal format
        bots = []
        
        if data.get("success") and "result" in data:
            for entry in data["result"].get("top_0", []):
                bot = {
                    "user_agent": entry.get("botName", ""),
                    "operator": entry.get("botCategory", ""),
                    "description": "",  # Cloudflare doesn't provide descriptions
                    "sources": ["cloudflare-radar"],
                    "raw_data": {
                        "asn": entry.get("asn", ""),
                        "ip_ranges": entry.get("ipRanges", []),
                        "verification_method": "cloudflare-verified",
                        "rank": entry.get("rank", ""),
                        "original": entry
                    }
                }
                bots.append(bot)
        
        # Save to staging area
        staging_dir = Path("staging")
        staging_dir.mkdir(exist_ok=True)
        
        output_file = staging_dir / "cloudflare_bots.json"
        with open(output_file, 'w') as f:
            json.dump(bots, f, indent=2)
        
        print(f"✓ Fetched {len(bots)} bots from Cloudflare Radar")
        return bots
        
    except requests.RequestException as e:
        print(f"✗ Error fetching from Cloudflare Radar: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON from Cloudflare: {e}")
        return []

if __name__ == "__main__":
    fetch_cloudflare_bots()
