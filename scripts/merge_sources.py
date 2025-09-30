"""
Merge bot data from multiple sources and deduplicate
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

def normalize_user_agent(ua: str) -> str:
    """Normalize user agent strings for comparison"""
    return ua.lower().strip().replace('-', '').replace('_', '')

def load_manual_bots() -> List[Dict]:
    """Load manually defined bots from local source"""
    manual_file = Path("sources/manual_bots.json")
    if not manual_file.exists():
        print("ℹ No manual bots file found, creating empty one")
        manual_file.parent.mkdir(exist_ok=True)
        with open(manual_file, 'w') as f:
            json.dump([], f, indent=2)
        return []
    
    with open(manual_file, 'r') as f:
        bots = json.load(f)
    print(f"✓ Loaded {len(bots)} manual bot entries")
    return bots

def load_staging_bots() -> List[Dict]:
    """Load bots from staging area"""
    staging_dir = Path("staging")
    all_bots = []
    
    if not staging_dir.exists():
        print("ℹ No staging directory found")
        return []
    
    for file in staging_dir.glob("*.json"):
        try:
            with open(file, 'r') as f:
                bots = json.load(f)
                all_bots.extend(bots)
                print(f"✓ Loaded {len(bots)} bots from {file.name}")
        except Exception as e:
            print(f"✗ Error loading {file.name}: {e}")
    
    return all_bots

def merge_bot_entries(existing: Dict, new: Dict) -> Dict:
    """Merge two bot entries, preferring manual data, then newer data"""
    merged = existing.copy()
    
    # Merge sources
    existing_sources = set(existing.get("sources", []))
    new_sources = set(new.get("sources", []))
    merged["sources"] = sorted(list(existing_sources | new_sources))
    
    # If new entry has manual source, prefer its data
    if "manual" in new.get("sources", []):
        for key in ["description", "operator", "purpose", "impact_of_blocking", "categories"]:
            if key in new and new[key]:
                merged[key] = new[key]
    else:
        # Otherwise, prefer non-empty values from new entry
        for key in ["description", "operator", "website"]:
            if key in new and new[key] and not existing.get(key):
                merged[key] = new[key]
    
    # Merge raw_data
    existing_raw = existing.get("raw_data", {})
    new_raw = new.get("raw_data", {})
    
    merged_raw = existing_raw.copy()
    for key, value in new_raw.items():
        if key not in merged_raw or not merged_raw[key]:
            merged_raw[key] = value
        elif key == "ip_ranges" and isinstance(value, list):
            # Merge IP ranges
            existing_ips = set(merged_raw.get("ip_ranges", []))
            new_ips = set(value)
            merged_raw["ip_ranges"] = sorted(list(existing_ips | new_ips))
    
    merged["raw_data"] = merged_raw
    
    return merged

def merge_sources():
    """Merge all bot sources and deduplicate"""
    
    # Load all sources
    manual_bots = load_manual_bots()
    staging_bots = load_staging_bots()
    
    all_bots = manual_bots + staging_bots
    
    if not all_bots:
        print("⚠️ No bots found to merge")
        # Create empty output anyway
        staging_dir = Path("staging")
        staging_dir.mkdir(exist_ok=True)
        output_file = staging_dir / "merged_bots.json"
        with open(output_file, 'w') as f:
            json.dump([], f, indent=2)
        return
    
    # Deduplicate by normalized user agent
    bot_map = {}
    
    for bot in all_bots:
        ua = bot.get("user_agent", "")
        if not ua:
            continue
        
        normalized_ua = normalize_user_agent(ua)
        
        if normalized_ua in bot_map:
            # Merge with existing entry
            bot_map[normalized_ua] = merge_bot_entries(bot_map[normalized_ua], bot)
        else:
            # New entry
            bot_map[normalized_ua] = bot
    
    # Convert back to list and sort
    merged_bots = sorted(bot_map.values(), key=lambda x: x.get("user_agent", "").lower())
    
    # Add metadata
    for bot in merged_bots:
        bot["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        # Ensure all required fields exist
        bot.setdefault("description", "")
        bot.setdefault("operator", "")
        bot.setdefault("purpose", "")
        bot.setdefault("impact_of_blocking", "")
        bot.setdefault("categories", {})
        bot.setdefault("sources", [])
        bot.setdefault("raw_data", {})
    
    # Save merged data
    output_dir = Path("staging")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "merged_bots.json"
    with open(output_file, 'w') as f:
        json.dump(merged_bots, f, indent=2)
    
    print(f"\n✓ Merged {len(merged_bots)} unique bots from {len(all_bots)} total entries")
    
    # Print summary
    source_counts = {}
    for bot in merged_bots:
        for source in bot.get("sources", []):
            source_counts[source] = source_counts.get(source, 0) + 1
    
    print("\nSource breakdown:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count} bots")

if __name__ == "__main__":
    merge_sources()
