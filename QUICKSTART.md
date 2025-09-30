# Quick Start Guide

Get up and running with the Bot Database in 5 minutes.

## Prerequisites

```bash
# Check you have Python 3.11+
python3 --version

# Install Ollama (for AI enrichment)
# Visit: https://ollama.ai
```

## Setup (First Time)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd bot-database

# 2. Run setup script
chmod +x setup.sh
./setup.sh

# 3. Pull AI model
ollama pull llama3.2
```

## Add Your First Bot

Edit `sources/manual_bots.json`:

```json
[
  {
    "user_agent": "MyBot/1.0",
    "operator": "My Company",
    "purpose": "What your bot does",
    "impact_of_blocking": "What happens if blocked",
    "website": "https://example.com/bot",
    "categories": {
      "ecommerce": "beneficial",
      "news": "neutral",
      "media": "beneficial",
      "blog": "beneficial",
      "saas": "neutral",
      "corporate": "beneficial",
      "documentation": "beneficial",
      "social": "not_applicable",
      "portfolio": "beneficial",
      "government": "neutral"
    },
    "sources": ["manual"],
    "raw_data": {
      "ip_ranges": ["192.0.2.0/24"],
      "asn": "AS64496",
      "verification_method": "DNS reverse lookup"
    }
  }
]
```

## Generate the Database

```bash
# Run the pipeline
chmod +x run_pipeline.sh
./run_pipeline.sh
```

## Check Your Outputs

```bash
# View JSON output
cat data/bots.json | jq '.bots[] | .user_agent'

# View Markdown
less docs/BOTS.md

# Or open in browser
open docs/BOTS.md
```

## Common Commands

### Search for a bot
```bash
python scripts/bot_utils.py search "googlebot"
```

### Get recommendations for your site
```bash
# For ecommerce site
python scripts/bot_utils.py recommend ecommerce

# For news site
python scripts/bot_utils.py recommend news --rating harmful
```

### Show bot details
```bash
python scripts/bot_utils.py details "Googlebot"
```

### Generate robots.txt
```bash
python scripts/bot_utils.py robots ecommerce > robots.txt
```

### View statistics
```bash
python scripts/bot_utils.py stats
```

### List all operators
```bash
python scripts/bot_utils.py operators
```

## Enable GitHub Actions

1. **Add Cloudflare Token** (optional):
   - Go to GitHub repo → Settings → Secrets
   - Add `CLOUDFLARE_API_TOKEN`

2. **Workflow runs automatically**:
   - Every Sunday at 2 AM UTC
   - Creates PR for review
   - Merge after reviewing

3. **Manual trigger**:
   - Go to Actions tab
   - Select "Sync and Enrich Bot Database"
   - Click "Run workflow"

## File Locations

| File | Purpose |
|------|---------|
| `sources/manual_bots.json` | Your manual bot entries (EDIT THIS) |
| `data/bots.json` | Generated JSON database (COMMIT THIS) |
| `docs/BOTS.md` | Generated documentation (COMMIT THIS) |
| `staging/` | Temporary files (DON'T COMMIT) |

## Typical Workflow

### Weekly (Automated)
1. GitHub Action runs
2. Pulls external data
3. Merges with your manual entries
4. Creates PR
5. You review and merge

### As Needed (Manual)
1. Edit `sources/manual_bots.json`
2. Run `./run_pipeline.sh`
3. Review changes with `git diff`
4. Commit and push

## Troubleshooting

### "Ollama not found"
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull model
ollama pull llama3.2
```

### "No bots found"
```bash
# Check if external sources are fetched
ls -la staging/

# Run individual scripts
python scripts/fetch_ai_robots.py
python scripts/fetch_cloudflare_radar.py
```

### "Cloudflare API error"
```bash
# Set token (optional - can skip Cloudflare)
export CLOUDFLARE_API_TOKEN='your-token-here'

# Or just use ai.robots.txt + manual entries
```

### "Validation errors"
```bash
# Check what's wrong
python scripts/validate_data.py

# Fix issues in sources/manual_bots.json
```

## Next Steps

1. **Customize Categories**: Adjust ratings based on your experience
2. **Add IP Ranges**: Include verification details for your bots
3. **Improve Descriptions**: Make AI-generated text more accurate
4. **Share**: Submit PRs to help others

## Getting Help

- 📖 Read `README.md` for detailed docs
- 🤝 Check `CONTRIBUTING.md` for guidelines
- 📊 See `EXAMPLE_OUTPUT.md` for examples
- 🔍 Review `PROJECT_OVERVIEW.md` for architecture
- 🐛 Open GitHub issue for bugs
- 💡 Open GitHub discussion for ideas

## Useful Links

- [Ollama Documentation](https://ollama.ai/docs)
- [ai.robots.txt](https://github.com/ai-robots-txt/ai.robots.txt)
- [Cloudflare Radar](https://radar.cloudflare.com)
- [robots.txt Spec](https://www.robotstxt.org)

## Quick Reference: Category Ratings

| Rating | Meaning | Example |
|--------|---------|---------|
| ✅ beneficial | Allow this bot | Search engines for most sites |
| ⚪ neutral | Case by case | Archive bots, research crawlers |
| ❌ harmful | Block this bot | Scrapers, unauthorized AI training |
| ➖ not_applicable | Bot doesn't apply | Mobile crawlers for web-only sites |

## Quick Reference: Site Types

| Type | Description | Examples |
|------|-------------|----------|
| ecommerce | Online stores | Amazon, Shopify sites |
| news | News outlets | CNN, local news |
| media | Streaming/galleries | YouTube, Spotify |
| blog | Content blogs | Medium, WordPress |
| saas | Web apps | Notion, Figma |
| corporate | Company sites | apple.com |
| documentation | Tech docs | docs.github.com |
| social | Social networks | Twitter, Reddit |
| portfolio | Personal sites | Artist portfolios |
| government | Gov sites | .gov domains |

## That's It!

You now have a working bot database. Run the pipeline, review the outputs, and start making informed decisions about which bots to allow or block on your sites.
