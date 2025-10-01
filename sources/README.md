# Manual Bot Submissions

This directory contains manually submitted bot definitions. Each bot should have its own JSON file.

## How to Add Your Bot

1. **Create a new file** named after your bot (e.g., `yourbot.json`)
2. **Use the template below** or copy `example_bot.json`
3. **Fill in all fields** with accurate information
4. **Submit a pull request**

## File Naming Convention

- Use lowercase with underscores: `my_company_bot.json`
- Or use the bot name: `googlebot.json`
- One bot per file (preferred) or multiple bots in an array

## Template (Single Bot)

```json
{
  "user_agent": "YourBot/1.0",
  "operator": "Your Company Name",
  "purpose": "Brief description of what your bot does (1-2 sentences)",
  "description": "Additional context if needed",
  "impact_of_blocking": "What happens if someone blocks your bot (1-2 sentences)",
  "website": "https://yourcompany.com/bot-documentation",
  "categories": {
    "ecommerce": "beneficial",
    "news": "neutral",
    "media": "beneficial",
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

## Template (Multiple Bots)

If you need to add multiple bots in one file:

```json
[
  {
    "user_agent": "FirstBot/1.0",
    "operator": "Your Company",
    "purpose": "...",
    "impact_of_blocking": "...",
    "website": "...",
    "categories": {},
    "sources": ["manual"],
    "raw_data": {}
  },
  {
    "user_agent": "SecondBot/2.0",
    "operator": "Your Company",
    "purpose": "...",
    "impact_of_blocking": "...",
    "website": "...",
    "categories": {},
    "sources": ["manual"],
    "raw_data": {}
  }
]
```

## Required Fields

- `user_agent` - Your bot's user agent string
- `operator` - Company or organization name
- `sources` - Must include `"manual"`

## Recommended Fields

- `purpose` - What your bot does
- `impact_of_blocking` - Consequences of blocking
- `website` - Link to bot documentation
- `categories` - Recommendations by site type
- `raw_data.ip_ranges` - IP ranges your bot uses
- `raw_data.asn` - Your Autonomous System Number
- `raw_data.verification_method` - How to verify your bot

## Category Ratings

Rate your bot for each site type:

- `beneficial` - Website owners should generally allow
- `neutral` - Depends on the use case
- `harmful` - Website owners should generally block
- `not_applicable` - Bot doesn't interact with this site type

### Site Categories

- `ecommerce` - Online stores
- `news` - News sites
- `media` - Video/audio streaming
- `blog` - Personal/professional blogs
- `saas` - Software-as-a-Service
- `corporate` - Company websites
- `documentation` - Technical docs
- `social` - Social networks
- `portfolio` - Personal portfolios
- `government` - Government sites

## Category Guidelines

### Beneficial
Your bot provides clear value to this site type:
- Search engine crawlers for most sites
- Monitoring services for sites that use them
- Legitimate research bots with permission

### Neutral
Impact depends on the specific use case:
- Archive bots (some sites want archiving, others don't)
- Academic research crawlers
- SEO analysis tools

### Harmful
Your bot may negatively impact this site type:
- Unauthorized content scrapers
- Bots that republish content without permission
- Aggressive crawlers that cause server load

### Not Applicable
Your bot doesn't interact with this site type:
- Mobile app crawlers on web-only sites
- Industry-specific bots on unrelated sites
- Platform-specific bots (e.g., social media bots on e-commerce sites)

## Technical Details

### IP Ranges
List all IP ranges your bot uses in CIDR notation:
```json
"ip_ranges": ["192.0.2.0/24", "198.51.100.0/24", "2001:db8::/32"]
```

### ASN (Autonomous System Number)
Provide your ASN if available:
```json
"asn": "AS64496"
```

Or multiple ASNs:
```json
"asn_list": ["AS64496", "AS64497"]
```

### Verification Method
Explain how website owners can verify your bot is legitimate:
- `"DNS reverse lookup"` - IP resolves to your domain
- `"User-agent + IP verification"` - Check both user agent and IP range
- `"Request header validation"` - Specific headers in requests
- `"Published IP ranges"` - IPs listed on your website
- `"API verification endpoint"` - Provide an API to check bot authenticity

## Validation

Your submission will be validated for:

- ✅ Valid JSON syntax
- ✅ Required fields present
- ✅ Category ratings are valid (`beneficial`, `neutral`, `harmful`, `not_applicable`)
- ✅ No duplicate user agents
- ✅ Sources includes `"manual"`

## Benefits of Individual Files

- **No merge conflicts** - Each contributor edits their own file
- **Easier reviews** - Changes are isolated
- **Better git history** - Clear attribution per bot
- **Simpler contributions** - Just add your file
- **Parallel development** - Multiple PRs can be open simultaneously

## Examples

### Good Examples

✅ `sources/mycompanybot.json` - Single bot, well documented  
✅ `sources/monitoring_bots.json` - Multiple related bots from same company  
✅ `sources/seo_crawler.json` - Comprehensive technical details

### What to Avoid

❌ Don't edit other people's bot files  
❌ Don't create duplicate entries for existing bots  
❌ Don't use generic or misleading user agent strings  
❌ Don't provide false or incomplete information

## Review Process

1. **Automated validation** - GitHub Actions checks your JSON
2. **Maintainer review** - We verify information accuracy
3. **Community feedback** - Other contributors may comment
4. **Merge** - Once approved, your bot is added to the database

## Questions?

- Check `example_bot.json` for a complete working example
- See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines
- Open an issue if you need help
- Review existing bot files for inspiration

## Quick Start

```bash
# 1. Copy the example
cp sources/example_bot.json sources/mybot.json

# 2. Edit with your bot's information
nano sources/mybot.json

# 3. Validate locally (optional)
python scripts/validate_data.py

# 4. Submit
git add sources/mybot.json
git commit -m "Add MyBot to database"
git push origin add-mybot
```

## Thank You!

Thanks for contributing to the Central Bot Database! Your submission helps website owners make informed decisions about which bots to allow or block.
