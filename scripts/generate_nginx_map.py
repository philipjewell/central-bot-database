#!/usr/bin/env python3
"""
Generate nginx map file that maps user agents to bot categories (operators)
"""
import json
from pathlib import Path
from datetime import datetime


def escape_nginx_regex(user_agent):
    """Escape special characters for nginx regex"""
    special_chars = ['.', '[', ']', '(', ')', '*', '+', '?', '{', '}', '^', '$', '|', '\\']
    escaped = user_agent
    for char in special_chars:
        escaped = escaped.replace(char, f'\\{char}')
    return escaped


def generate_nginx_map():
    """Generate nginx map file from bot database"""

    # Load bot database
    db_file = Path("data/bots.json")
    if not db_file.exists():
        print(f"✗ Error: {db_file} not found")
        return 1

    with open(db_file, 'r') as f:
        data = json.load(f)

    bots = data.get('bots', [])
    print(f"✓ Loaded {len(bots)} bots from {db_file}")

    # Create output directory
    output_dir = Path("nginx")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "bot_category_map.conf"

    # Generate map file
    lines = [
        "# Bot Category Mapping for nginx",
        f"# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "# Source: Central Bot Database",
        "#",
        "# This map assigns each bot user agent to its operator category.",
        "# Use this to identify and rate limit bots by category.",
        "#",
        "# Usage: Include this file in your nginx http block:",
        "#   include /path/to/bot_category_map.conf;",
        "#",
        "# Then use $bot_category in your server/location blocks for rate limiting.",
        "",
        "map $http_user_agent $bot_category {",
        "    default \"unknown\";",
        ""
    ]

    # Group bots by operator for better organization
    operators = {}
    for bot in bots:
        operator = bot.get('operator', 'Other')
        if operator not in operators:
            operators[operator] = []
        operators[operator].append(bot)

    # Sort operators alphabetically
    for operator in sorted(operators.keys()):
        lines.append(f"    # {operator}")

        for bot in sorted(operators[operator], key=lambda x: x.get('user_agent', '')):
            user_agent = bot.get('user_agent', '')
            if user_agent:
                escaped_ua = escape_nginx_regex(user_agent)
                lines.append(f'    ~*{escaped_ua} "{operator}";')

        lines.append("")

    lines.append("}")
    lines.append("")

    # Write to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✓ Generated {output_file}")
    print(f"✓ Mapped {len(bots)} bots across {len(operators)} categories")
    print(f"\nCategories included:")
    for operator in sorted(operators.keys()):
        print(f"  - {operator}: {len(operators[operator])} bots")

    return 0


if __name__ == '__main__':
    exit(generate_nginx_map())
