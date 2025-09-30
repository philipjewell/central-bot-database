# Example Output

This document shows what the final generated outputs will look like.

## JSON Output Example (`data/bots.json`)

```json
{
  "meta": {
    "generated_at": "2025-09-30T14:30:00Z",
    "version": "1.0",
    "total_bots": 3,
    "description": "Comprehensive database of internet bots with categorization by site type"
  },
  "bots": [
    {
      "user_agent": "Googlebot",
      "operator": "Google",
      "purpose": "Crawls and indexes web pages for Google Search, helping websites get discovered by users searching for relevant content.",
      "description": "Google's web crawler",
      "impact_of_blocking": "Your website will not appear in Google Search results, significantly reducing organic traffic and discoverability.",
      "website": "https://developers.google.com/search/docs/crawling-indexing/googlebot",
      "categories": {
        "ecommerce": "beneficial",
        "news": "beneficial",
        "media": "beneficial",
        "blog": "beneficial",
        "saas": "beneficial",
        "corporate": "beneficial",
        "documentation": "beneficial",
        "social": "neutral",
        "portfolio": "beneficial",
        "government": "beneficial"
      },
      "sources": ["ai-robots-txt", "cloudflare-radar"],
      "raw_data": {
        "ip_ranges": [
          "66.249.64.0/19",
          "66.249.64.0/20"
        ],
        "asn": "AS15169",
        "verification_method": "DNS reverse lookup",
        "rank": 1
      },
      "last_updated": "2025-09-30T14:30:00Z"
    },
    {
      "user_agent": "GPTBot",
      "operator": "OpenAI",
      "purpose": "Collects web data to train OpenAI's language models, including GPT-4 and ChatGPT, helping improve AI understanding of internet content.",
      "description": "OpenAI's web crawler for AI training",
      "impact_of_blocking": "Your content will not be used to train future OpenAI models, which may affect the AI's knowledge about your domain or industry.",
      "website": "https://platform.openai.com/docs/gptbot",
      "categories": {
        "ecommerce": "neutral",
        "news": "harmful",
        "media": "harmful",
        "blog": "neutral",
        "saas": "neutral",
        "corporate": "neutral",
        "documentation": "beneficial",
        "social": "not_applicable",
        "portfolio": "neutral",
        "government": "harmful"
      },
      "sources": ["ai-robots-txt"],
      "raw_data": {
        "ip_ranges": [],
        "asn": "",
        "verification_method": "User-agent string",
        "documentation_url": "https://platform.openai.com/docs/gptbot"
      },
      "last_updated": "2025-09-30T14:30:00Z"
    },
    {
      "user_agent": "MyCompanyBot/1.0",
      "operator": "My Company",
      "purpose": "Monitors website uptime and performance metrics for our customers, providing real-time alerts and analytics.",
      "description": "Our proprietary monitoring bot",
      "impact_of_blocking": "Monitoring services for your website will fail, preventing uptime tracking and performance analysis for our mutual customers.",
      "website": "https://example.com/bot",
      "categories": {
        "ecommerce": "beneficial",
        "news": "beneficial",
        "media": "beneficial",
        "blog": "beneficial",
        "saas": "beneficial",
        "corporate": "beneficial",
        "documentation": "beneficial",
        "social": "neutral",
        "portfolio": "beneficial",
        "government": "neutral"
      },
      "sources": ["manual"],
      "raw_data": {
        "ip_ranges": ["192.0.2.0/24", "198.51.100.0/24"],
        "asn": "AS64496",
        "asn_list": ["AS64496"],
        "verification_method": "DNS reverse lookup on crawler IPs",
        "documentation_url": "https://example.com/bot/verify"
      },
      "last_updated": "2025-09-30T14:30:00Z"
    }
  ]
}
```

## Markdown Output Example (`docs/BOTS.md`)

