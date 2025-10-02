"""
Bot category mapper - normalizes categories across different sources
"""
import json
from pathlib import Path
from typing import Dict, Set

class CategoryMapper:
    """Maps source-specific categories to unified categories"""
    
    def __init__(self):
        # Load or initialize category mappings
        self.mappings = self.load_mappings()
        self.reverse_mappings = self._build_reverse_mappings()
    
    def load_mappings(self) -> Dict[str, str]:
        """Load category mappings from file"""
        mapping_file = Path("schemas/category_mappings.json")
        
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                return json.load(f)
        else:
            # Default mappings based on known patterns
            return {
                # AI-related bots
                "AI Data Scraper": "AI Crawler",
                "AI Assistant": "AI Crawler",
                "AI Bot": "AI Crawler",
                "AI Search": "AI Crawler",
                "LLM Crawler": "AI Crawler",
                "Machine Learning": "AI Crawler",
                
                # Search engines
                "Search Engine": "Search Engine Crawler",
                "Search Bot": "Search Engine Crawler",
                "Search Crawler": "Search Engine Crawler",
                "Web Crawler": "Search Engine Crawler",
                
                # SEO & Analytics
                "SEO": "SEO Crawler",
                "SEO Bot": "SEO Crawler",
                "SEO Crawler": "SEO Crawler",
                "Analytics": "Analytics",
                "Site Analyzer": "Analytics",
                
                # Monitoring
                "Uptime Monitor": "Monitoring",
                "Site Monitor": "Monitoring",
                "Monitoring Bot": "Monitoring",
                "Health Check": "Monitoring",
                
                # Social Media
                "Social Media": "Social Media Bot",
                "Social Bot": "Social Media Bot",
                "Social Crawler": "Social Media Bot",
                
                # Archive & Research
                "Archive": "Archiver",
                "Archiver Bot": "Archiver",
                "Web Archive": "Archiver",
                "Research": "Research",
                "Academic": "Research",
                
                # Feed readers
                "Feed Reader": "Feed Fetcher",
                "RSS": "Feed Fetcher",
                "Feed Bot": "Feed Fetcher",
                
                # Screenshot & Testing
                "Screenshot": "Screenshot Bot",
                "Headless Browser": "Screenshot Bot",
                "Testing": "Testing Bot",
                "QA Bot": "Testing Bot",
                
                # Security
                "Security": "Security Scanner",
                "Vulnerability Scanner": "Security Scanner",
                "Security Bot": "Security Scanner",
                
                # Other catch-alls
                "Unknown": "Other",
                "Uncategorized": "Other",
                "": "Other"
            }
    
    def _build_reverse_mappings(self) -> Dict[str, Set[str]]:
        """Build reverse lookup: unified category -> set of source categories"""
        reverse = {}
        for source_cat, unified_cat in self.mappings.items():
            if unified_cat not in reverse:
                reverse[unified_cat] = set()
            reverse[unified_cat].add(source_cat)
        return reverse
    
    def normalize_category(self, category: str) -> str:
        """Normalize a category to its unified form"""
        if not category or category.strip() == "":
            return "Other"
        
        # Check if it's already a unified category
        if category in self.reverse_mappings:
            return category
        
        # Check if we have a mapping for it
        if category in self.mappings:
            return self.mappings[category]
        
        # No mapping found - keep original and add to mappings for future
        print(f"  ℹ️  New category discovered: '{category}' - keeping as-is")
        return category
    
    def learn_from_bots(self, bots: list) -> None:
        """Learn category mappings from bots with multiple sources"""
        # Find bots that appear in multiple sources
        bot_categories = {}  # normalized_ua -> {source -> category}
        
        for bot in bots:
            ua = bot.get("user_agent", "").lower().strip()
            if not ua:
                continue
            
            sources = bot.get("sources", [])
            category = bot.get("operator", "")  # operator field often contains category
            
            if ua not in bot_categories:
                bot_categories[ua] = {}
            
            for source in sources:
                if category:
                    bot_categories[ua][source] = category
        
        # Look for patterns: same bot, different sources, different categories
        for ua, source_cats in bot_categories.items():
            if len(source_cats) > 1:
                # Bot has multiple source categories
                categories = list(source_cats.values())
                
                # If cloudflare has a category, it becomes the unified one
                if "cloudflare-radar" in source_cats:
                    unified = source_cats["cloudflare-radar"]
                    
                    # Map other sources to this unified category
                    for source, cat in source_cats.items():
                        if source != "cloudflare-radar" and cat != unified:
                            if cat not in self.mappings or self.mappings[cat] == "Other":
                                self.mappings[cat] = unified
                                print(f"  📝 Learned mapping: '{cat}' -> '{unified}'")
    
    def save_mappings(self) -> None:
        """Save current mappings to file"""
        mapping_file = Path("schemas/category_mappings.json")
        mapping_file.parent.mkdir(exist_ok=True)
        
        with open(mapping_file, 'w') as f:
            json.dump(self.mappings, f, indent=2, sort_keys=True)
        
        print(f"✓ Saved category mappings to {mapping_file}")
    
    def get_unified_category(self, bot: Dict) -> str:
        """Get the unified category for a bot, considering all sources"""
        sources = bot.get("sources", [])
        operator = bot.get("operator", "").strip()
        
        # If no operator/category, return Other
        if not operator:
            return "Other"
        
        # Normalize the category
        return self.normalize_category(operator)
    
    def merge_categories(self, existing_category: str, new_category: str, new_sources: list) -> str:
        """Merge categories when combining bot entries"""
        existing_normalized = self.normalize_category(existing_category) if existing_category else "Other"
        new_normalized = self.normalize_category(new_category) if new_category else "Other"
        
        # If they're the same after normalization, use that
        if existing_normalized == new_normalized:
            return existing_normalized
        
        # If one is "Other", prefer the other one
        if existing_normalized == "Other" and new_normalized != "Other":
            return new_normalized
        if new_normalized == "Other" and existing_normalized != "Other":
            return existing_normalized
        
        # If manual source is present, prefer that
        if "manual" in new_sources and new_category:
            return new_normalized
        
        # Otherwise, prefer existing (first one wins)
        return existing_normalized


# Singleton instance
_mapper = None

def get_category_mapper() -> CategoryMapper:
    """Get the singleton category mapper instance"""
    global _mapper
    if _mapper is None:
        _mapper = CategoryMapper()
    return _mapper
