"""
Generate final JSON and Markdown outputs
"""
import json
from pathlib import Path
from datetime import datetime

def generate_json_output(bots):
    """Generate the final JSON output"""
    
    output = {
        "meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "version": "1.0",
            "total_bots": len(bots),
            "description": "Comprehensive database of internet bots with categorization by site type"
        },
        "bots": bots
    }
    
    # Save to data directory
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "bots.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Generated JSON output: {output_file}")
    return output_file

def format_category_badge(rating):
    """Format category rating as emoji badge"""
    badges = {
        "beneficial": "✅",
        "neutral": "⚪",
        "harmful": "❌",
        "not_applicable": "➖"
    }
    return badges.get(rating, "❓")

def generate_markdown_output(bots):
    """Generate human-readable Markdown documentation"""
    
    md_lines = [
        "# Bot Database",
        "",
        f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Total bots: **{len(bots)}**",
        "",
        "## Legend",
        "",
        "### Category Ratings",
        "- ✅ **Beneficial** - Generally recommended to allow",
        "- ⚪ **Neutral** - Depends on your specific use case",
        "- ❌ **Harmful** - Generally recommended to block",
        "- ➖ **Not Applicable** - Bot doesn't interact with this site type",
        "",
        "### Site Categories",
        "- **ecommerce** - Online stores and shopping sites",
        "- **news** - News publications and journalism sites",
        "- **media** - Video/audio streaming, galleries, entertainment",
        "- **blog** - Personal and professional blogs",
        "- **saas** - Software-as-a-Service platforms",
        "- **corporate** - Corporate and business websites",
        "- **documentation** - Technical docs, wikis, knowledge bases",
        "- **social** - Social media platforms",
        "- **portfolio** - Personal portfolios and showcase sites",
        "- **government** - Government and public sector sites",
        "",
        "## Table of Contents",
        ""
    ]
    
    # Group bots by operator
    operators = {}
    for bot in bots:
        operator = bot.get("operator", "Unknown")
        if operator not in operators:
            operators[operator] = []
        operators[operator].append(bot)
    
    # Add TOC
    for operator in sorted(operators.keys()):
        anchor = operator.lower().replace(' ', '-').replace('.', '').replace('/', '').replace('(', '').replace(')', '')
        md_lines.append(f"- [{operator}](#{anchor}) ({len(operators[operator])} bot{'s' if len(operators[operator]) > 1 else ''})")
    
    md_lines.extend(["", "---", ""])
    
    # Add detailed entries
    for operator in sorted(operators.keys()):
        anchor = operator.lower().replace(' ', '-').replace('.', '').replace('/', '').replace('(', '').replace(')', '')
        md_lines.append(f"## {operator}")
        md_lines.append("")
        
        for bot in sorted(operators[operator], key=lambda x: x.get("user_agent", "")):
            user_agent = bot.get("user_agent", "Unknown")
            purpose = bot.get("purpose", "No description available")
            impact = bot.get("impact_of_blocking", "Impact unknown")
            categories = bot.get("categories", {})
            sources = bot.get("sources", [])
            website = bot.get("website", "")
            
            # Technical details from raw_data
            raw_data = bot.get("raw_data", {})
            ip_ranges = raw_data.get("ip_ranges", [])
            asn = raw_data.get("asn", "")
            asn_list = raw_data.get("asn_list", [])
            verification_method = raw_data.get("verification_method", "")
            
            md_lines.append(f"### {user_agent}")
            md_lines.append("")
            
            # Purpose
            md_lines.append(f"**Purpose:** {purpose}")
            md_lines.append("")
            
            # Impact
            md_lines.append(f"**Impact of Blocking:** {impact}")
            md_lines.append("")
            
            # Technical details if available
            tech_details = []
            if ip_ranges:
                tech_details.append(f"**IP Ranges:** `{', '.join(ip_ranges)}`")
            if asn:
                tech_details.append(f"**ASN:** `{asn}`")
            if asn_list:
                tech_details.append(f"**ASN:** `{', '.join(map(str, asn_list))}`")
            if verification_method:
                tech_details.append(f"**Verification:** {verification_method}")
            
            if tech_details:
                md_lines.extend(tech_details)
                md_lines.append("")
            
            # Website
            if website:
                md_lines.append(f"**Website:** [{website}]({website})")
                md_lines.append("")
            
            # Category recommendations
            if categories:
                md_lines.append("**Recommendations by Site Type:**")
                md_lines.append("")
                md_lines.append("| Category | Rating |")
                md_lines.append("|----------|--------|")
                
                for category in ["ecommerce", "news", "media", "blog", "saas", 
                                "corporate", "documentation", "social", "portfolio", "government"]:
                    rating = categories.get(category, "neutral")
                    badge = format_category_badge(rating)
                    md_lines.append(f"| {category.capitalize()} | {badge} {rating.replace('_', ' ').title()} |")
                
                md_lines.append("")
            
            # Sources
            md_lines.append(f"**Sources:** {', '.join(sources)}")
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
    
    # Add footer
    md_lines.extend([
        "## Contributing",
        "",
        "To add a bot manually, edit `sources/manual_bots.json` and submit a pull request.",
        "",
        "## Data Sources",
        "",
        "This database is compiled from:",
        "- [ai.robots.txt](https://github.com/ai-robots-txt/ai.robots.txt) - Community-maintained list of AI bots",
        "- [Cloudflare Radar](https://radar.cloudflare.com/) - Verified bot traffic data",
        "- Manual submissions from the community",
        "",
        "## License",
        "",
        "This database is provided as-is for informational purposes. Please verify bot behavior independently before implementing blocks.",
        ""
    ])
    
    # Save to docs directory
    output_dir = Path("docs")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "BOTS.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(md_lines))
    
    print(f"✓ Generated Markdown output: {output_file}")
    return output_file

def generate_outputs():
    """Generate both JSON and Markdown outputs"""
    
    # Load enriched bots
    enriched_file = Path("staging/enriched_bots.json")
    if not enriched_file.exists():
        print("✗ No enriched bots file found")
        return
    
    with open(enriched_file, 'r') as f:
        bots = json.load(f)
    
    print(f"\nGenerating outputs for {len(bots)} bots...\n")
    
    # Generate both formats
    generate_json_output(bots)
    generate_markdown_output(bots)
    
    print("\n✓ All outputs generated successfully")

if __name__ == "__main__":
    generate_outputs()