```markdown
# Bot Database

Last updated: 2025-09-30 14:30 UTC

Total bots: **3**

## Legend

### Category Ratings
- ✅ **Beneficial** - Generally recommended to allow
- ⚪ **Neutral** - Depends on your specific use case
- ❌ **Harmful** - Generally recommended to block
- ➖ **Not Applicable** - Bot doesn't interact with this site type

### Site Categories
- **ecommerce** - Online stores and shopping sites
- **news** - News publications and journalism sites
- **media** - Video/audio streaming, galleries, entertainment
- **blog** - Personal and professional blogs
- **saas** - Software-as-a-Service platforms
- **corporate** - Corporate and business websites
- **documentation** - Technical docs, wikis, knowledge bases
- **social** - Social media platforms
- **portfolio** - Personal portfolios and showcase sites
- **government** - Government and public sector sites

## Table of Contents

- [Google](#google) (1 bot)
- [My Company](#my-company) (1 bot)
- [OpenAI](#openai) (1 bot)

---

## Google

### Googlebot

**Purpose:** Crawls and indexes web pages for Google Search, helping websites get discovered by users searching for relevant content.

**Impact of Blocking:** Your website will not appear in Google Search results, significantly reducing organic traffic and discoverability.

**IP Ranges:** `66.249.64.0/19, 66.249.64.0/20`

**ASN:** `AS15169`

**Verification:** DNS reverse lookup

**Website:** [https://developers.google.com/search/docs/crawling-indexing/googlebot](https://developers.google.com/search/docs/crawling-indexing/googlebot)

**Recommendations by Site Type:**

| Category | Rating |
|----------|--------|
| Ecommerce | ✅ Beneficial |
| News | ✅ Beneficial |
| Media | ✅ Beneficial |
| Blog | ✅ Beneficial |
| Saas | ✅ Beneficial |
| Corporate | ✅ Beneficial |
| Documentation | ✅ Beneficial |
| Social | ⚪ Neutral |
| Portfolio | ✅ Beneficial |
| Government | ✅ Beneficial |

**Sources:** ai-robots-txt, cloudflare-radar

---

## My Company

### MyCompanyBot/1.0

**Purpose:** Monitors website uptime and performance metrics for our customers, providing real-time alerts and analytics.

**Impact of Blocking:** Monitoring services for your website will fail, preventing uptime tracking and performance analysis for our mutual customers.

**IP Ranges:** `192.0.2.0/24, 198.51.100.0/24`

**ASN:** `AS64496`

**Verification:** DNS reverse lookup on crawler IPs

**Website:** [https://example.com/bot](https://example.com/bot)

**Recommendations by Site Type:**

| Category | Rating |
|----------|--------|
| Ecommerce | ✅ Beneficial |
| News | ✅ Beneficial |
| Media | ✅ Beneficial |
| Blog | ✅ Beneficial |
| Saas | ✅ Beneficial |
| Corporate | ✅ Beneficial |
| Documentation | ✅ Beneficial |
| Social | ⚪ Neutral |
| Portfolio | ✅ Beneficial |
| Government | ⚪ Neutral |

**Sources:** manual

---

## OpenAI

### GPTBot

**Purpose:** Collects web data to train OpenAI's language models, including GPT-4 and ChatGPT, helping improve AI understanding of internet content.

**Impact of Blocking:** Your content will not be used to train future OpenAI models, which may affect the AI's knowledge about your domain or industry.

**Website:** [https://platform.openai.com/docs/gptbot](https://platform.openai.com/docs/gptbot)

**Recommendations by Site Type:**

| Category | Rating |
|----------|--------|
| Ecommerce | ⚪ Neutral |
| News | ❌ Harmful |
| Media | ❌ Harmful |
| Blog | ⚪ Neutral |
| Saas | ⚪ Neutral |
| Corporate | ⚪ Neutral |
| Documentation | ✅ Beneficial |
| Social | ➖ Not Applicable |
| Portfolio | ⚪ Neutral |
| Government | ❌ Harmful |

**Sources:** ai-robots-txt

---

## Contributing

To add a bot manually, edit `sources/manual_bots.json` and submit a pull request.

## Data Sources

This database is compiled from:
- [ai.robots.txt](https://github.com/ai-robots-txt/ai.robots.txt) - Community-maintained list of AI bots
- [Cloudflare Radar](https://radar.cloudflare.com/) - Verified bot traffic data
- Manual submissions from the community

## License

This database is provided as-is for informational purposes. Please verify bot behavior independently before implementing blocks.
```

## How to Use These Outputs

### For Website Owners

