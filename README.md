# Central Bot Database 🤖

[![Tests](https://github.com/philipjewell/central-bot-database/actions/workflows/test.yml/badge.svg)](https://github.com/philipjewell/central-bot-database/actions/workflows/test.yml)
[![PR Validation](https://github.com/philipjewell/central-bot-database/actions/workflows/pr-validation.yml/badge.svg)](https://github.com/philipjewell/central-bot-database/actions/workflows/pr-validation.yml)
[![Sync Bots](https://github.com/philipjewell/central-bot-database/actions/workflows/sync-bots.yml/badge.svg)](https://github.com/philipjewell/central-bot-database/actions/workflows/sync-bots.yml)
[![codecov](https://codecov.io/gh/philipjewell/central-bot-database/branch/main/graph/badge.svg)](https://codecov.io/gh/philipjewell/central-bot-database)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

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

## Web Application & API

🌐 **Browse the database online:** [https://central-bot-database.pages.dev](https://central-bot-database.pages.dev)

The bot database includes a modern web interface and RESTful API:

- **Interactive Table** - Search, filter, and sort bots by all fields
- **Category Recommendations** - Find the best bots for your site type
- **RESTful API** - Programmatic access via simple HTTP endpoints
- **robots.txt Generator** - Generate robots.txt files on-the-fly
- **Fast & Global** - Powered by Cloudflare Pages and Workers

### Deploy Your Own

```bash
# Fork the repository, then:
cd web
wrangler pages deploy . --project-name=central-bot-database
```

See [web/README.md](web/README.md) for detailed deployment instructions.

### API Quick Start

```bash
# Search for bots
curl "https://central-bot-database.pages.dev/api/search?q=googlebot"

# Get recommendations for e-commerce sites
curl "https://central-bot-database.pages.dev/api/recommend?category=ecommerce&rating=beneficial"

# Generate robots.txt
curl "https://central-bot-database.pages.dev/api/robots?category=ecommerce&block=harmful"
```

See the [API Documentation](https://central-bot-database.pages.dev/api.html) for all endpoints.

## Quick Start

### For Users

**Query the database:**
```bash
# Search for a specific bot
python scripts/bot_utils.py search "googlebot"

# Get recommendations for your site type
python scripts/bot_utils.py recommend ecommerce

# Generate a robots.txt file
python scripts/bot_utils.py robots ecommerce > robots.txt
```

**Use the JSON data:**
```python
import requests

# Load the database
url = "https://raw.githubusercontent.com/philipjewell/central-bot-database/main/data/bots.json"
data = requests.get(url).json()

# Filter for beneficial bots
good_bots = [bot for bot in data['bots']
             if bot['categories'].get('ecommerce') == 'beneficial']
```

### For Contributors

**Prerequisites:**
- Python 3.11+
- [Ollama](https://ollama.ai) with llama3.2 model (for local development)
- Git

**Setup:**
```bash
# Clone the repository
git clone https://github.com/philipjewell/central-bot-database.git
cd central-bot-database

# Install dependencies
pip install -r requirements.txt

# Install Ollama and model (for AI enrichment)
ollama pull llama3.2

# Run tests
pytest

# Run the pipeline locally
chmod +x run_pipeline.sh
./run_pipeline.sh
```

**Add your bot:**
1. Create a file in `sources/` (e.g., `sources/mybot.json`)
2. Use the template from `sources/README.md`
3. Run tests: `pytest`
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### For Maintainers

**GitHub Actions Setup:**
1. Add `CLOUDFLARE_API_TOKEN` in repository secrets (optional)
2. Add `PAT_TOKEN` for PR creation (required)
3. Workflows run automatically every Sunday at 2 AM UTC

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
1. Fetches latest bots from ai.robots.txt (all bots)
2. Optionally fetches from Cloudflare Radar (top 250 most common bots)
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
    "verification_method": "DNS reverse lookup",
    "cf_traffic_percentage": "0.123"
  },
  "last_updated": "2025-10-01T14:30:00Z"
}
```

### Field Descriptions

**Core Fields:**
- `user_agent` - The bot's user agent string as it appears in HTTP requests
- `operator` - **Bot category or classification.** This represents either:
  - The organization running the bot (e.g., "Google", "Amazon", "Ahrefs")
  - A functional category (e.g., "Search Engines", "Monitoring & Analytics", "AI Crawlers")
  - Source priority: Cloudflare category → ai.robots.txt function → company/owner → "Other"
- `purpose` - AI-generated description of what the bot does
- `description` - Additional context about the bot (from source data)
- `impact_of_blocking` - AI-generated explanation of consequences if you block this bot
- `website` - Official documentation or information page for the bot

**Categorization:**
- `categories` - Recommendations for 10 site types (ecommerce, news, media, blog, saas, corporate, documentation, social, portfolio, government)
  - `beneficial` - Generally recommended to allow
  - `neutral` - Depends on your use case
  - `harmful` - Generally recommended to block
  - `not_applicable` - Bot doesn't interact with this site type

**Metadata:**
- `sources` - Where the bot data came from (ai-robots-txt, cloudflare-radar, manual)
- `last_updated` - ISO 8601 timestamp, only updated when bot data actually changes

**Technical Details (raw_data):**
- `ip_ranges` - IP address ranges the bot operates from (CIDR notation)
- `asn` - Autonomous System Number(s)
- `verification_method` - How to verify the bot is legitimate
- `cf_traffic_percentage` - Cloudflare-specific metric showing relative traffic volume (only from cloudflare-radar source, cannot be set manually)

## Testing

This project uses pytest with comprehensive test coverage (>70% required for core logic).

**Run tests:**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=scripts --cov-report=html

# Run specific test file
pytest tests/test_merge_sources.py

# Run tests in verbose mode
pytest -v
```

**Test structure:**
- `tests/` - Unit tests for core business logic
- `conftest.py` - Shared test fixtures
- `pytest.ini` - Test configuration

**Coverage:**
- **Core scripts** (70% minimum): fetch, merge, validate, category mapping
- **Excluded from coverage**: CLI utilities, output generators, AI enrichment (requires Ollama)
- Current coverage: ~75% on tested scripts

**CI/CD:**
- All pull requests must pass tests before merging
- Coverage reports are uploaded to Codecov
- Tests run on every push to main and all PRs

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

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick Contribution:**
1. Fork the repository
2. Add your bot to `sources/` directory
3. Run tests: `pytest`
4. Submit a pull request

All PRs must:
- ✅ Pass unit tests (>70% coverage on core logic)
- ✅ Pass data validation
- ✅ Follow the schema in `sources/README.md`

## Data Sources

- **[ai.robots.txt](https://github.com/ai-robots-txt/ai.robots.txt)** - Community-maintained AI bot list (all bots)
- **[Cloudflare Radar](https://radar.cloudflare.com/)** - Verified bot traffic data (top 250 most common bots by traffic, optional)
- **Manual community submissions** - User-contributed bot entries in `sources/` directory

**Note:** The Cloudflare integration fetches the top 250 most common bots based on traffic patterns, not their entire bot database. This ensures we capture the most relevant bots while staying within API limits.

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
