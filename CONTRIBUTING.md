# Contributing to Bot Database

Thank you for your interest in contributing! This guide will help you add new bots or improve existing entries.

## Ways to Contribute

1. **Add new bots** not yet in the database
2. **Improve bot descriptions** with better context
3. **Update category recommendations** based on real-world experience
4. **Add technical details** like IP ranges or ASN information
5. **Report issues** with incorrect bot information

## Adding a New Bot

### Step 1: Fork and Clone

```bash
git clone https://github.com/your-username/bot-database.git
cd bot-database
```

### Step 2: Edit Manual Bots File

Open `sources/manual_bots.json` and add your bot entry:

```json
{
  "user_agent": "YourBot/1.0",
  "operator": "Your Company Name",
  "purpose": "A clear, concise description of what your bot does (1-2 sentences)",
  "description": "Additional context if needed",
  "impact_of_blocking": "What happens if someone blocks your bot (1-2 sentences)",
  "website": "https://yourcompany.com/bot-documentation",
  "categories": {
    "ecommerce": "beneficial",
    "news": "beneficial",
    "media": "neutral",
    "blog": "beneficial",
    "saas": "not_applicable",
    "corporate": "neutral",
    "documentation": "beneficial",
    "social": "not_applicable",
    "portfolio": "beneficial",
    "government": "harmful"
  },
  "sources": ["manual"],
  "raw_data": {
    "ip_ranges": ["192.0.2.0/24", "198.51.100.0/24"],
    "asn": "AS64496",
    "asn_list": ["AS64496", "AS64497"],
    "verification_method": "DNS reverse lookup",
    "documentation_url": "https://yourcompany.com/bot/verify"
  }
}
```

### Step 3: Understanding Category Ratings

Rate your bot for each website type:

#### Rating Definitions

- **`beneficial`** - Website owners should generally allow this bot
  - Examples: Search engine crawlers for ecommerce sites, news aggregators for news sites
  - Blocking would harm the site owner's interests

- **`neutral`** - Depends on the specific website's goals
  - Examples: Archive bots for most sites, research crawlers
  - No clear benefit or harm

- **`harmful`** - Website owners should generally block this bot
  - Examples: Scraping bots that steal content, aggressive crawlers
  - Can cause harm through content theft or server load

- **`not_applicable`** - Bot doesn't interact with this type of site
  - Examples: Mobile app crawlers for websites, specialized industry bots
  - Bot's purpose is incompatible with this site type

#### Site Category Definitions

- **ecommerce**: Online stores, shopping carts, product catalogs
- **news**: News outlets, journalism, online magazines
- **media**: Streaming services, video/audio platforms, image galleries
- **blog**: Personal blogs, professional blogs, content creators
- **saas**: Software-as-a-Service platforms, web applications
- **corporate**: Company websites, business information sites
- **documentation**: Technical docs, API references, wikis, knowledge bases
- **social**: Social networks, community platforms, forums
- **portfolio**: Personal portfolios, artist showcases, resume sites
- **government**: Government agencies, public sector, civic sites

### Step 4: Technical Details (Optional but Encouraged)

Include as much technical information as possible:

#### IP Ranges
```json
"ip_ranges": [
  "192.0.2.0/24",
  "198.51.100.0/24",
  "2001:db8::/32"
]
```

#### ASN (Autonomous System Number)
```json
"asn": "AS64496"
```
or for multiple:
```json
"asn_list": ["AS64496", "AS64497", "AS64498"]
```

#### Verification Method
How website owners can verify your bot is legitimate:
```json
"verification_method": "DNS reverse lookup on crawler IPs"
```

Common methods:
- DNS reverse lookup
- User-agent + IP verification
- Request header validation
- Published IP ranges
- API verification endpoint

### Step 5: Validate Your Entry

```bash
# Install dependencies
pip install -r requirements.txt

# Run validation
python scripts/validate_data.py
```

### Step 6: Submit Pull Request

```bash
git checkout -b add-bot-yourbot
git add sources/manual_bots.json
git commit -m "Add YourBot to manual entries"
git push origin add-bot-yourbot
```

Create a pull request with:
- **Title**: "Add [BotName] to bot database"
- **Description**: Brief explanation of the bot and why it should be included

## Updating Existing Bots

If you find incorrect information:

1. Open an issue describing the problem
2. Or submit a PR with corrections to `sources/manual_bots.json`
3. Include sources/references for your corrections

## Guidelines

### Do's ✅

- **Be honest** about your bot's purpose
- **Be specific** in descriptions (avoid marketing speak)
- **Be accurate** with technical details
- **Be fair** in category ratings
- **Include verification methods** for bot legitimacy
- **Link to documentation** where possible

### Don'ts ❌

- **Don't exaggerate** your bot's benefits
- **Don't hide** harmful behaviors
- **Don't game** category ratings
- **Don't omit** information about scraping/archiving
- **Don't submit** bots you don't operate (unless improving existing entries)

## Review Process

1. **Automated checks**: GitHub Actions validates your submission
2. **Maintainer review**: We check accuracy and completeness
3. **Community feedback**: Other contributors may comment
4. **Merge**: Once approved, your bot is added to the database

## Questions?

- Open an issue for questions
- Check existing issues for similar questions
- Review the main README.md for setup help

## Code of Conduct

Be respectful, honest, and constructive. We're building a resource for everyone.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).
