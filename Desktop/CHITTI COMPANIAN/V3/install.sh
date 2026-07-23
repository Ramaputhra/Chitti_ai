#!/bin/bash
# ============================================================
# CHITTI AI Desktop Companion - Installation Script
# ============================================================

set -e  # Exit on error

echo "============================================================"
echo "🧠 CHITTI AI Desktop Companion - Installation"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "   Found Python $PYTHON_VERSION"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment created and activated${NC}"
fi

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install core requirements first
echo ""
echo "📦 Installing core requirements..."
pip install -r requirements.txt

# Install optional extras based on features
echo ""
echo "📦 Installing optional features..."

# Team Communication
if [ "$1" == "--all" ] || [ "$1" == "--communication" ]; then
    echo "   Installing Slack SDK..."
    pip install slack-sdk
    
    echo "   Installing Discord.py..."
    pip install discord.py
    
    echo "   Installing Telegram Bot..."
    pip install python-telegram-bot
fi

# Smart Home
if [ "$1" == "--all" ] || [ "$1" == "--smarthome" ]; then
    echo "   Installing Smart Home dependencies..."
    pip install phue homeassistant-api
fi

# Task Management
if [ "$1" == "--all" ] || [ "$1" == "--tasks" ]; then
    echo "   Installing Task Management..."
    pip install notion-client todoist-api-python
fi

# Developer Tools
if [ "$1" == "--all" ] || [ "$1" == "--developer" ]; then
    echo "   Installing Developer Tools..."
    pip install PyGithub GitPython
fi

# Media Control
if [ "$1" == "--all" ] || [ "$1" == "--media" ]; then
    echo "   Installing Media Control..."
    pip install spotipy pafy
fi

# Document Processing
if [ "$1" == "--all" ] || [ "$1" == "--documents" ]; then
    echo "   Installing Document Processing..."
    pip install pypdf2 python-docx easyocr pytesseract
fi

# Download AI Models
echo ""
echo "📥 Downloading AI models (this may take a while)..."
echo "   Note: You can skip this and models will be downloaded on first use"

if [ "$1" == "--all" ] || [ "$1" == "--models" ]; then
    echo "   Download faster-whisper model (base)..."
    python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('base', download_root='./models')" 2>/dev/null || echo "   Skipped (will download on first use)"
    
    echo "   Download Piper TTS voice..."
    mkdir -p models/tts
    # Voice will be downloaded automatically
fi

# Final check
echo ""
echo "📋 Running installation check..."
python3 -c "
import sys
sys.path.insert(0, '.')
from desktop.capabilities.health import HealthCapability
from desktop.capabilities.analytics_cap import PersonalAnalyticsCapability
from desktop.capabilities.meeting_intelligence import MeetingIntelligenceCapability
print('   ✅ All new capabilities importable')
" 2>/dev/null || echo "   ⚠️ Some optional modules not available (this is OK)"

echo ""
echo "============================================================"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "============================================================"
echo ""
echo "📚 Next steps:"
echo "   1. Configure settings in config/settings.json"
echo "   2. Download AI models (first run will prompt)"
echo "   3. Run: PYTHONPATH=. python main.py"
echo ""
echo "📖 Documentation:"
echo "   - README.md - Overview"
echo "   - docs/FEATURE_ROADMAP.md - Features"
echo "   - desktop/plugins/sdk/README.md - Plugin SDK"
echo ""
echo "💡 Installation flags:"
echo "   --all            Install all optional features"
echo "   --communication  Install Slack, Discord, Telegram"
echo "   --smarthome      Install Smart Home integrations"
echo "   --tasks          Install Notion, Todoist"
echo "   --developer      Install GitHub, Git tools"
echo "   --media          Install Spotify, YouTube"
echo "   --documents      Install OCR, PDF tools"
echo "   --models         Download AI models"
echo ""
