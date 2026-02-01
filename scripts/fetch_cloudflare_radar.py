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
    
    # Cloudflare API limit - fetches top 250 most common verified bots
    # Note: This does not fetch ALL bots from Cloudflare, only the top N by traffic
    CLOUDFLARE_BOT_LIMIT = 250

    # Try multiple possible endpoints with proper date ranges
    endpoints_to_try = [
        (
            "https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots",
            {
                "limit": CLOUDFLARE_BOT_LIMIT,
                "dateStart": date_from,
                "dateEnd": date_to,
                "format": "json"
            }
        ),
        (
            "https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots",
            {
                "limit": CLOUDFLARE_BOT_LIMIT,
                "dateRange": "7d"
            }
        ),
        (
            "https://api.cloudflare.com/client/v4/radar/verified_bots/top/bots",
            {
                "limit": CLOUDFLARE_BOT_LIMIT,
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
                            # Extract user agent patterns - prefer userAgentPatterns over botName
                            user_agent_patterns = entry.get("userAgentPatterns", entry.get("user_agent_patterns", []))

                            # Determine the user_agent to use
                            if user_agent_patterns:
                                # If patterns exist, use the first one as the primary user_agent
                                if isinstance(user_agent_patterns, list) and len(user_agent_patterns) > 0:
                                    user_agent = user_agent_patterns[0]
                                elif isinstance(user_agent_patterns, str):
                                    user_agent = user_agent_patterns
                                else:
                                    # Fallback if patterns exist but are empty
                                    user_agent = entry.get("botName", entry.get("name", entry.get("bot_name", entry.get("clientName", "Unknown"))))
                            else:
                                # Fallback to bot name if no patterns available
                                user_agent = (
                                    entry.get("botName") or
                                    entry.get("name") or
                                    entry.get("bot_name") or
                                    entry.get("clientName") or
                                    "Unknown"
                                )

                            # Skip if we couldn't find a user agent
                            if user_agent == "Unknown":
                                continue

                            bot = {
                                "user_agent": user_agent,
                                "operator": entry.get("botCategory", entry.get("category", "")),
                                "description": entry.get("description", ""),
                                "sources": ["cloudflare-radar"],
                                "raw_data": {
                                    "asn": str(entry.get("asn", "")),
                                    "ip_ranges": entry.get("ipRanges", entry.get("ip_ranges", [])),
                                    "verification_method": "cloudflare-verified",
                                    "cf_traffic_percentage": entry.get("value", ""),
                                    "bot_name": entry.get("botName", entry.get("name", "")),
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
