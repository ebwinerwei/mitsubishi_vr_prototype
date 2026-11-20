#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手動 Deep Zoom (DZI) 切片生成コマンドラインツール (tools/make_single_dzi.py)
使い方：
  python3 tools/make_single_dzi.py <入力画像パス（JPG/PNG/TIFF）> <出力先フォルダパス>
例：
  python3 tools/make_single_dzi.py ./my_photo.tif ./assets/documents/doc_005/page_1
"""
import sys
import os
from build_203_dzi import slice_image_to_dzi

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: python3 tools/make_single_dzi.py <入力画像ファイル> <出力先フォルダ>")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2]
    w, h, dzi_path, _ = slice_image_to_dzi(src, out, dzi_name="doc", tile_size=256)
    print(f"✅ DZIタイル生成完了! 元サイズ: {w}×{h}px -> 出力DZI: {dzi_path}")
