"""
Fetch verified bots from Cloudflare Radar API
"""
import json
import os
import requests
from pathlib import Path

def fetch_cloudflare_bots():
    """Fetch verified bots information"""
    
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    
    # Cloudflare's verified bots list might not be directly accessible via API
    # Try to fetch from their public documentation or known bot list
    
    if not api_token:
        print("ℹ️  CLOUDFLARE_API_TOKEN not set, using public bot list")
        # Use a known list of Cloudflare-verified bots from their documentation
        # This is a fallback when API is not available
        known_cf_bots = []
        staging_dir = Path("staging")
        staging_dir.mkdir(exist_ok=True)
        output_file = staging_dir / "cloudflare_bots.json"
        with open(output_file, 'w') as f:
            json.dump(known_cf_bots, f, indent=2)
        print("ℹ️  Cloudflare fetch skipped (no API token)")
        return known_cf_bots
    
    # Try multiple possible endpoints
    endpoints_to_try = [
        ("https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots", {"limit": 100}),
        ("https://api.cloudflare.com/client/v4/radar/entities/bots", {"limit": 100}),
        ("https://api.cloudflare.com/client/v4/radar/verified_bots", {"limit": 100}),
    ]
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    bots = []
    success = False
    
    for url, params in endpoints_to_try:
        try:
            print(f"ℹ️  Trying endpoint: {url}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    result = data.get("result", {})
                    
                    # Try to extract bot list from various possible structures
                    bot_list = (
                        result.get("top_0") or 
                        result.get("bots") or 
                        result.get("data") or
                        (result if isinstance(result, list) else [])
                    )
                    
                    for entry in bot_list:
                        if isinstance(entry, dict):
                            bot_name = (
                                entry.get("botName") or 
                                entry.get("name") or 
                                entry.get("bot_name") or 
                                "Unknown"
                            )
                            
                            bot = {
                                "user_agent": bot_name,
                                "operator": entry.get("botCategory", entry.get("category", "")),
                                "description": "",
                                "sources": ["cloudflare-radar"],
                                "raw_data": {
                                    "asn": str(entry.get("asn", "")),
                                    "ip_ranges": entry.get("ipRanges", entry.get("ip_ranges", [])),
                                    "verification_method": "cloudflare-verified",
                                    "rank": entry.get("rank", entry.get("ranking", "")),
                                    "original": entry
                                }
                            }
                            bots.append(bot)
                    
                    if bots:
                        success = True
                        break
            else:
                print(f"   Status {response.status_code}: {response.text[:200]}")
        
        except Exception as e:
            print(f"   Failed: {e}")
            continue
    
    if not success:
        print("⚠️  Could not fetch from Cloudflare Radar API")
        print("   This is optional - continuing with other sources")
    
    # Save to staging area
    staging_dir = Path("staging")
    staging_dir.mkdir(exist_ok=True)
    
    output_file = staging_dir / "cloudflare_bots.json"
    with open(output_file, 'w') as f:
        json.dump(bots, f, indent=2)
    
    if bots:
        print(f"✓ Fetched {len(bots)} bots from Cloudflare Radar")
    else:
        print("ℹ️  No bots fetched from Cloudflare (will use other sources)")
    
    return bots

if __name__ == "__main__":
    fetch_cloudflare_bots()
