"""
Fetch verified bots from Cloudflare Radar API
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta

def fetch_cloudflare_bots():
    """Fetch verified bots information"""
    
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    
    if not api_token:
        print("ℹ️  CLOUDFLARE_API_TOKEN not set, skipping Cloudflare fetch")
        staging_dir = Path("staging")
        staging_dir.mkdir(exist_ok=True)
        output_file = staging_dir / "cloudflare_bots.json"
        with open(output_file, 'w') as f:
            json.dump([], f, indent=2)
        return []
    
    # Calculate date range (last 7 days)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    date_from = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Try multiple possible endpoints with proper date ranges
    endpoints_to_try = [
        (
            "https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots",
            {
                "limit": 100,
                "dateStart": date_from,
                "dateEnd": date_to,
                "format": "json"
            }
        ),
        (
            "https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots",
            {
                "limit": 100,
                "dateRange": "7d"
            }
        ),
        (
            "https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots",
            {
                "limit": 100,
                "range": "7d"
            }
        ),
    ]
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    bots = []
    success = False
    
    for url, params in endpoints_to_try:
        try:
            print(f"ℹ️  Trying endpoint with params: {params}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    result = data.get("result", {})
                    
                    # Try to extract bot list from various possible structures
                    bot_list = []
                    
                    if "top" in result:
                        # Array of top items
                        bot_list = result.get("top", [])
                    elif "top_0" in result:
                        bot_list = result.get("top_0", [])
                    elif "bots" in result:
                        bot_list = result.get("bots", [])
                    elif "data" in result:
                        bot_list = result.get("data", [])
                    elif isinstance(result, list):
                        bot_list = result
                    
                    for entry in bot_list:
                        if isinstance(entry, dict):
                            # Extract bot name - try different possible fields
                            bot_name = (
                                entry.get("botName") or 
                                entry.get("name") or 
                                entry.get("bot_name") or
                                entry.get("clientName") or
                                "Unknown"
                            )
                            
                            # Skip if we couldn't find a name
                            if bot_name == "Unknown":
                                continue
                            
                            bot = {
                                "user_agent": bot_name,
                                "operator": entry.get("botCategory", entry.get("category", "")),
                                "description": entry.get("description", ""),
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
                        print(f"✓ Successfully fetched {len(bots)} bots!")
                        break
                    else:
                        print(f"   No bots found in response structure")
                else:
                    errors = data.get("errors", [])
                    if errors:
                        print(f"   API Error: {errors[0].get('message', 'Unknown error')}")
            else:
                try:
                    error_data = response.json()
                    print(f"   Status {response.status_code}: {error_data}")
                except:
                    print(f"   Status {response.status_code}: {response.text[:200]}")
        
        except Exception as e:
            print(f"   Failed: {e}")
            continue
    
    if not success:
        print("⚠️  Could not fetch from Cloudflare Radar API")
        print("   The API may require different authentication or parameters")
        print("   Continuing with other sources (ai.robots.txt + manual)")
    
    # Save to staging area (even if empty)
    staging_dir = Path("staging")
    staging_dir.mkdir(exist_ok=True)
    
    output_file = staging_dir / "cloudflare_bots.json"
    with open(output_file, 'w') as f:
        json.dump(bots, f, indent=2)
    
    if bots:
        print(f"✓ Saved {len(bots)} bots from Cloudflare Radar")
    else:
        print("ℹ️  No bots fetched from Cloudflare (will use other sources)")
    
    return bots

if __name__ == "__main__":
    fetch_cloudflare_bots()
