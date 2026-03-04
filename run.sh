#!/bin/bash
# FRAX® Tool — Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🦴 FRAX® Tool — ระบบคัดกรองความเสี่ยง"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 เปิดเบราว์เซอร์ที่: http://localhost:8000"
echo ""

python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
