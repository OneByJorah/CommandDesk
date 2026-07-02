#!/bin/bash
# ═══════════════════════════════════════════════════
# Helpdesk Agent - Setup Script
# One-time initialization
# ═══════════════════════════════════════════════════

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

# Error handler
handle_error() {
    error "Setup failed at line $1"
    error "Command: $2"
    exit 1
}

trap 'handle_error $LINENO "$BASH_COMMAND"' ERR

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

One-time setup for CommandDesk helpdesk agent.

Options:
  -h, --help          Show this help message
  --skip-model        Skip model download
  --skip-certs        Skip certificate generation
  --force             Overwrite existing files without prompting
  --model MODEL       Specify model to download (default: qwen2.5-7b-instruct-q4_k_m.gguf)

Examples:
  $0                  # Full setup
  $0 --skip-model     # Setup without downloading LLM model
  $0 --force          # Force overwrite of existing files
EOF
    exit 0
}

# Parse arguments
SKIP_MODEL=false
SKIP_CERTS=false
FORCE=false
MODEL_FILE="qwen2.5-7b-instruct-q4_k_m.gguf"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help) usage ;;
        --skip-model) SKIP_MODEL=true; shift ;;
        --skip-certs) SKIP_CERTS=true; shift ;;
        --force) FORCE=true; shift ;;
        --model) MODEL_FILE="$2"; shift 2 ;;
        *) error "Unknown option: $1"; usage ;;
    esac
done

echo ""
echo "═══════════════════════════════════════════"
echo "  J1 Helpdesk Agent - Setup"
echo "═══════════════════════════════════════════"
echo ""

# ═══════════════════════════════════════════════════
# Prerequisites Check
# ═══════════════════════════════════════════════════

info "Checking prerequisites..."

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        success "$1 found: $(command -v "$1")"
        return 0
    else
        error "$1 not found"
        return 1
    fi
}

PREREQ_FAILED=false

check_command docker || PREREQ_FAILED=true
check_command "docker compose" || check_command docker-compose || PREREQ_FAILED=true

# Check Docker daemon is running
if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        success "Docker daemon is running"
    else
        warn "Docker daemon is not running. Start it with: sudo systemctl start docker"
    fi
fi

if [ "$PREREQ_FAILED" = true ]; then
    echo ""
    error "Missing required dependencies. Please install:"
    echo "  - Docker Engine: https://docs.docker.com/engine/install/"
    echo "  - Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# ═══════════════════════════════════════════════════
# Directory Setup
# ═══════════════════════════════════════════════════

info "Creating directories..."
mkdir -p models config scripts knowledge-base workflows certs data/logs queue
success "Directories created"

# ═══════════════════════════════════════════════════
# Environment File
# ═══════════════════════════════════════════════════

info "Setting up environment configuration..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        success ".env created from template"
        warn "→ Edit .env with your credentials before starting!"
    else
        error ".env.example not found. Cannot create .env"
        exit 1
    fi
elif [ "$FORCE" = true ]; then
    cp .env.example .env
    success ".env overwritten from template (--force)"
    warn "→ Edit .env with your credentials before starting!"
else
    success ".env already exists (use --force to overwrite)"
fi

# ═══════════════════════════════════════════════════
# SSL Certificates
# ═══════════════════════════════════════════════════

if [ "$SKIP_CERTS" = false ]; then
    info "Setting up SSL certificates..."
    if [ ! -f certs/cert.pem ] || [ "$FORCE" = true ]; then
        if command -v openssl >/dev/null 2>&1; then
            openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem \
                -out certs/cert.pem -days 365 -nodes \
                -subj "/CN=helpdesk.local" 2>/dev/null
            success "Self-signed certificate generated"
            warn "→ Replace with real certificates for production use"
        else
            warn "openssl not found. Skipping certificate generation."
            warn "→ Install openssl or manually create certificates"
        fi
    else
        success "Certificates already exist (use --force to regenerate)"
    fi
