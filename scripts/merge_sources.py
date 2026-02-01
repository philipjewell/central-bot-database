"""
Merge bot data from multiple sources and deduplicate
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from category_mapper import get_category_mapper

def normalize_user_agent(ua: str) -> str:
    """Normalize user agent strings for comparison"""
    return ua.lower().strip().replace('-', '').replace('_', '')

def bot_has_changed(original: Dict, updated: Dict) -> bool:
    """
    Compare two bot dictionaries to see if any meaningful fields changed.

    Compares: user_agent, operator, description, sources, raw_data,
              purpose, impact_of_blocking, categories

    Returns True if any field has changed, False otherwise.
    """
    # Fields to compare (excluding last_updated)
    fields_to_compare = [
        "user_agent",
        "operator",
        "description",
        "purpose",
        "impact_of_blocking"
    ]

    # Compare simple fields
    for field in fields_to_compare:
        if original.get(field) != updated.get(field):
            return True

    # Compare sources (as sets to ignore order)
    original_sources = set(original.get("sources", []))
    updated_sources = set(updated.get("sources", []))
    if original_sources != updated_sources:
        return True

    # Compare categories (nested dict)
    original_categories = original.get("categories", {})
    updated_categories = updated.get("categories", {})
    if original_categories != updated_categories:
        return True

    # Compare raw_data (nested dict)
    original_raw = original.get("raw_data", {})
    updated_raw = updated.get("raw_data", {})

    # Compare all keys in raw_data
    all_raw_keys = set(original_raw.keys()) | set(updated_raw.keys())
    for key in all_raw_keys:
        original_val = original_raw.get(key)
        updated_val = updated_raw.get(key)

        # For lists (like ip_ranges), compare as sets to ignore order
        if isinstance(original_val, list) and isinstance(updated_val, list):
            if set(original_val) != set(updated_val):
                return True
        elif original_val != updated_val:
            return True

    # No changes detected
    return False

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
    """Load manually defined bots from all JSON files in sources/ directory"""
    sources_dir = Path("sources")
    if not sources_dir.exists():
        print("ℹ No sources directory found, creating it")
        sources_dir.mkdir(exist_ok=True)
        return []
    
    all_manual_bots = []
    json_files = list(sources_dir.glob("*.json"))
    
    if not json_files:
        print("ℹ No manual bot files found in sources/")
        return []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                content = json.load(f)
                
                # Handle both single bot object and array of bots
                if isinstance(content, list):
                    bots = content
                elif isinstance(content, dict):
                    # Single bot object
                    bots = [content]
                else:
                    print(f"⚠️  Skipping {json_file.name}: Invalid format")
                    continue
                
                # Ensure each bot has the manual source
                for bot in bots:
                    if "sources" not in bot:
                        bot["sources"] = ["manual"]
                    elif "manual" not in bot["sources"]:
                        bot["sources"].append("manual")
                    
                    # Default operator to "Other" if not provided
                    if not bot.get("operator"):
                        bot["operator"] = "Other"
                
                all_manual_bots.extend(bots)
                print(f"✓ Loaded {len(bots)} bot(s) from {json_file.name}")
                
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing {json_file.name}: {e}")
        except Exception as e:
            print(f"✗ Error loading {json_file.name}: {e}")
    
    print(f"✓ Total manual bots loaded: {len(all_manual_bots)}")
    return all_manual_bots

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
                
                # Default operator to "Other" if not provided
                for bot in bots:
                    if not bot.get("operator"):
                        bot["operator"] = "Other"
                
                all_bots.extend(bots)
                print(f"✓ Loaded {len(bots)} bots from {file.name}")
        except Exception as e:
            print(f"✗ Error loading {file.name}: {e}")
    
    return all_bots

def merge_bot_entries(existing: Dict, new: Dict, preserve_enrichment: bool = False) -> Dict:
    """Merge two bot entries, preferring manual data, then newer data"""
    # Take snapshot of original state (deep copy of fields we care about)
    original_state = {
        "user_agent": existing.get("user_agent"),
        "operator": existing.get("operator"),
        "description": existing.get("description"),
        "sources": existing.get("sources", [])[:],  # copy list
        "raw_data": existing.get("raw_data", {}).copy(),
        "purpose": existing.get("purpose"),
        "impact_of_blocking": existing.get("impact_of_blocking"),
        "categories": existing.get("categories", {}).copy()
    }

    merged = existing.copy()
    mapper = get_category_mapper()

    # Merge sources
    existing_sources = set(existing.get("sources", []))
    new_sources = set(new.get("sources", []))
    merged_sources_set = existing_sources | new_sources

    # Only update if sources actually changed (compare sets to ignore order)
    if merged_sources_set != existing_sources:
        merged["sources"] = sorted(list(merged_sources_set))

    # Merge operator/category with priority: Cloudflare > Manual > Mapped
    existing_category = existing.get("operator", "")
    new_category = new.get("operator", "")

    if existing_category != new_category:
        unified_category = mapper.merge_categories(
            existing_category, list(existing_sources),
            new_category, list(new_sources)
        )
        if unified_category != existing_category:
            merged["operator"] = unified_category

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
                if key in new and new[key] and new[key] != existing.get(key):
                    merged[key] = new[key]
        else:
            # Otherwise, prefer non-empty values from new entry
            for key in ["description", "website"]:
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
            merged_ips = sorted(list(existing_ips | new_ips))
            if merged_ips != merged_raw.get("ip_ranges", []):
                merged_raw["ip_ranges"] = merged_ips

    merged["raw_data"] = merged_raw

    # Compare final state to original state
    # Only update timestamp if something actually changed
    if bot_has_changed(original_state, merged):
        merged["last_updated"] = datetime.utcnow().isoformat() + "Z"

    return merged

def merge_sources():
    """Merge all bot sources and deduplicate"""
    
    mapper = get_category_mapper()
    
    # Load existing database first (this has enriched data we want to preserve)
    existing_db_bots = load_existing_database()
    
    # Load all new sources
    manual_bots = load_manual_bots()
    staging_bots = load_staging_bots()
    
    # Start with existing database
    all_bots = existing_db_bots + manual_bots + staging_bots
    sorted_bots = sorted(all_bots, key=lambda x: x["user_agent"])
    
    if not sorted_bots:
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
        # Get category using priority system
        bot["operator"] = mapper.get_category_for_bot(bot)
        bot_map[normalized_ua] = bot
        existing_bot_uas.add(normalized_ua)
    
    # Second pass: merge new bots
    for bot in manual_bots + staging_bots:
        ua = bot.get("user_agent", "")
        if not ua:
            continue
        
        normalized_ua = normalize_user_agent(ua)
        
        # Get category using priority system
        bot["operator"] = mapper.get_category_for_bot(bot)
        
        if normalized_ua in bot_map:
            # Bot exists - preserve enrichment, update technical details
            preserve = normalized_ua in existing_bot_uas
            bot_map[normalized_ua] = merge_bot_entries(bot_map[normalized_ua], bot, preserve_enrichment=preserve)
        else:
            # New bot - set timestamp
            bot["last_updated"] = datetime.utcnow().isoformat() + "Z"
            bot_map[normalized_ua] = bot
    
    # Convert back to list and sort
    merged_bots = sorted(bot_map.values(), key=lambda x: x.get("user_agent", "").lower())
    
    # Ensure all required fields exist (but don't update timestamp)
    for bot in merged_bots:
        bot.setdefault("description", "")
        bot.setdefault("operator", "Other")
        bot.setdefault("purpose", "")
        bot.setdefault("impact_of_blocking", "")
        bot.setdefault("categories", {})
        bot.setdefault("sources", [])
        bot.setdefault("raw_data", {})
        # Note: last_updated is only set when bot is created (line 257) or modified (line 194)
        # Do NOT set a default timestamp here as it causes all bots to appear changed in PRs
    
    # Save category mappings for future runs
    mapper.save_mappings()
    
    # Save merged data
    output_dir = Path("staging")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "merged_bots.json"
    with open(output_file, 'w') as f:
        json.dump(merged_bots, f, indent=2)
    
    print(f"\n✓ Merged {len(merged_bots)} unique bots from {len(sorted_bots)} total entries")
    
    # Print summary
    source_counts = {}
    for bot in merged_bots:
        for source in bot.get("sources", []):
            source_counts[source] = source_counts.get(source, 0) + 1
    
    print("\nSource breakdown:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count} bots")
    
    # Print category breakdown
    category_counts = {}
    for bot in merged_bots:
        category = bot.get("operator", "Other")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print("\nCategory breakdown:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count} bots")
    
    # Count already enriched vs needs enrichment
    enriched = sum(1 for b in merged_bots if b.get("purpose") and b.get("categories"))
    needs_enrichment = len(merged_bots) - enriched
    
    print(f"\nEnrichment status:")
    print(f"  Already enriched: {enriched}")
    print(f"  Needs enrichment: {needs_enrichment}")

if __name__ == "__main__":
    merge_sources()
