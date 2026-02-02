# nginx Bot Category Mapping

This directory contains an auto-generated nginx map configuration that maps bot user agents to their operator categories for easy identification and rate limiting.

## Files

- `bot_category_map.conf` - Auto-generated nginx map file (updated weekly via GitHub Actions)

## What It Does

The map file creates an nginx variable `$bot_category` that identifies which category a bot belongs to based on its user agent string. This allows you to:

- Rate limit specific bot categories
- Block entire categories of bots
- Allow-list beneficial bots
- Apply different policies to different bot types

## Basic Usage

### 1. Include the Map File

Add this to your nginx `http` block:

```nginx
http {
    # Include the bot category mapping
    include /path/to/bot_category_map.conf;

    # Your other http configuration...
}
```

### 2. Use the `$bot_category` Variable

The `$bot_category` variable will now contain the operator category for each request, or `"unknown"` if the user agent doesn't match any known bot.

## Rate Limiting Examples

### Example 1: Rate Limit AI Crawlers

Block or heavily rate limit AI training crawlers:

```nginx
http {
    # Include bot category mapping
    include /path/to/bot_category_map.conf;

    # Define rate limit zone for AI crawlers
    limit_req_zone $binary_remote_addr zone=ai_crawlers:10m rate=1r/m;

    server {
        listen 80;
        server_name example.com;

        location / {
            # Apply rate limit only to AI Crawler category
            if ($bot_category = "AI Crawler") {
                set $limit_ai 1;
            }

            if ($limit_ai) {
                limit_req zone=ai_crawlers burst=5 nodelay;
            }

            # Your normal location configuration
            try_files $uri $uri/ =404;
        }
    }
}
```

### Example 2: Block Specific Categories Completely

Block harmful bots entirely:

```nginx
server {
    listen 80;
    server_name example.com;

    # Block specific bot categories
    if ($bot_category = "AI Crawler") {
        return 403 "AI crawlers not permitted";
    }

    if ($bot_category = "AI Assistant") {
        return 403 "AI assistants not permitted";
    }

    location / {
        # Your normal configuration
        try_files $uri $uri/ =404;
    }
}
```

### Example 3: Different Rate Limits for Different Categories

Apply tiered rate limiting based on bot type:

```nginx
http {
    include /path/to/bot_category_map.conf;

    # Define multiple rate limit zones
    limit_req_zone $binary_remote_addr zone=ai_crawlers:10m rate=1r/m;
    limit_req_zone $binary_remote_addr zone=seo_tools:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=monitoring:10m rate=60r/m;

    server {
        listen 80;
        server_name example.com;

        location / {
            # AI Crawlers - very strict
            if ($bot_category = "AI Crawler") {
                set $rate_limit ai_crawlers;
            }

            # SEO tools - moderate
            if ($bot_category = "Search Engine Optimization") {
                set $rate_limit seo_tools;
            }

            # Monitoring services - lenient
            if ($bot_category = "Monitoring & Analytics") {
                set $rate_limit monitoring;
            }

            # Apply the appropriate rate limit
            limit_req zone=$rate_limit burst=5 nodelay;

            try_files $uri $uri/ =404;
        }
    }
}
```

### Example 4: Allow-List Good Bots, Rate Limit Unknown

Only rate limit user agents that aren't recognized as beneficial bots:

```nginx
http {
    include /path/to/bot_category_map.conf;

    limit_req_zone $binary_remote_addr zone=unknown_bots:10m rate=10r/m;

    # Map to determine if bot should be rate limited
    map $bot_category $limit_unknown {
        default 1;  # Rate limit by default
        "Search Engine Crawler" 0;  # Allow search engines
        "Monitoring & Analytics" 0;  # Allow monitoring
        "Security" 0;  # Allow security scanners
        "Page Preview" 0;  # Allow social media previews
    }

    server {
        listen 80;
        server_name example.com;

        location / {
            if ($limit_unknown) {
                limit_req zone=unknown_bots burst=20;
            }

            try_files $uri $uri/ =404;
        }
    }
}
```

### Example 5: robots.txt Integration

Serve different robots.txt based on bot category:

```nginx
server {
    listen 80;
    server_name example.com;

    location = /robots.txt {
        # AI crawlers get restrictive robots.txt
        if ($bot_category = "AI Crawler") {
            rewrite ^ /robots-ai-blocked.txt last;
        }

        # Search engines get normal robots.txt
        if ($bot_category = "Search Engine Crawler") {
            rewrite ^ /robots-search.txt last;
        }

        # Default robots.txt for everyone else
        try_files /robots-default.txt =404;
    }
}
```

## Available Bot Categories

The map file includes the following categories:

**AI & Machine Learning:**
- AI Assistant
- AI Crawler
- AI Search

**Content & Aggregation:**
- Search Engine Crawler
- Feed Fetcher
- Aggregator
- Page Preview
- Archiver

**Marketing & Analytics:**
- Advertising & Marketing
- Monitoring & Analytics
- Search Engine Optimization

**Utilities:**
- Security
- Accessibility
- Webhooks

**Company-Specific:**
- Anthropic
- ByteDance
- DeepSeek
- And many more...

See the full list in `bot_category_map.conf` or browse the [web interface](https://central-bot-database.pages.dev).

## Logging Bot Categories

Add logging to track which bots are accessing your site:

```nginx
log_format bot_tracking '$remote_addr - $remote_user [$time_local] '
                        '"$request" $status $body_bytes_sent '
                        '"$http_user_agent" Category: "$bot_category"';

access_log /var/log/nginx/bot_access.log bot_tracking;
```

## Testing

Test which category a user agent matches:

```bash
# Test an AI crawler
curl -A "GPTBot" http://example.com/

# Test a search engine
curl -A "Googlebot" http://example.com/

# Test unknown bot
curl -A "MyCustomBot/1.0" http://example.com/
```

## Maintenance

The `bot_category_map.conf` file is automatically generated and updated weekly via GitHub Actions. To regenerate it manually:

```bash
# From the repository root
source venv/bin/activate
python scripts/generate_nginx_map.py
```

This will regenerate the map file from the latest `data/bots.json` database.

## Performance Considerations

- The map uses regex matching (`~*` for case-insensitive), which is efficient in nginx
- User agent patterns are escaped to prevent regex errors
- Map lookups happen once per request and are cached
- Minimal performance impact even with hundreds of bot patterns

## Best Practices

1. **Test before deploying** - Use a staging environment to verify rate limits work as expected
2. **Monitor your logs** - Track which bots are being rate limited
3. **Be conservative** - Start with lenient limits and tighten as needed
4. **Allow beneficial bots** - Don't block search engines or monitoring services you use
5. **Update regularly** - Pull the latest bot_category_map.conf file weekly

## Contributing

If you find a bot that should be categorized differently or want to add a new bot:

1. Visit the [central-bot-database repository](https://github.com/philipjewell/central-bot-database)
2. Add your bot to `sources/` directory
3. Submit a pull request

The nginx map file will be automatically updated when your bot is merged.

## Resources

- [Central Bot Database](https://github.com/philipjewell/central-bot-database)
- [Web Interface](https://central-bot-database.pages.dev)
- [nginx map directive documentation](http://nginx.org/en/docs/http/ngx_http_map_module.html)
- [nginx rate limiting guide](http://nginx.org/en/docs/http/ngx_http_limit_req_module.html)