else
    info "Skipping certificate generation (--skip-certs)"
fi

# ═══════════════════════════════════════════════════
# LLM Model Download
# ═══════════════════════════════════════════════════

if [ "$SKIP_MODEL" = false ]; then
    info "Setting up LLM model..."
    MODEL_PATH="models/$MODEL_FILE"

    if [ ! -f "$MODEL_PATH" ] || [ "$FORCE" = true ]; then
        if [ "$FORCE" = true ] && [ -f "$MODEL_PATH" ]; then
            warn "Removing existing model (--force)..."
            rm -f "$MODEL_PATH"
        fi

        echo ""
        info "Downloading $MODEL_FILE..."
        info "This may take 10-20 minutes depending on your connection."
        echo ""

        if command -v huggingface-cli >/dev/null 2>&1; then
            info "Using huggingface-cli..."
            huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF \
                "$MODEL_FILE" --local-dir models/
        elif command -v wget >/dev/null 2>&1; then
            info "Using wget..."
            MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/$MODEL_FILE"
            wget -q --show-progress "$MODEL_URL" -O "$MODEL_PATH"
        elif command -v curl >/dev/null 2>&1; then
            info "Using curl..."
            MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/$MODEL_FILE"
            curl -L --progress-bar "$MODEL_URL" -o "$MODEL_PATH"
        else
            warn "No download tool found (huggingface-cli, wget, or curl)"
            warn "→ Download manually from: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF"
            warn "→ Place the file at: $MODEL_PATH"
        fi

        if [ -f "$MODEL_PATH" ]; then
            MODEL_SIZE=$(du -h "$MODEL_PATH" | cut -f1)
            success "Model downloaded: $MODEL_PATH ($MODEL_SIZE)"
        fi
    else
        MODEL_SIZE=$(du -h "$MODEL_PATH" | cut -f1)
        success "Model already exists: $MODEL_PATH ($MODEL_SIZE)"
    fi
else
    info "Skipping model download (--skip-model)"
fi

# ═══════════════════════════════════════════════════
# Knowledge Base
# ═══════════════════════════════════════════════════

info "Setting up knowledge base..."
if [ -d knowledge-base ] && [ "$(ls -A knowledge-base/*.md knowledge-base/*.txt 2>/dev/null)" ]; then
    success "Knowledge base files found"
else
    info "Adding sample knowledge base article..."
    cat > knowledge-base/welcome.md << 'EOF'
# Welcome to J1 Helpdesk

## How to get help

1. **Email**: Send your question to helpdesk@example.com
2. **Web portal**: Visit https://support.example.com
3. **Chat**: Use this AI assistant to search your existing tickets

## Common Issues

### Password Reset
Go to https://support.example.com/reset and enter your email address. You'll receive a reset link within 5 minutes.

### Billing Questions
Contact billing@example.com or call +1-555-0123. Have your account number ready (format: ACC-XXXXXX).

### Service Status
Check current service status at https://status.example.com.
EOF
    success "Sample knowledge base article added"
fi

# ═══════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════"
echo "  Setup Complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your credentials"
echo "     ${YELLOW}nano .env${NC}"
echo ""
echo "  2. Start all services:"
echo "     ${GREEN}docker compose up -d${NC}"
echo ""
echo "  3. Open the dashboard:"
echo "     ${BLUE}http://localhost/dashboard/${NC}"
echo ""
echo "  4. Check service health:"
echo "     ${GREEN}make health${NC}"
echo ""
echo "For osTicket/Freshdesk integration:"
echo "  - Set OSTICKET_URL and OSTICKET_API_KEY in .env"
echo "  - Set FRESHDESK_URL and FRESHDESK_API_KEY in .env"
echo ""
echo "To add knowledge base articles:"
echo "  - Place .md or .txt files in knowledge-base/"
echo "  - Run: ${GREEN}docker compose exec helpdesk-agent python3 scripts/index_kb.py${NC}"
echo ""
