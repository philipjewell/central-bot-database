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

def load_existing_database() -> List[Dict]:
    """Load existing enriched bots from data/bots.json if it exists"""
    db_file = Path("data/bots.json")
    if not db_file.exists():
        print("ℹ No existing database found, starting fresh")
        return []
    
    try:
        with open(db_file, 'r') as f:
            data = json.load(f)
            bots = data.get("bots", [])
            print(f"✓ Loaded {len(bots)} bots from existing database")
            return bots
    except Exception as e:
        print(f"⚠️ Error loading existing database: {e}")
        return []

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
        # Skip merged/enriched files
        if file.name in ["merged_bots.json", "enriched_bots.json"]:
            continue
            
        try:
            with open(file, 'r') as f:
                bots = json.load(f)
                all_bots.extend(bots)
                print(f"✓ Loaded {len(bots)} bots from {file.name}")
        except Exception as e:
            print(f"✗ Error loading {file.name}: {e}")
    
    return all_bots

def merge_bot_entries(existing: Dict, new: Dict, preserve_enrichment: bool = False) -> Dict:
    """Merge two bot entries, preferring manual data, then newer data"""
    merged = existing.copy()
    
    # Merge sources
    existing_sources = set(existing.get("sources", []))
    new_sources = set(new.get("sources", []))
    merged["sources"] = sorted(list(existing_sources | new_sources))
    
    # If preserve_enrichment is True, keep existing enrichment data
    if preserve_enrichment:
        # Only update technical details, not enrichment
        for key in ["description", "website"]:
            if key in new and new[key] and not existing.get(key):
                merged[key] = new[key]
        
        # Keep existing enrichment if present
        if not existing.get("purpose") and new.get("purpose"):
            merged["purpose"] = new["purpose"]
        if not existing.get("impact_of_blocking") and new.get("impact_of_blocking"):
            merged["impact_of_blocking"] = new["impact_of_blocking"]
        if not existing.get("categories") and new.get("categories"):
            merged["categories"] = new["categories"]
    else:
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
    
    # Merge raw_data (always update technical details)
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
    
    # Load existing database first (this has enriched data we want to preserve)
    existing_db_bots = load_existing_database()
    
    # Load all new sources
    manual_bots = load_manual_bots()
    staging_bots = load_staging_bots()
    
    # Start with existing database
    all_bots = existing_db_bots + manual_bots + staging_bots
    
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
    existing_bot_uas = set()
    
    # First pass: add existing database bots (these are already enriched)
    for bot in existing_db_bots:
        ua = bot.get("user_agent", "")
        if not ua:
            continue
        
        normalized_ua = normalize_user_agent(ua)
        bot_map[normalized_ua] = bot
        existing_bot_uas.add(normalized_ua)
    
    # Second pass: merge new bots
    for bot in manual_bots + staging_bots:
        ua = bot.get("user_agent", "")
        if not ua:
            continue
        
        normalized_ua = normalize_user_agent(ua)
        
        if normalized_ua in bot_map:
            # Bot exists - preserve enrichment, update technical details
            preserve = normalized_ua in existing_bot_uas
            bot_map[normalized_ua] = merge_bot_entries(bot_map[normalized_ua], bot, preserve_enrichment=preserve)
        else:
            # New bot
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
    
    # Count already enriched vs needs enrichment
    enriched = sum(1 for b in merged_bots if b.get("purpose") and b.get("categories"))
    needs_enrichment = len(merged_bots) - enriched
    
    print(f"\nEnrichment status:")
    print(f"  Already enriched: {enriched}")
    print(f"  Needs enrichment: {needs_enrichment}")

if __name__ == "__main__":
    merge_sources()
