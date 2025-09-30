#!/bin/bash

# Bot Database Setup Script
# Prepares the repository for first run

set -e

echo "🤖 Bot Database Setup"
echo "===================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.11 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check Ollama
echo "Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✓ Ollama is running"
        
        # Check if llama3.2 model exists
        if ollama list | grep -q "llama3.2"; then
            echo "✓ llama3.2 model is installed"
        else
            echo "⚠️  llama3.2 model not found"
            read -p "Do you want to download it now? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ollama pull llama3.2
                echo "✓ llama3.2 model downloaded"
            else
                echo "ℹ️  You can download it later with: ollama pull llama3.2"
            fi
        fi
    else
        echo "⚠️  Ollama is not running"
        echo "   Start it with: ollama serve"
    fi
else
    echo "❌ Ollama is not installed"
    echo "   Install from: https://ollama.ai"
    echo "   After installing, run: ollama pull llama3.2"
fi
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p staging data docs sources schemas scripts .github/workflows
echo "✓ Directories created"
echo ""

# Create manual_bots.json if it doesn't exist
if [ ! -f "sources/manual_bots.json" ]; then
    echo "Creating manual_bots.json template..."
    cat > sources/manual_bots.json << 'EOF'
[
  {
    "user_agent": "ExampleBot/1.0",
    "operator": "Example Company",
    "purpose": "Example bot for demonstration purposes. Replace with your actual bot.",
    "description": "This is a template entry.",
    "impact_of_blocking": "No impact - this is just an example.",
    "website": "https://example.com",
    "categories": {
      "ecommerce": "neutral",
      "news": "neutral",
      "media": "neutral",
      "blog": "neutral",
      "saas": "neutral",
      "corporate": "neutral",
      "documentation": "neutral",
      "social": "neutral",
      "portfolio": "neutral",
      "government": "neutral"
    },
    "sources": ["manual"],
    "raw_data": {
      "ip_ranges": [],
      "asn": "",
      "verification_method": ""
    }
  }
]
EOF
    echo "✓ Created sources/manual_bots.json"
else
    echo "ℹ️  sources/manual_bots.json already exists"
fi
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_pipeline.sh
chmod +x setup.sh
echo "✓ Scripts are executable"
echo ""

# Check for Cloudflare API token
echo "Checking for Cloudflare API token..."
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "⚠️  CLOUDFLARE_API_TOKEN environment variable not set"
    echo "   This is optional but recommended for Cloudflare Radar data"
    echo "   Get a token from: https://dash.cloudflare.com"
    echo "   Set it with: export CLOUDFLARE_API_TOKEN='your-token'"
else
    echo "✓ CLOUDFLARE_API_TOKEN is set"
fi
echo ""

# Summary
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit sources/manual_bots.json to add your bots"
echo "  2. Run the pipeline: ./run_pipeline.sh"
echo "  3. Review outputs:"
echo "     - data/bots.json (machine-readable)"
echo "     - docs/BOTS.md (human-readable)"
echo ""
echo "For automated GitHub Actions:"
echo "  1. Add CLOUDFLARE_API_TOKEN to repository secrets"
echo "  2. Workflows will run weekly on Sundays"
echo "  3. Review and merge the automated PRs"
echo ""
echo "Need help? Check README.md or CONTRIBUTING.md"
