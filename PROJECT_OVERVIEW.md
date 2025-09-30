# Bot Database - Project Overview

## Complete File Structure

```
bot-database/
├── .github/
│   └── workflows/
│       └── sync-bots.yml              # Weekly automation workflow
├── scripts/
│   ├── fetch_ai_robots.py             # Pull from ai.robots.txt
│   ├── fetch_cloudflare_radar.py      # Pull from Cloudflare Radar API
│   ├── merge_sources.py               # Merge & deduplicate bots
│   ├── enrich_with_ai.py              # Add AI-generated descriptions
│   ├── generate_outputs.py            # Create JSON & Markdown outputs
│   └── validate_data.py               # Validate data integrity
├── sources/
│   └── manual_bots.json               # Your manually-added bots
├── schemas/
│   └── bot_schema.json                # JSON schema definition
├── data/
│   └── bots.json                      # Generated JSON output (commit this)
├── docs/
│   └── BOTS.md                        # Generated Markdown docs (commit this)
├── staging/                           # Temporary files (gitignored)
│   ├── ai_robots_bots.json
│   ├── cloudflare_bots.json
│   ├── merged_bots.json
│   └── enriched_bots.json
├── venv/                              # Python virtual environment (gitignored)
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # Python dependencies
├── setup.sh                           # First-time setup script
├── run_pipeline.sh                    # Manual pipeline runner
├── README.md                          # Main documentation
├── CONTRIBUTING.md                    # Contribution guidelines
└── PROJECT_OVERVIEW.md               # This file
```

## Data Flow

```
┌─────────────────────┐
│ External Sources    │
├─────────────────────┤
│ • ai.robots.txt     │
│ • Cloudflare Radar  │
└──────────┬──────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌──────────────────┐    ┌─────────────────┐
│ fetch_ai_robots  │    │ fetch_cloudflare│
└────────┬─────────┘    └────────┬────────┘
         │                       │
         │    ┌─────────────────────────┐
         │    │ sources/manual_bots.json│
         │    └──────────┬──────────────┘
         │               │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ merge_sources │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ enrich_with_ai│ (Ollama/llama3.2)
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │generate_outputs│
         └───────┬───────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ data/bots.json│  │ docs/BOTS.md│
└──────────────┘  └──────────────┘
```

## Workflow Steps

### 1. **Fetching** (fetch_ai_robots.py & fetch_cloudflare_radar.py)

- Downloads bot lists from external sources
- Transforms to internal format
- Extracts IP ranges, ASN, verification methods
- Saves to `staging/` directory

### 2. **Merging** (merge_sources.py)

- Loads all sources (external + manual)
- Normalizes user agent strings
- Deduplicates by user agent
- **Manual entries take precedence** over external sources
- Merges metadata (IP ranges, ASN, etc.)
- Outputs `staging/merged_bots.json`

### 3. **Enrichment** (enrich_with_ai.py)

- Uses local Ollama (llama3.2 model)
- Generates:
  - **Purpose**: What the bot does and why
  - **Impact of blocking**: Consequences of blocking
  - **Category ratings**: Recommendations for 10 site types
- Skips manual entries that are already complete
- Outputs `staging/enriched_bots.json`

### 4. **Output Generation** (generate_outputs.py)

- Creates `data/bots.json` (machine-readable)
- Creates `docs/BOTS.md` (human-readable)
- Includes all metadata:
  - IP ranges
  - ASN information
  - Verification methods
  - Category recommendations
  - Sources

### 5. **Validation** (validate_data.py)

- Checks data integrity
- Validates required fields
- Checks category ratings
- Detects duplicates
- Generates statistics

## Automation

### GitHub Actions Workflow

**Trigger**: Weekly on Sundays at 2 AM UTC (or manual trigger)

**Process**:
1. Fetch from external sources
2. Merge with manual entries
3. Enrich with AI
4. Generate outputs
5. Validate data
6. **Create Pull Request** (requires human review)
7. Wait for approval before merging

**Why Pull Requests?**
- Human oversight on AI-generated content
- Catch errors or inconsistencies
- Review new bots before publishing
- Maintain quality control

## Key Features

### 1. **Multi-Source Aggregation**
- Combines data from multiple authoritative sources
- Manual entries for bots not in public databases
- Automatic deduplication

### 2. **Technical Details**
Captures valuable information:
- IP address ranges for bot verification
- ASN (Autonomous System Numbers)
- Verification methods (DNS, IP, headers)
- Official documentation links

### 3. **Intelligent Categorization**
10 website categories:
- ecommerce
- news
- media
- blog
- saas
- corporate
- documentation
- social
- portfolio
- government

4 rating levels:
- beneficial
- neutral
- harmful
- not_applicable

### 4. **AI Enrichment**
Uses local Ollama (privacy-friendly):
- No external API costs
- No data sent to third parties
- Consistent, contextual descriptions
- Category recommendations based on bot behavior

### 5. **Dual Output Formats**

**JSON** (`data/bots.json`):
- Machine-readable
- Complete metadata
- Programmatic access
- API integration ready

**Markdown** (`docs/BOTS.md`):
- Human-readable
- Searchable
- GitHub-friendly
- Easy reference

## Manual Bot Entry Priority

When you add a bot to `sources/manual_bots.json`:

1. **Manual data always wins** - Your values override external sources
2. **Partial entries work** - Fill in what you know, AI fills the rest
3. **Full control** - Completely define descriptions and ratings
4. **Technical details** - Add IP ranges, ASN not available elsewhere

## Common Use Cases

### As a Website Owner
Query the database to decide which bots to allow/block based on your site type.

### As a Bot Operator
Add your bot with accurate information to help website owners make informed decisions.

### As a Researcher
Analyze bot trends, operators, and behaviors across the internet.

### As a Developer
Integrate the JSON API into your robots.txt generation tools.

## Setup Options

### Option 1: Automated (GitHub Actions)
1. Fork repository
2. Add `CLOUDFLARE_API_TOKEN` secret (optional)
3. Wait for weekly PRs
4. Review and merge

### Option 2: Manual (Local)
1. Run `./setup.sh`
2. Edit `sources/manual_bots.json`
3. Run `./run_pipeline.sh`
4. Commit `data/bots.json` and `docs/BOTS.md`

### Option 3: Hybrid
- Use GitHub Actions for external sources
- Manually add/update bots as needed
- Review automated PRs weekly

## Requirements

- **Python 3.11+**
- **Ollama** with llama3.2 model (for AI enrichment)
- **Cloudflare API Token** (optional, for Cloudflare data)
- **GitHub** (for automated workflows)

## Security & Privacy

- ✅ Uses local LLM (no data sent to external APIs)
- ✅ All data is public (no sensitive information)
- ✅ Open source and auditable
- ✅ No tracking or analytics
- ✅ Rate limiting to respect API limits

## Maintenance

### Weekly (Automated)
- Pull latest bot lists
- Update descriptions
- Generate new outputs
- Create PR for review

### As Needed (Manual)
- Add new bots to manual_bots.json
- Correct inaccurate information
- Update category ratings
- Add technical details

## Future Enhancements

Potential additions:
- Web dashboard for browsing
- REST API endpoint
- robots.txt generator
- Browser extension
- Integration with popular CMS platforms
- Historical tracking of bot changes
- Reputation scoring system

## License

MIT License - Free to use, modify, and distribute.

## Support

- 📖 Check README.md for setup
- 🤝 See CONTRIBUTING.md for adding bots
- 🐛 Open GitHub issues for bugs
- 💡 Open GitHub discussions for ideas
