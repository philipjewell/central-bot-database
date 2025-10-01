# Central Bot Database 🤖

A comprehensive, automated database of internet bots with AI-powered categorization for different types of websites. This project aggregates bot information from multiple sources, enriches it with contextual descriptions, and provides recommendations for whether each bot should be allowed or blocked based on your site type.

## Features

✨ **Multi-Source Aggregation**
- Pulls from [ai.robots.txt](https://github.com/ai-robots-txt/ai.robots.txt) community database
- Optionally fetches from Cloudflare Radar API
- Supports manual bot entries for proprietary crawlers

🤖 **AI-Powered Enrichment**
- Uses local Ollama (llama3.2) for privacy-friendly AI descriptions
- Generates purpose descriptions for each bot
- Explains the impact of blocking each bot
- Provides category recommendations for 10 different site types

📊 **Dual Output Formats**
- **JSON** (`data/bots.json`) - Machine-readable for programmatic access
- **Markdown** (`docs/BOTS.md`) - Human-readable documentation

🔄 **Automated Weekly Updates**
- GitHub Actions workflow runs weekly
- Only enriches new or incomplete bots (preserves existing AI descriptions)
- Creates pull requests for human review
- Updates technical details (IP ranges, ASN) automatically

📝 **Site Type Categorization**

Each bot is rated for 10 website categories:
- E-commerce
- News
- Media
- Blog
- SaaS
- Corporate
- Documentation
- Social
- Portfolio
- Government

**Rating System:**
- ✅ **Beneficial** - Generally recommended to allow
- ⚪ **Neutral** - Depends on your use case
- ❌ **Harmful** - Generally recommended to block
- ➖ **Not Applicable** - Bot doesn't interact with this site type

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) with llama3.2 model (for AI enrichment)
- GitHub repository with Actions enabled
- (Optional) Cloudflare API token

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/central-bot-database.git
   cd central-bot-database
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama and pull the model**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.2
   ```

4. **Run the pipeline locally (optional)**
   ```bash
   chmod +x run_pipeline.sh
   ./run_pipeline.sh
   ```

### GitHub Actions Setup

1. **Add Cloudflare API Token** (optional)
   - Go to repository Settings → Secrets → Actions
   - Add `CLOUDFLARE_API_TOKEN` (if you have one)

2. **Add Personal Access Token** (required for PR creation)
   - Create a Fine-Grained Personal Access Token
   - Permissions needed: Contents (read/write), Pull Requests (read/write)
   - Add as `PAT_TOKEN` in repository secrets

3. **Enable GitHub Actions**
   - Workflows run automatically every Sunday at 2 AM UTC
   - Or trigger manually from the Actions tab

## Usage

### For Website Owners

**Find bots good for your site type:**

```bash
# View recommendations for e-commerce sites
python scripts/bot_utils.py recommend ecommerce

# Find bots you should block
python scripts/bot_utils.py recommend news --rating harmful
```

**Generate robots.txt:**

```bash
python scripts/bot_utils.py robots ecommerce > robots.txt
```

**Programmatic access:**

```python
import requests

# Load the database
url = "https://raw.githubusercontent.com/yourusername/central-bot-database/main/data/bots.json"
data = requests.get(url).json()

