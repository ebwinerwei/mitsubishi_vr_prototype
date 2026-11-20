#!/bin/bash
cd "$(dirname "$0")/.."
python3 tools/build_203_dzi.py
echo ""
echo "処理が完了しました。このウィンドウを閉じてください。"
read -n 1
