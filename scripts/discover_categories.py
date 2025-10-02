"""
Discover and map bot categories from all sources
"""
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Tuple

def load_existing_mappings() -> Dict[str, str]:
    """Load existing category mappings"""
    mapping_file = Path("schemas/category_mappings.json")
    
    if mapping_file.exists():
        with open(mapping_file, 'r') as f:
            return json.load(f)
    else:
        return {
            "": "Other",
            "Other": "Other",
            "Unknown": "Other",
            "Uncategorized": "Other"
        }

def load_all_bot_data() -> List[Dict]:
    """Load bot data from all staging sources"""
    all_bots = []
    staging_dir = Path("staging")
    
    if not staging_dir.exists():
        return all_bots
    
    for file in staging_dir.glob("*.json"):
        # Skip merged/enriched files
        if file.name in ["merged_bots.json", "enriched_bots.json"]:
            continue
        
        try:
            with open(file, 'r') as f:
                bots = json.load(f)
                all_bots.extend(bots)
        except Exception as e:
            print(f"⚠️  Error loading {file.name}: {e}")
    
    # Also load manual bots
    sources_dir = Path("sources")
    if sources_dir.exists():
        for file in sources_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        all_bots.extend(content)
                    elif isinstance(content, dict):
                        all_bots.append(content)
            except Exception as e:
                print(f"⚠️  Error loading {file.name}: {e}")
    
    return all_bots

def normalize_user_agent(ua: str) -> str:
    """Normalize user agent for comparison"""
    return ua.lower().strip().replace('-', '').replace('_', '')

def discover_categories() -> Tuple[Dict[str, Set[str]], Dict[str, str]]:
    """
    Discover all categories and learn mappings
    
    Strategy:
    - Cloudflare categories are AUTHORITATIVE (no mapping needed)
    - Manual categories are kept as-is (no mapping needed)
    - Other source categories get mapped TO Cloudflare categories when same bot exists
    
    Returns:
        - all_categories: Dict mapping category -> set of sources that use it
        - learned_mappings: Dict mapping non-Cloudflare category -> Cloudflare category
    """
    
    all_bots = load_all_bot_data()
    
    if not all_bots:
        print("⚠️  No bot data found to analyze")
        return {}, {}
    
    print(f"📊 Analyzing {len(all_bots)} bots from all sources...\n")
    
    # Track all categories and which sources use them
    all_categories = defaultdict(set)
    
    # Track bots that appear in multiple sources with their categories
    # Structure: normalized_ua -> {source: category}
    bot_source_categories = defaultdict(dict)
    
    for bot in all_bots:
        ua = bot.get("user_agent", "")
        if not ua:
            continue
        
        normalized_ua = normalize_user_agent(ua)
        category = bot.get("operator", "").strip()
        sources = bot.get("sources", [])
        
        if not category:
            category = "Other"
        
        # Track all categories
        for source in sources:
            all_categories[category].add(source)
            
            # For learning mappings, we only care about the primary source
            # (a bot should primarily come from one source at fetch time)
            if source in bot_source_categories[normalized_ua]:
                # Already have this source, skip
                continue
            
            bot_source_categories[normalized_ua][source] = category
    
    # Learn mappings: Other sources -> Cloudflare categories
    learned_mappings = {}
    
    print("🔍 Discovering category mappings:\n")
    print("   Strategy: Map non-Cloudflare categories to Cloudflare categories\n")
    
    cloudflare_bots_analyzed = 0
    mappings_learned = 0
    
    for ua, source_cats in bot_source_categories.items():
        # Check if this bot has a Cloudflare category
        if "cloudflare-radar" not in source_cats:
            continue
        
        cloudflare_bots_analyzed += 1
        cloudflare_category = source_cats["cloudflare-radar"]
        
        # For each other source this bot appears in, map to Cloudflare category
        for source, category in source_cats.items():
            if source == "cloudflare-radar":
                continue
            
            # Don't map manual categories
            if source == "manual":
                continue
            
            # Don't map if category is already correct
            if category == cloudflare_category:
                continue
            
            # Don't map "Other"
            if category == "Other":
                continue
            
            # Learn this mapping
            if category not in learned_mappings:
                learned_mappings[category] = cloudflare_category
                mappings_learned += 1
                print(f"  ✓ {category} → {cloudflare_category}")
                print(f"      (learned from bot that exists in both {source} and Cloudflare)")
    
    if cloudflare_bots_analyzed == 0:
        print("  ℹ️  No bots found in Cloudflare Radar to learn from")
    else:
        print(f"\n  📊 Analyzed {cloudflare_bots_analyzed} bots that exist in Cloudflare")
        print(f"  📝 Learned {mappings_learned} new category mappings")
    
    return dict(all_categories), learned_mappings

def update_mappings():
    """Update category mappings file with newly discovered categories"""
    
    existing_mappings = load_existing_mappings()
    all_categories, learned_mappings = discover_categories()
    
    if not all_categories:
        print("⚠️  No categories discovered")
        return False
    
    updated = False
    
    print("\n📝 Updating category mappings...\n")
    
    # Add learned mappings (non-Cloudflare -> Cloudflare)
    for source_cat, cloudflare_cat in learned_mappings.items():
        if source_cat not in existing_mappings or existing_mappings[source_cat] != cloudflare_cat:
            existing_mappings[source_cat] = cloudflare_cat
            print(f"  + Added mapping: {source_cat} → {cloudflare_cat}")
            updated = True
    
    # Don't auto-add new categories that don't have mappings
    # Those will be kept as-is when they're used
    
    # Ensure standard "Other" mappings exist
    standard_others = {
        "": "Other",
        "Other": "Other",
        "Unknown": "Other",
        "Uncategorized": "Other"
    }
    
    for key, value in standard_others.items():
        if key not in existing_mappings:
            existing_mappings[key] = value
            updated = True
    
    if not updated:
        print("  ℹ️  No new mappings to add")
        return False
    
    # Save updated mappings
    mapping_file = Path("schemas/category_mappings.json")
    mapping_file.parent.mkdir(exist_ok=True)
    
    # Sort mappings alphabetically for easier review
    sorted_mappings = dict(sorted(existing_mappings.items()))
    
    with open(mapping_file, 'w') as f:
        json.dump(sorted_mappings, f, indent=2)
    
    print(f"\n✅ Updated category mappings saved to {mapping_file}")
    print(f"   Total mappings: {len(sorted_mappings)}")
    
    # Print summary
    print(f"\n📋 Category Mapping Summary:")
    print(f"   These mappings apply ONLY to non-Cloudflare, non-Manual sources")
    print(f"   Cloudflare and Manual categories are used as-is\n")
    
    # Group by target category
    by_target = defaultdict(list)
    for source, target in sorted_mappings.items():
        if source != target:  # Don't show identity mappings
            by_target[target].append(source)
    
    for target, sources in sorted(by_target.items()):
        print(f"  • {target}")
        for source in sorted(sources):
            print(f"      ← {source}")
    
    return True

if __name__ == "__main__":
    updated = update_mappings()
    if not updated:
        print("\n✓ Category mappings are up to date")
    else:
        print("\n✓ Category mappings have been updated")