# Filter bots
good_bots = [
    bot for bot in data['bots'] 
    if bot['categories'].get('ecommerce') == 'beneficial'
]
```

### For Bot Operators

**Add your bot to the database:**

1. Edit `sources/manual_bots.json`:
   ```json
   {
     "user_agent": "YourBot/1.0",
     "operator": "Your Company",
     "purpose": "Brief description of what your bot does",
     "impact_of_blocking": "What happens if blocked",
     "website": "https://yourcompany.com/bot",
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
   ```

2. Submit a pull request

**Verify your bot is listed:**

```bash
python scripts/bot_utils.py search "YourBot"
python scripts/bot_utils.py details "YourBot/1.0"
```

## Project Structure

```
central-bot-database/
├── .github/workflows/
│   └── sync-bots.yml           # Automated workflow (3 phases)
├── scripts/
│   ├── fetch_ai_robots.py      # Fetch from ai.robots.txt
│   ├── fetch_cloudflare_radar.py # Fetch from Cloudflare
│   ├── merge_sources.py        # Merge & deduplicate
│   ├── enrich_with_ai.py       # AI enrichment (Ollama)
│   ├── fix_ratings.py          # Fix whitespace in ratings
│   ├── generate_outputs.py     # Generate JSON & Markdown
│   ├── validate_data.py        # Validate data integrity
│   └── bot_utils.py            # CLI utilities
├── sources/
│   └── manual_bots.json        # Your manual bot entries
├── schemas/
│   └── bot_schema.json         # JSON schema definition
├── data/
│   └── bots.json               # Generated JSON database
├── docs/
│   └── BOTS.md                 # Generated Markdown docs
├── staging/                    # Temporary processing files
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## How It Works

### Weekly Automation Workflow

**Phase 1: Fetch and Merge** (~1 minute)
1. Fetches latest bots from ai.robots.txt
2. Optionally fetches from Cloudflare Radar
3. Loads existing enriched database
4. Merges all sources, preserving existing AI enrichment
5. Only updates technical details (IP ranges, ASN)

**Phase 2: AI Enrichment** (~2-30 minutes, depends on new bots)
1. Installs and starts Ollama
2. Pulls llama3.2 model if needed
3. Only enriches NEW or INCOMPLETE bots
4. Skips bots that already have purpose, impact, and categories
5. Updates timestamps only for changed bots

**Phase 3: Generate and PR** (~1 minute)
1. Generates `data/bots.json` from enriched data
2. Generates `docs/BOTS.md` with human-readable format
3. Validates all data integrity
4. Creates pull request if changes detected
5. Waits for human approval before merging

### Key Design Decisions

**✅ Preserves Existing Enrichment**
- AI descriptions don't change on every run
- Consistent data across updates
- Faster processing (only enriches new bots)

**✅ Only Updates When Changed**
- `last_updated` timestamp only changes when data changes
- Clean git diffs show exactly what was modified
- No unnecessary PR noise

**✅ Privacy-Friendly AI**
- Uses local Ollama, not external APIs
- No data sent to third parties
- No API costs

**✅ Human-in-the-Loop**
- All updates require PR approval
- Review AI-generated descriptions before publishing
- Prevents accidental bad data

## Data Schema

Each bot entry includes:

```json
{
  "user_agent": "BotName/1.0",
  "operator": "Company Name",
  "purpose": "What the bot does",
  "description": "Additional context",
  "impact_of_blocking": "Consequences of blocking",
  "website": "https://company.com/bot",
  "categories": {
    "ecommerce": "beneficial",
    "news": "neutral",
    "media": "harmful",
    "blog": "beneficial",
    "saas": "not_applicable",
    "corporate": "neutral",
    "documentation": "beneficial",
    "social": "not_applicable",
    "portfolio": "beneficial",
    "government": "neutral"
  },
  "sources": ["ai-robots-txt", "manual"],
  "raw_data": {
    "ip_ranges": ["192.0.2.0/24"],
    "asn": "AS64496",
    "verification_method": "DNS reverse lookup"
  },
  "last_updated": "2025-10-01T14:30:00Z"
}
```

## CLI Utilities

```bash
# Search for bots
python scripts/bot_utils.py search "googlebot"

# Get recommendations by site type
python scripts/bot_utils.py recommend ecommerce
python scripts/bot_utils.py recommend news --rating harmful

# Show bot details
python scripts/bot_utils.py details "Googlebot"

# Generate robots.txt
python scripts/bot_utils.py robots ecommerce > robots.txt

# View statistics
python scripts/bot_utils.py stats

# List all operators
python scripts/bot_utils.py operators
```

## Contributing

We welcome contributions! Here's how:

1. **Add a new bot**: Edit `sources/manual_bots.json` and submit a PR
2. **Improve descriptions**: Open an issue with corrections
3. **Report bugs**: Open an issue with details
4. **Suggest features**: Open a discussion

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Data Sources

- [ai.robots.txt](https://github.com/ai-robots-txt/ai.robots.txt) - Community-maintained AI bot list
- [Cloudflare Radar](https://radar.cloudflare.com/) - Verified bot traffic data (optional)
- Manual community submissions

## License

MIT License - See [LICENSE](LICENSE) for details.

## Disclaimer

This database is provided as-is for informational purposes. Bot behaviors can change over time. Always verify bot legitimacy independently before implementing blocks. The AI-generated descriptions are for guidance only and should be reviewed for accuracy.

## Support

- 📖 Documentation: Check this README and `docs/BOTS.md`
- 🐛 Bug reports: [Open an issue](../../issues)
- 💬 Questions: [Start a discussion](../../discussions)
- 🤝 Contributing: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Acknowledgments

- [ai.robots.txt](https://github.com/ai-robots-txt/ai.robots.txt) community
- [Ollama](https://ollama.ai) for local AI inference
- [Cloudflare Radar](https://radar.cloudflare.com/) for bot verification data

---

**Built with ❤️ for a better, more transparent web**
