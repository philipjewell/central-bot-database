#!/bin/bash

# Bot Database Pipeline Runner
# Runs all scripts in sequence to generate the bot database

set -e  # Exit on error

echo "🤖 Bot Database Pipeline Starting..."
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama is not running!"
    echo "   Please start Ollama and ensure llama3.2 model is installed:"
    echo "   ollama serve"
    echo "   ollama pull llama3.2"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p staging data docs sources schemas

# Ensure manual_bots.json exists
if [ ! -f "sources/manual_bots.json" ]; then
    echo "📝 Creating manual_bots.json template..."
    cp "sources/manual_bots.json.template" "sources/manual_bots.json" 2>/dev/null || echo "[]" > sources/manual_bots.json
fi

echo ""
echo "1️⃣  Fetching from ai.robots.txt..."
python scripts/fetch_ai_robots.py || echo "⚠️  ai.robots.txt fetch failed (continuing...)"

echo ""
echo "2️⃣  Fetching from Cloudflare Radar..."
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "ℹ️  CLOUDFLARE_API_TOKEN not set, skipping Cloudflare fetch"
else
    python scripts/fetch_cloudflare_radar.py || echo "⚠️  Cloudflare fetch failed (continuing...)"
fi

echo ""
echo "3️⃣  Merging and deduplicating sources..."
python scripts/merge_sources.py

echo ""
echo "4️⃣  Enriching with AI descriptions..."
python scripts/enrich_with_ai.py

echo ""
echo "5️⃣  Generating output files..."
python scripts/generate_outputs.py

echo ""
echo "✅ Pipeline complete!"
echo ""
echo "📊 Output files:"
echo "   - data/bots.json (machine-readable)"
echo "   - docs/BOTS.md (human-readable)"
echo ""
echo "🔍 Review the changes with:"
echo "   git diff data/bots.json"
echo "   git diff docs/BOTS.md"
