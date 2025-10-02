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
            # Default mappings - empty to start, will be learned
            return {
                "": "Other",
                "Other": "Other",
                "Unknown": "Other",
                "Uncategorized": "Other"
            }
    
    def _build_reverse_mappings(self) -> Dict[str, Set[str]]:
        """Build reverse lookup: unified category -> set of source categories"""
        reverse = {}
        for source_cat, unified_cat in self.mappings.items():
            if unified_cat not in reverse:
                reverse[unified_cat] = set()
            reverse[unified_cat].add(source_cat)
        return reverse
    
    def get_category_for_bot(self, bot: Dict) -> str:
        """
        Get the category for a bot, respecting source priority:
        1. Cloudflare category (if present) - use as-is, NO mapping
        2. Manual category (if present) - use as-is, NO mapping
        3. Other sources - apply mapping
        """
        sources = bot.get("sources", [])
        category = bot.get("operator", "").strip()
        
        if not category:
            return "Other"
        
        # If bot has cloudflare-radar as a source, use its category directly
        if "cloudflare-radar" in sources:
            return category
        
        # If bot has manual as a source, use its category directly
        if "manual" in sources:
            return category
        
        # For other sources (ai-robots-txt, etc), apply mapping
        return self.normalize_category(category)
    
    def normalize_category(self, category: str) -> str:
        """Normalize a category to its unified form (only for non-Cloudflare sources)"""
        if not category or category.strip() == "":
            return "Other"
        
        # Check if we have a mapping for it
        if category in self.mappings:
            return self.mappings[category]
        
        # No mapping found - return as-is
        return category
    
    def merge_categories(self, existing_category: str, existing_sources: list, 
                        new_category: str, new_sources: list) -> str:
        """
        Merge categories when combining bot entries
        Priority: Cloudflare > Manual > Mapped
        """
        
        # If either has Cloudflare, use that
        if "cloudflare-radar" in existing_sources:
            return existing_category
        if "cloudflare-radar" in new_sources:
            return new_category
        
        # If either has Manual, prefer that
        if "manual" in existing_sources:
            return existing_category
        if "manual" in new_sources:
            return new_category
        
        # Both are from other sources - use existing (first wins)
        return existing_category
    
    def save_mappings(self) -> None:
        """Save current mappings to file"""
        mapping_file = Path("schemas/category_mappings.json")
        mapping_file.parent.mkdir(exist_ok=True)
        
        # Sort mappings alphabetically
        sorted_mappings = dict(sorted(self.mappings.items()))
        
        with open(mapping_file, 'w') as f:
            json.dump(sorted_mappings, f, indent=2)


# Singleton instance
_mapper = None

def get_category_mapper() -> CategoryMapper:
    """Get the singleton category mapper instance"""
    global _mapper
    if _mapper is None:
        _mapper = CategoryMapper()
    return _mapper