**Using the JSON:**
```python
import json
import requests

# Load bot database
response = requests.get('https://raw.githubusercontent.com/your-repo/main/data/bots.json')
bots = response.json()

# Find bots good for your site type
site_type = 'ecommerce'
good_bots = [
    bot for bot in bots['bots'] 
    if bot['categories'].get(site_type) == 'beneficial'
]

# Generate robots.txt
for bot in good_bots:
    print(f"# Allow {bot['user_agent']} - {bot['operator']}")
    print(f"User-agent: {bot['user_agent']}")
    print("Allow: /\n")
```

**Using the Markdown:**
1. Browse to your site category (e.g., "ecommerce")
2. Look for ✅ Beneficial ratings
3. Read the impact of blocking
4. Make informed decisions

### For Bot Operators

**Verify Your Bot is Listed:**
```bash
# Check if your bot is in the database
curl -s https://raw.githubusercontent.com/your-repo/main/data/bots.json | \
  jq '.bots[] | select(.user_agent | contains("YourBot"))'
```

**Add Missing Information:**
1. Find your bot in the Markdown
2. Note missing IP ranges or ASN
3. Submit PR with complete details

### For Developers

**API Integration Example:**
```javascript
// Fetch bot database
const response = await fetch('https://raw.githubusercontent.com/your-repo/main/data/bots.json');
const data = await response.json();

// Filter by operator
const googleBots = data.bots.filter(bot => bot.operator === 'Google');

// Find harmful bots for your site type
const harmfulForNews = data.bots.filter(bot => 
  bot.categories.news === 'harmful'
);

// Generate nginx block rules
harmfulForNews.forEach(bot => {
  console.log(`if ($http_user_agent ~* "${bot.user_agent}") { return 403; }`);
});
```

### For Researchers

**Analysis Examples:**
```python
import json
import pandas as pd

# Load data
with open('data/bots.json') as f:
    data = json.load(f)

df = pd.DataFrame(data['bots'])

# Most common operators
print(df['operator'].value_counts().head(10))

# Bots with IP ranges
bots_with_ips = df[df['raw_data'].apply(lambda x: len(x.get('ip_ranges', [])) > 0)]
print(f"Bots with IP ranges: {len(bots_with_ips)}")

# Category distribution
categories_df = pd.DataFrame([bot['categories'] for bot in data['bots']])
print(categories_df.apply(pd.Series.value_counts))
```

## Real-World Use Cases

### 1. E-commerce Site
**Goal:** Maximize product visibility while preventing scraping

**Strategy:**
- Allow: ✅ Search engines (Googlebot, Bingbot)
- Allow: ✅ Price comparison bots
- Block: ❌ Content scrapers
- Block: ❌ Unauthorized AI trainers

### 2. News Publisher
**Goal:** Protect original content, allow syndication

**Strategy:**
- Allow: ✅ Search engines
- Allow: ✅ News aggregators (with agreements)
- Block: ❌ AI training bots (GPTBot, ClaudeBot without permission)
- Block: ❌ Content thieves

### 3. Technical Documentation
**Goal:** Maximum reach for developers

**Strategy:**
- Allow: ✅ All search engines
- Allow: ✅ AI training bots (help AI answer coding questions)
- Allow: ✅ Archive bots
- Neutral: ⚪ Research crawlers

### 4. Personal Portfolio
**Goal:** Get discovered

**Strategy:**
- Allow: ✅ Everything beneficial
- Monitor: ⚪ Neutral bots
- Case-by-case: Decide based on purpose

## Statistics You Can Generate

From the outputs, you can analyze:
- Total number of bots
- Bots per operator
- Bots with verification methods
- Bots with IP ranges
- Category rating distributions
- Source coverage (ai.robots.txt vs Cloudflare)
- Manual vs automated entries
- Enrichment completion rate

## Updating the Database

### Weekly Automated Updates
1. GitHub Action runs on Sunday
2. Fetches latest data
3. Merges with manual entries
4. AI enriches new bots
5. Creates PR with changes
6. You review and approve
7. Database updates

### Manual Updates Anytime
1. Edit `sources/manual_bots.json`
2. Run `./run_pipeline.sh`
3. Review outputs
4. Commit and push
5. Database updates immediately
