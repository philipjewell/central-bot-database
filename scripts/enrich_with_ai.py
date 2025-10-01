"""
Enrich bot data using local LLM (Ollama)
"""
import json
import requests
from pathlib import Path
from typing import Dict

# Site categories for classification
SITE_CATEGORIES = [
    "ecommerce",
    "news",
    "media",
    "blog",
    "saas",
    "corporate",
    "documentation",
    "social",
    "portfolio",
    "government"
]

def get_ollama_response(prompt: str, model: str = "llama3.2") -> str:
    """Get response from local Ollama instance"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120  # Increased timeout
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"✗ Error calling Ollama: {e}")
        return ""

def normalize_category_name(category: str) -> str:
    """Normalize category names to handle typos"""
    # Fix common typos
    typo_map = {
        'sas': 'saas',
        'e-commerce': 'ecommerce',
        'ecommerce': 'ecommerce',
        'tech-docs': 'documentation',
        'docs': 'documentation',
        'doc': 'documentation',
        'govt': 'government',
        'gov': 'government',
    }
    return typo_map.get(category.lower().strip(), category.lower().strip())

def enrich_bot(bot: Dict, bot_num: int, total: int) -> Dict:
    """Enrich a single bot with AI-generated content"""
    
    user_agent = bot.get("user_agent", "")
    operator = bot.get("operator", "")
    existing_desc = bot.get("description", "")
    
    # Check if bot is already fully enriched
    has_purpose = bool(bot.get("purpose"))
    has_impact = bool(bot.get("impact_of_blocking"))
    has_categories = bool(bot.get("categories"))
    
    if has_purpose and has_impact and has_categories:
        # Already fully enriched - skip
        source_type = "manual" if "manual" in bot.get("sources", []) else "external"
        print(f"  [{bot_num}/{total}] ⊙ Skipping {user_agent} (already enriched, {source_type})")
        return bot
    
    # Bot needs enrichment - will update timestamp
    was_enriched = False
    
    # Only enrich what's missing
    print(f"  [{bot_num}/{total}] → Enriching {user_agent}...")
    needs_enrichment = []
    
    if not has_purpose:
        needs_enrichment.append("purpose")
    if not has_impact:
        needs_enrichment.append("impact")
    if not has_categories:
        needs_enrichment.append("categories")
    
    print(f"      Needs: {', '.join(needs_enrichment)}")
    
    # Generate purpose description
    if not has_purpose:
        purpose_prompt = f"""Describe the purpose of this bot in 1-2 concise sentences:

Bot Name: {user_agent}
Operator: {operator}
{f'Description: {existing_desc}' if existing_desc else ''}

Focus on what the bot does and why it exists. Be factual and concise."""

        purpose = get_ollama_response(purpose_prompt)
        if purpose:
            bot["purpose"] = purpose.strip()
            was_enriched = True
            print(f"      ✓ Generated purpose")
    
    # Generate impact of blocking
    if not has_impact:
        impact_prompt = f"""In 1-2 sentences, describe the potential impact of blocking this bot:

Bot Name: {user_agent}
Operator: {operator}
Purpose: {bot.get('purpose', existing_desc)}

Focus on what functionality or visibility would be lost. Be specific and practical."""

        impact = get_ollama_response(impact_prompt)
        if impact:
            bot["impact_of_blocking"] = impact.strip()
            was_enriched = True
            print(f"      ✓ Generated impact")
    
    # Generate category recommendations
    if not has_categories:
        categories_prompt = f"""For the following bot, classify it for different website types.
Respond with ONLY a JSON object mapping each category to one of: "beneficial", "neutral", "harmful", or "not_applicable".

Bot Name: {user_agent}
Operator: {operator}
Purpose: {bot.get('purpose', existing_desc)}

Categories (USE THESE EXACT NAMES):
- ecommerce (NOT "sas" or "e-commerce")
- news
- media
- blog
- saas (spell it "saas" with TWO a's)
- corporate
- documentation
- social
- portfolio
- government

Example format:
{{"ecommerce": "beneficial", "news": "beneficial", "saas": "neutral", "media": "neutral"}}

Your JSON response (use exact category names):"""

        categories_response = get_ollama_response(categories_prompt)
        try:
            # Extract JSON from response
            start = categories_response.find('{')
            end = categories_response.rfind('}') + 1
            if start >= 0 and end > start:
                categories_json = categories_response[start:end]
                categories = json.loads(categories_json)
                
                # Normalize any typos in category names and strip whitespace from ratings
                normalized_categories = {}
                for cat, rating in categories.items():
                    normalized_cat = normalize_category_name(cat)
                    # Strip whitespace from rating values
                    normalized_rating = rating.strip() if isinstance(rating, str) else rating
                    
                    if normalized_cat in SITE_CATEGORIES:
                        # Validate the rating
                        if normalized_rating in ["beneficial", "neutral", "harmful", "not_applicable"]:
                            normalized_categories[normalized_cat] = normalized_rating
                        else:
                            print(f"      ⚠️  Invalid rating '{normalized_rating}' for {normalized_cat}, defaulting to neutral")
                            normalized_categories[normalized_cat] = "neutral"
                    else:
                        print(f"      ⚠️  Ignoring invalid category: {cat}")
                
                # Fill in any missing categories with neutral
                for cat in SITE_CATEGORIES:
                    if cat not in normalized_categories:
                        normalized_categories[cat] = "neutral"
                
                bot["categories"] = normalized_categories
                was_enriched = True
                print(f"      ✓ Generated categories")
        except Exception as e:
            print(f"      ✗ Error parsing categories: {e}")
            # Default to neutral for all categories
            bot["categories"] = {cat: "neutral" for cat in SITE_CATEGORIES}
            was_enriched = True
    
    # Update timestamp only if we enriched the bot
    if was_enriched:
        bot["last_updated"] = datetime.utcnow().isoformat() + "Z"
    
    return bot

def enrich_with_ai():
    """Enrich all bots with AI-generated content"""
    
    # Check if Ollama is available
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        print("✓ Ollama is running")
    except Exception as e:
        print(f"✗ Ollama is not available: {e}")
        print("  Please install Ollama (https://ollama.ai) and run: ollama pull llama3.2")
        print("  Skipping AI enrichment...")
        # Copy merged to enriched without changes
        merged_file = Path("staging/merged_bots.json")
        enriched_file = Path("staging/enriched_bots.json")
        if merged_file.exists():
            import shutil
            shutil.copy(merged_file, enriched_file)
            print("  Copied merged bots to enriched (no AI enrichment)")
        return
    
    # Load merged bots
    merged_file = Path("staging/merged_bots.json")
    if not merged_file.exists():
        print("✗ No merged bots file found")
        return
    
    with open(merged_file, 'r') as f:
        bots = json.load(f)
    
    total = len(bots)
    print(f"\n🤖 Enriching {total} bots with AI-generated content...")
    print(f"   This may take a while (approximately {total * 2} minutes)\n")
    
    # Enrich each bot
    for i, bot in enumerate(bots, 1):
        bots[i-1] = enrich_bot(bot, i, total)
        
        # Progress update every 10 bots
        if i % 10 == 0:
            print(f"\n   Progress: {i}/{total} bots enriched ({i*100//total}%)\n")
    
    # Save enriched data
    output_file = Path("staging/enriched_bots.json")
    with open(output_file, 'w') as f:
        json.dump(bots, f, indent=2)
    
    print(f"\n✅ Enrichment complete! Saved to {output_file}")
    print(f"   Total bots enriched: {total}")

if __name__ == "__main__":
    enrich_with_ai()
