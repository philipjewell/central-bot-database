"""
Fix rating values with leading/trailing whitespace
"""
import json
from pathlib import Path

def fix_ratings():
    """Strip whitespace from all rating values in the database"""
    
    # Load the enriched bots
    enriched_file = Path("staging/enriched_bots.json")
    if not enriched_file.exists():
        print("✗ No enriched bots file found")
        return
    
    with open(enriched_file, 'r') as f:
        bots = json.load(f)
    
    fixed_count = 0
    
    for bot in bots:
        categories = bot.get("categories", {})
        if categories:
            fixed = False
            for cat, rating in categories.items():
                if isinstance(rating, str):
                    stripped = rating.strip()
                    if stripped != rating:
                        categories[cat] = stripped
                        fixed = True
            
            if fixed:
                fixed_count += 1
                print(f"✓ Fixed ratings for {bot.get('user_agent', 'Unknown')}")
    
    # Save fixed data
    with open(enriched_file, 'w') as f:
        json.dump(bots, f, indent=2)
    
    print(f"\n✅ Fixed {fixed_count} bots with whitespace issues")

if __name__ == "__main__":
    fix_ratings()
