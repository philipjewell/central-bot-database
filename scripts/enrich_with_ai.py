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
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"✗ Error calling Ollama: {e}")
        return ""

def enrich_bot(bot: Dict) -> Dict:
    """Enrich a single bot with AI-generated content"""
    
    # Skip if already has manual data
    if "manual" in bot.get("sources", []):
        if bot.get("purpose") and bot.get("categories"):
            print(f"  ⊙ Skipping {bot['user_agent']} (manual entry)")
            return bot
    
    user_agent = bot.get("user_agent", "")
    operator = bot.get("operator", "")
    existing_desc = bot.get("description", "")
    
    print(f"  → Enriching {user_agent}...")
    
    # Generate purpose description
    if not bot.get("purpose"):
        purpose_prompt = f"""Describe the purpose of this bot in 1-2 concise sentences:

Bot Name: {user_agent}
Operator: {operator}
{f'Description: {existing_desc}' if existing_desc else ''}

Focus on what the bot does and why it exists. Be factual and concise."""

        purpose = get_ollama_response(purpose_prompt)
        if purpose:
            bot["purpose"] = purpose.strip()
    
    # Generate impact of blocking
    if not bot.get("impact_of_blocking"):
        impact_prompt = f"""In 1-2 sentences, describe the potential impact of blocking this bot:

Bot Name: {user_agent}
Operator: {operator}
Purpose: {bot.get('purpose', existing_desc)}

Focus on what functionality or visibility would be lost. Be specific and practical."""

        impact = get_ollama_response(impact_prompt)
        if impact:
            bot["impact_of_blocking"] = impact.strip()
    
    # Generate category recommendations
    if not bot.get("categories"):
        categories_prompt = f"""For the following bot, classify it for different website types.
Respond with ONLY a JSON object mapping each category to one of: "beneficial", "neutral", "harmful", or "not_applicable".

Bot Name: {user_agent}
Operator: {operator}
Purpose: {bot.get('purpose', existing_desc)}

Categories: {', '.join(SITE_CATEGORIES)}

Example format:
{{"ecommerce": "beneficial", "news": "beneficial", "media": "neutral"}}

Your JSON response:"""

        categories_response = get_ollama_response(categories_prompt)
        try:
            # Extract JSON from response
            start = categories_response.find('{')
            end = categories_response.rfind('}') + 1
            if start >= 0 and end > start:
                categories_json = categories_response[start:end]
                categories = json.loads(categories_json)
                bot["categories"] = categories
        except Exception as e:
            print(f"    ✗ Error parsing categories: {e}")
            # Default to neutral for all categories
            bot["categories"] = {cat: "neutral" for cat in SITE_CATEGORIES}
    
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
    
    print(f"\nEnriching {len(bots)} bots with AI-generated content...\n")
    
    # Enrich each bot
    for i, bot in enumerate(bots, 1):
        print(f"[{i}/{len(bots)}]", end=" ")
        bots[i-1] = enrich_bot(bot)
    
    # Save enriched data
    output_file = Path("staging/enriched_bots.json")
    with open(output_file, 'w') as f:
        json.dump(bots, f, indent=2)
    
    print(f"\n✓ Enrichment complete, saved to {output_file}")

if __name__ == "__main__":
    enrich_with_ai()
