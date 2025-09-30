"""
Validate bot database against schema and check for issues
"""
import json
from pathlib import Path
from typing import List, Dict

VALID_RATINGS = ["beneficial", "neutral", "harmful", "not_applicable"]
VALID_CATEGORIES = [
    "ecommerce", "news", "media", "blog", "saas",
    "corporate", "documentation", "social", "portfolio", "government"
]

def validate_bot(bot: Dict, bot_index: int) -> List[str]:
    """Validate a single bot entry"""
    issues = []
    
    # Check required fields
    if not bot.get("user_agent"):
        issues.append(f"Bot {bot_index}: Missing user_agent")
    
    if not bot.get("operator"):
        issues.append(f"Bot {bot_index}: Missing operator")
    
    if not bot.get("sources"):
        issues.append(f"Bot {bot_index}: Missing sources")
    
    # Check categories
    categories = bot.get("categories", {})
    for category, rating in categories.items():
        if category not in VALID_CATEGORIES:
            issues.append(f"Bot {bot_index} ({bot.get('user_agent')}): Invalid category '{category}'")
        
        if rating not in VALID_RATINGS:
            issues.append(f"Bot {bot_index} ({bot.get('user_agent')}): Invalid rating '{rating}' for category '{category}'")
    
    # Only warn about missing enrichment for manual entries
    # External entries can be enriched later
    if "manual" in bot.get("sources", []):
        if not bot.get("purpose"):
            issues.append(f"Bot {bot_index} ({bot.get('user_agent')}): Manual entry missing purpose description")
        
        if not bot.get("impact_of_blocking"):
            issues.append(f"Bot {bot_index} ({bot.get('user_agent')}): Manual entry missing impact_of_blocking")
    
    return issues

def validate_data():
    """Validate the entire bot database"""
    
    print("🔍 Validating bot database...\n")
    
    # Check if output file exists
    output_file = Path("data/bots.json")
    if not output_file.exists():
        print("❌ data/bots.json not found!")
        return False
    
    # Load data
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    # Check structure
    if "meta" not in data:
        print("❌ Missing 'meta' section")
        return False
    
    if "bots" not in data:
        print("❌ Missing 'bots' section")
        return False
    
    bots = data["bots"]
    print(f"✓ Found {len(bots)} bots\n")
    
    # Validate each bot
    all_issues = []
    for i, bot in enumerate(bots):
        issues = validate_bot(bot, i)
        all_issues.extend(issues)
    
    # Check for duplicates
    user_agents = [bot.get("user_agent", "").lower() for bot in bots]
    duplicates = [ua for ua in set(user_agents) if user_agents.count(ua) > 1]
    
    if duplicates:
        print("⚠️  Duplicate user agents found:")
        for dup in duplicates:
            print(f"   - {dup}")
        print()
    
    # Count enrichment status
    enriched = sum(1 for b in bots if b.get("purpose") and b.get("categories"))
    unenriched = len(bots) - enriched
    
    print(f"📊 Enrichment Status:")
    print(f"   Enriched: {enriched}/{len(bots)} ({enriched*100//len(bots) if len(bots) > 0 else 0}%)")
    print(f"   Awaiting enrichment: {unenriched}")
    print()
    
    # Print validation results
    if all_issues:
        print(f"⚠️  Found {len(all_issues)} validation issues:\n")
        for issue in all_issues[:20]:  # Show first 20
            print(f"   - {issue}")
        
        if len(all_issues) > 20:
            print(f"\n   ... and {len(all_issues) - 20} more issues")
        
        print()
        
        # Only fail if critical issues (not enrichment warnings)
        critical_issues = [i for i in all_issues if not ("Missing purpose" in i or "Missing impact" in i or "Missing category" in i)]
        
        if critical_issues:
            print(f"❌ {len(critical_issues)} critical validation errors found!")
            return False
        else:
            print("⚠️  Non-critical issues found (missing enrichment), but validation passes")
            print("   These bots will be enriched in the next run when Ollama is available")
    else:
        print("✅ All validations passed!")
    
    # Print statistics
    print("\n📊 Statistics:")
    print(f"   Total bots: {len(bots)}")
    
    # Count by source
    sources = {}
    for bot in bots:
        for source in bot.get("sources", []):
            sources[source] = sources.get(source, 0) + 1
    
    print("\n   By source:")
    for source, count in sorted(sources.items()):
        print(f"      {source}: {count}")
    
    # Count by operator (top 10)
    operators = {}
    for bot in bots:
        op = bot.get("operator", "Unknown")
        if op:  # Only count non-empty operators
            operators[op] = operators.get(op, 0) + 1
    
    if operators:
        print("\n   Top 10 Operators:")
        for op, count in sorted(operators.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {op}: {count}")
    
    # Technical details
    with_ips = sum(1 for b in bots if b.get('raw_data', {}).get('ip_ranges'))
    with_asn = sum(1 for b in bots if b.get('raw_data', {}).get('asn'))
    
    print(f"\n   Technical Details:")
    print(f"      With IP ranges: {with_ips}")
    print(f"      With ASN: {with_asn}")
    
    return True

if __name__ == "__main__":
    import sys
    success = validate_data()
    sys.exit(0 if success else 1)
