#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
三菱史料館 ウェブ展示室 納品用バッチ構築ツール (tools/build_203_dzi.py)
=============================================================================
【機能概要】
CMSバックエンドを開発しない初期納品フェーズにおいて、全203点の史料データ（複数画像・異サイズ混在）を
一括処理して納品可能な静的パッケージを生成するオフライン自動構築スクリプトです。

1. `raw_input/<史料ID>/` フォルダ内のすべての画像（1枚でも複数枚でも、縦長・横長・解像度不統一でもすべて対応）を自動スキャン
2. 各画像の縦横比・解像度を自動判別し、OpenSeadragon 用の Deep Zoom Image (`.dzi` + `_files/` 256×256px 階層タイル) を自動生成
3. `raw_input/catalog_203_template.csv` の日英テキスト・翻刻文と結合し、`data/exhibition_data.json` を自動出力
4. Krpano 用の全203個（または登録件数分）のホットスポット定義ファイル `vtour/hotspots_203.xml` を自動生成
   （パノラマ空間内でホットスポットをマウスドラッグして座標 `ath` / `atv` を調整できるデバッグモード付き！）

【実行方法（Mac / Windows 共通）】
  pip install Pillow
  python3 tools/build_203_dzi.py
=============================================================================
"""

import os
import csv
import json
import math
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_INPUT_DIR = os.path.join(ROOT_DIR, "raw_input")
ASSETS_DOCS_DIR = os.path.join(ROOT_DIR, "assets", "documents")
DATA_JSON_PATH = os.path.join(ROOT_DIR, "data", "exhibition_data.json")
VTOUR_HOTSPOTS_XML = os.path.join(ROOT_DIR, "vtour", "hotspots_203.xml")

SUPPORTED_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp")

def slice_image_to_dzi(img_path, out_dir, dzi_name="page", tile_size=256):
    """
    任意のサイズ・縦横比の画像を読み込み、OpenSeadragon 標準の DZI (Deep Zoom Image)
    ピラミッドタイル群 (256x256px) と .dzi XML ファイルを生成します。
    """
    os.makedirs(out_dir, exist_ok=True)
    img = Image.open(img_path)
    if img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    max_dim = max(w, h)
    max_level = int(math.ceil(math.log(max_dim, 2))) if max_dim > 1 else 0

    files_dir = os.path.join(out_dir, f"{dzi_name}_files")
    os.makedirs(files_dir, exist_ok=True)

    for level in range(max_level, -1, -1):
        scale = 2 ** (max_level - level)
        lw = max(1, int(math.ceil(w / scale)))
        lh = max(1, int(math.ceil(h / scale)))
        level_img = img.resize((lw, lh), Image.Resampling.LANCZOS)

        level_dir = os.path.join(files_dir, str(level))
        os.makedirs(level_dir, exist_ok=True)

        cols = int(math.ceil(lw / tile_size))
        rows = int(math.ceil(lh / tile_size))
        for col in range(cols):
            for row in range(rows):
                x1 = col * tile_size
                y1 = row * tile_size
                x2 = min(lw, (col + 1) * tile_size)
                y2 = min(lh, (row + 1) * tile_size)
                tile = level_img.crop((x1, y1, x2, y2))
                tile.save(os.path.join(level_dir, f"{col}_{row}.jpg"), "JPEG", quality=90)

    # Save thumbnail for multi-image bottom strip
    thumb = img.copy()
    thumb.thumbnail((320, 240), Image.Resampling.LANCZOS)
    thumb_path = os.path.join(out_dir, f"{dzi_name}_thumb.jpg")
    thumb.save(thumb_path, "JPEG", quality=85)

    dzi_xml_path = os.path.join(out_dir, f"{dzi_name}.dzi")
    dzi_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<Image TileSize="{tile_size}" Overlap="0" Format="jpg" xmlns="http://schemas.microsoft.com/deepzoom/2008">\n'
        f'    <Size Width="{w}" Height="{h}"/>\n'
        '</Image>'
    )
    with open(dzi_xml_path, "w", encoding="utf-8") as f:
        f.write(dzi_xml)

    return w, h, dzi_xml_path, thumb_path

def main():
    print("=================================================================")
    print(" 三菱史料館 203点史料 Deep Zoom 自動切片 ＆ Krpano XML ビルド開始")
    print("=================================================================")

    csv_path = os.path.join(RAW_INPUT_DIR, "catalog_203_template.csv")
    if not os.path.exists(csv_path):
        print(f"[エラー] {csv_path} が見つかりません。")
        return

    documents_out = []
    krpano_hotspots_xml_lines = [
        "<krpano>",
        "    <!-- 自動生成された 203点史料用 Krpano ホットスポット定義ファイル (vtour/hotspots_203.xml) -->",
        "    <!-- ドラッグ調整モード：ホットスポットをShift+ドラッグするとコンソールに新しい ath/atv 座標を表示します -->",
        "    <action name=\"meri_drag_hotspot\">",
        "        spheretoscreen(ath, atv, hotspotcenterx, hotspotcentery);",
        "        sub(drag_adjustx, mouse.stagex, hotspotcenterx);",
        "        sub(drag_adjusty, mouse.stagey, hotspotcentery);",
        "        asyncloop(pressed,",
        "            sub(dx, mouse.stagex, drag_adjustx);",
        "            sub(dy, mouse.stagey, drag_adjusty);",
        "            screentosphere(dx, dy, ath, atv);",
        "            roundval(ath, 2); roundval(atv, 2);",
        "            trace('Hotspot [', name, '] moved to ath=\"', ath, '\" atv=\"', atv, '\"');",
        "        );",
        "    </action>",
        ""
    ]

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            doc_id = row["doc_id"].strip()
            doc_raw_folder = os.path.join(RAW_INPUT_DIR, doc_id)
            doc_out_folder = os.path.join(ASSETS_DOCS_DIR, doc_id)

            images_list = []
            if os.path.exists(doc_raw_folder):
                img_files = sorted([
                    fn for fn in os.listdir(doc_raw_folder)
                    if fn.lower().endswith(SUPPORTED_EXTS)
                ])
                for page_num, fn in enumerate(img_files, start=1):
                    src_img = os.path.join(doc_raw_folder, fn)
                    page_subfolder = os.path.join(doc_out_folder, f"page_{page_num}")
                    w, h, dzi_file, thumb_file = slice_image_to_dzi(src_img, page_subfolder, dzi_name="doc")
                    rel_dzi = os.path.relpath(dzi_file, ROOT_DIR).replace("\\", "/")
                    rel_thumb = os.path.relpath(thumb_file, ROOT_DIR).replace("\\", "/")
                    print(f"  ✔ [{doc_id}] 第{page_num}頁 ({fn}: {w}x{h}px) -> {rel_dzi}")
                    images_list.append({
                        "page": page_num,
                        "caption_ja": f"第{page_num}頁：{fn} ({w}×{h}px)",
                        "caption_en": f"Page {page_num}: {fn} ({w}×{h}px)",
                        "width": w,
                        "height": h,
                        "dzi_path": rel_dzi,
                        "image_uri": rel_thumb
                    })

            documents_out.append({
                "id": doc_id,
                "code": f"史料番号：{doc_id}",
                "showcase_id": row.get("showcase_id", "SHOWCASE-B"),
                "scene_name": row.get("scene_name", "scene_room1"),
                "ath": float(row.get("ath", 0.0) or 0.0),
                "atv": float(row.get("atv", 0.0) or 0.0),
                "status": "原史料デジタルデータ（Deep Zoom タイル配信）",
                "era_ja": row.get("era_ja", ""),
                "era_en": row.get("era_en", ""),
                "title_ja": row.get("title_ja", ""),
                "title_en": row.get("title_en", ""),
                "calligraphy_note_ja": row.get("calligraphy_note_ja", ""),
                "calligraphy_note_en": row.get("calligraphy_note_en", ""),
                "transcription_ja": row.get("transcription_ja", ""),
                "explanation_ja": row.get("explanation_ja", ""),
                "explanation_en": row.get("explanation_en", ""),
                "images": images_list
            })

            # Generate Krpano Hotspot XML entry
            ath = row.get("ath", "0.0")
            atv = row.get("atv", "0.0")
            safe_title = row.get("title_ja", doc_id).replace("'", "")
            hs_name = f"hs_doc_{idx:03d}_{doc_id.lower().replace('-', '_')}"
            krpano_hotspots_xml_lines.append(
                f"    <!-- [{idx}/203] {doc_id}: {safe_title} (画像枚数: {len(images_list)}枚) -->\n"
                f"    <hotspot name=\"{hs_name}\" style=\"skin_hotspotstyle\" ath=\"{ath}\" atv=\"{atv}\" keep=\"false\"\n"
                f"             ondown=\"if(keydown(16), meri_drag_hotspot());\"\n"
                f"             onclick=\"js(window.ArchiveBridge.openDocumentModal('{doc_id}'));\" />\n"
            )

    krpano_hotspots_xml_lines.append("</krpano>\n")
    os.makedirs(os.path.dirname(VTOUR_HOTSPOTS_XML), exist_ok=True)
    with open(VTOUR_HOTSPOTS_XML, "w", encoding="utf-8") as f:
        f.write("\n".join(krpano_hotspots_xml_lines))

    print("-----------------------------------------------------------------")
    print(f"✅ Krpano ホットスポットXML出力完了: {VTOUR_HOTSPOTS_XML}")
    print("   （vtour/tour.xml 内で <include url=\"hotspots_203.xml\" /> と記述するだけで読み込めます）")
    print("=================================================================")

if __name__ == "__main__":
    main()
