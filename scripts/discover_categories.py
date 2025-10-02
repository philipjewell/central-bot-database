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
        return {}

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
    Discover all categories and learn mappings from bots appearing in multiple sources
    
    Returns:
        - all_categories: Dict mapping category -> set of sources that use it
        - learned_mappings: Dict mapping source category -> unified category
    """
    
    all_bots = load_all_bot_data()
    
    if not all_bots:
        print("⚠️  No bot data found to analyze")
        return {}, {}
    
    print(f"📊 Analyzing {len(all_bots)} bots from all sources...\n")
    
    # Track all categories and which sources use them
    all_categories = defaultdict(set)
    
    # Track bots that appear in multiple sources with their categories
    bot_categories = defaultdict(lambda: defaultdict(set))  # normalized_ua -> source -> categories
    
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
            bot_categories[normalized_ua][source].add(category)
    
    # Learn mappings from bots appearing in multiple sources
    learned_mappings = {}
    
    print("🔍 Discovering category mappings from multi-source bots:\n")
    
    for ua, source_data in bot_categories.items():
        if len(source_data) < 2:
            # Bot only appears in one source
            continue
        
        # Bot appears in multiple sources - look for patterns
        categories = {}
        for source, cats in source_data.items():
            if cats:
                categories[source] = list(cats)[0]  # Take first category
        
        if len(categories) < 2:
            continue
        
        # If cloudflare-radar has a category, it becomes the canonical one
        if "cloudflare-radar" in categories:
            canonical = categories["cloudflare-radar"]
            
            for source, cat in categories.items():
                if source != "cloudflare-radar" and cat != canonical and cat != "Other":
                    if cat not in learned_mappings:
                        learned_mappings[cat] = canonical
                        print(f"  ✓ {cat} → {canonical} (from {source} to cloudflare-radar)")
        
        # If ai-robots-txt and manual both exist, prefer manual
        elif "manual" in categories and "ai-robots-txt" in categories:
            canonical = categories["manual"]
            cat = categories["ai-robots-txt"]
            
            if cat != canonical and cat != "Other":
                if cat not in learned_mappings:
                    learned_mappings[cat] = canonical
                    print(f"  ✓ {cat} → {canonical} (from ai-robots-txt to manual)")
    
    return dict(all_categories), learned_mappings

def update_mappings():
    """Update category mappings file with newly discovered categories"""
    
    existing_mappings = load_existing_mappings()
    all_categories, learned_mappings = discover_categories()
    
    if not all_categories:
        print("⚠️  No categories discovered")
        return False
    
    # Find new categories (not in existing mappings as keys or values)
    existing_keys = set(existing_mappings.keys())
    existing_values = set(existing_mappings.values())
    all_seen_categories = existing_keys | existing_values
    
    new_categories = []
    for category in all_categories.keys():
        if category not in all_seen_categories and category != "Other":
            new_categories.append(category)
    
    # Update mappings with learned mappings
    updated = False
    
    print("\n📝 Updating category mappings...\n")
    
    # Add learned mappings
    for source_cat, unified_cat in learned_mappings.items():
        if source_cat not in existing_mappings or existing_mappings[source_cat] != unified_cat:
            existing_mappings[source_cat] = unified_cat
            print(f"  + Added mapping: {source_cat} → {unified_cat}")
            updated = True
    
    # Add new categories that don't have mappings (map to themselves)
    for category in new_categories:
        if category not in existing_mappings:
            existing_mappings[category] = category
            print(f"  + New category discovered: {category} (keeping as-is)")
            updated = True
    
    # Ensure "Other" is always mapped
    if "" not in existing_mappings:
        existing_mappings[""] = "Other"
        updated = True
    if "Other" not in existing_mappings:
        existing_mappings["Other"] = "Other"
        updated = True
    if "Unknown" not in existing_mappings:
        existing_mappings["Unknown"] = "Other"
        updated = True
    if "Uncategorized" not in existing_mappings:
        existing_mappings["Uncategorized"] = "Other"
        updated = True
    
    if not updated:
        print("  ℹ️  No new categories or mappings to add")
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
    
    # Print summary of all unified categories
    unified_categories = set(sorted_mappings.values())
    print(f"\n📋 Unified categories ({len(unified_categories)}):")
    for cat in sorted(unified_categories):
        count = sum(1 for v in sorted_mappings.values() if v == cat)
        source_cats = [k for k, v in sorted_mappings.items() if v == cat]
        print(f"  • {cat} ({count} source categories)")
        if count <= 5:  # Show mappings if not too many
            for sc in source_cats[:5]:
                if sc != cat:
                    print(f"      - {sc}")
    
    return True

if __name__ == "__main__":
    updated = update_mappings()
    if not updated:
        print("\n✓ Category mappings are up to date")
    else:
        print("\n✓ Category mappings have been updated")
