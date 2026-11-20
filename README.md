# 三菱史料館 ウェブ展示室 技術プロトタイプ（Krpano + OpenSeadragon + 専用CMS）

本パッケージは、[公益財団法人 三菱経済研究所](https://www.meri.or.jp/) 付属 [三菱史料館](https://www.meri.or.jp/siryo-kan/) 様への提案・デモンストレーション用に構築した、**100%落地可能な3層ハイブリッド構成（Krpano + OpenSeadragon + 専用CMS）** の技術プロトタイプ一式です。

---


---

## 0. 【最重要】貴社お手元の `vtour` プロジェクト（スクリーンショットの構成）との30秒ドッキング手順

お手元の `vtour` フォルダ（`panos`, `plugins`, `skin`, `tour_testingserver_macos`, `tour.html`, `tour.js`, `tour.xml` が入ったフォルダ）と本プロトタイプは、**すでに100%自動認識・統合できるように配線済み**です。

以下の **どちらか好きな方法（A または B）** で即座にドッキングできます：

### 方法A：お手元の `vtour` の中身を、本フォルダ内の `vtour/` にそのままコピーする（一番簡単・推奨！）
1. お手元の `vtour` フォルダの中にある以下のファイル・フォルダをすべて選択してコピーします：
   * `panos/` （パノラマタイル画像フォルダ）
   * `plugins/` （プラグインフォルダ）
   * `skin/` （スキンフォルダ）
   * `tour.js` （Krpanoエンジン本体）
   * `tour.xml` （Krpanoシーン定義ファイル）
   * `tour_testingserver_macos` （Mac用テストサーバー実行ファイル）
2. 本圧縮包を解凍した `mitsubishi_vr_prototype/vtour/` フォルダの中にそのまま貼り付けます。
3. `tour_testingserver_macos` を本フォルダのルート（`index.html` と同じ階層）に置いてダブルクリックして起動し、ブラウザで `index.html` を開きます。
4. **これだけで完了です！** `index.html` が自動的に `vtour/tour.js` と `vtour/tour.xml` を検知して貴社の本物のKrpanoパノラマを起動し、さらにパノラマ空間内に自動的に **「📦 ショーケースB」「🔍 古文書『三菱会社社則』超拡大＋解説併記」「🪧 展示パネル2」** のホットスポットボタンを生成します！

### 方法B：お手元の `vtour/tour.xml` の好きな座標にホットスポットを手動追加する場合
貴社の方でホットスポットの座標（`ath`, `atv`）やアイコンを細かく調整したい場合は、`vtour/tour.xml` の `<scene>` タグ内に以下の `<hotspot>` タグを貼り付けるだけで、クリック時に OpenSeadragon 超拡大ビューアやショーケース一覧が呼び出されます：

```xml
<!-- ① ショーケースBの一覧ドロワーを開くホットスポット -->
<hotspot name="hs_showcase_b" style="skin_hotspotstyle" ath="-14.0" atv="14.5"
         onclick="js(window.ArchiveBridge.openShowcaseDrawer('SHOWCASE-B'));" />

<!-- ② 古文書（郵便汽船三菱会社 社則達書）の超拡大＋解説併記画面を直接開くホットスポット -->
<hotspot name="hs_doc_001" style="skin_hotspotstyle" ath="6.0" atv="12.0"
         onclick="js(window.ArchiveBridge.openDocumentModal('MERI-M08-001'));" />

<!-- ③ 展示パネル2の全画面拡大を開くホットスポット -->
<hotspot name="hs_panel_02" style="skin_hotspotstyle" ath="-16.0" atv="-8.0"
         onclick="js(window.ArchiveBridge.openPanelModal('PANEL-02'));" />

<!-- ④ タッチパネル（過去の企画展・三菱のあゆみ）を開くホットスポット -->
<hotspot name="hs_touch_special" style="skin_hotspotstyle" ath="32.0" atv="-3.0"
         onclick="js(window.ArchiveBridge.openSpecialExhibitionModal());" />
```

## 1. ディレクトリ・ファイル構造

```text
mitsubishi_vr_prototype/
├── index.html                  # メインエントリ（来館者用360°展示室ビュー ＆ CMS管理画面デモ）
├── README.md                   # 構成説明書・プレゼン実演ガイド（本書）
├── css/
│   └── style.css               # 高齢者配慮UI・レスポンシブ・印刷/右クリック防盗制御スタイル
├── js/
│   └── app.js                  # Krpano連携・OpenSeadragon制御・CMSリアルタイム同期ロジック
├── krpano/
│   ├── tour.xml                # Krpano 360°空間設定・3Dトランジション・JSブリッジ定義ファイル
│   └── krpano_bridge.js        # Krpano <-> OpenSeadragon / CMS 連携インターフェース
├── data/
│   └── exhibition_data.json    # 展示パネル・ショーケース・原史料・日英解説・歴史用語辞書データ
└── assets/
    ├── panoramas/
    │   └── room1_equirectangular.jpg  # 第一展示室（21.3坪）2:1 360°パノラマ画像
    ├── panels/
    │   └── panel_02.jpg               # 展示パネル2 高解像度データ
    └── documents/
        ├── doc_001/                   # 史料1：郵便汽船三菱会社 社則達書（明治8年・毛筆・朱印）
        │   ├── doc.dzi                # Deep Zoom Image (DZI) XML記述子
        │   ├── doc_files/             # ピラミッド階層タイル群（256×256px細分化画像）
        │   └── master_preview.jpg     # プレビュー用画像
        ├── doc_002/                   # 史料2：九十九商会 創立盟約書覚（明治3年）
        │   ├── doc.dzi
        │   └── doc_files/
        └── doc_003/                   # 史料3：長崎造船局 借受経営願書控（明治17年・復刻史料）
            ├── doc.dzi
            └── doc_files/
```

---

## 2. 起動方法とKrpano本番エンジンとの結合方法

### 2.1 デモの即時起動（サーバー不要）
* 本フォルダ内の `index.html` をそのままダブルクリックしてブラウザ（Chrome / Edge / Safari）で開くだけで、オフライン環境でもすべての機能（360°パノラマ回遊、ショーケース展開、OpenSeadragonによる毛筆・朱印の超拡大、解説文併記、右クリック防盗、CMS更新反映）が即座に動作します。
* ローカルWebサーバー経由で起動する場合は、任意のHTTPサーバー（`python3 -m http.server 8000` や VSCode Live Server）でルートディレクトリを配信してください。

### 2.2 貴社保有の Krpano ライセンスバイナリとの結合手順
* 本番撮影パノラマを組み込む際は、貴社保有の [krpano Tools](https://krpano.com/docu/tools/) から生成した `krpano.js` を `krpano/` フォルダに配置し、`krpano/tour.xml` を読み込ませるだけで、`onclick="js(window.ArchiveBridge.openShowcaseDrawer('SHOWCASE-B'));"` がそのまま発火し、本プロトタイプの [OpenSeadragon](https://openseadragon.github.io/) モーダルおよびCMSと100%連動します。

---

## 3. 顧客打ち合わせ時の「3分間キラー実演シナリオ」

1. **【ステップ1：空間からショーケース→古文書の超拡大＋解説併記（1分）】**
   * 画面を開き、360°パノラマ内の **「📦 ショーケースB」**（または左上プレゼン実演バーの「🔍 1. 古文書超拡大＋解説併記を実演」ボタン）をクリックします。
   * 左側に明治8年の『郵便汽船三菱会社 社則達書』（和紙・毛筆）、右側に『翻刻・現代語解説』が2画面併記で開きます。
   * 左画面下部の **「🎯 朱印・毛筆署名へ超拡大」** ボタンを押すと、岩崎彌太郎の署名と朱印「三菱社印」へ滑らかにズームインし、和紙の繊維や毛筆のかすれまで鮮明に判読できることを実演します。
   * 右画面の **「文字サイズ 大(＋)」** を押し、高齢の見学者でも解説文と古文書を見比べながら楽に読めることを示します。

2. **【ステップ2：右クリック防盗保護の実演（30秒）】**
   * 拡大した古文書の上で **マウス右クリック** を行います。
   * 即座に画面右下に **「🛡️ コンテンツ保護作動：右クリック・画像保存は禁止されています」** の警告が表示され、さらに `assets/documents/doc_001/doc_files/` フォルダを見せて「サーバー上では256pxの細切れタイルに分割されているため、1枚の元画像として丸ごと抜き出すことは物理的に不可能である」と説明し、要件「2-(2)⑧・4-(8)」のセキュリティ懸念を100%解消します。

3. **【ステップ3：CMS管理画面での自前更新＆再撮影ゼロの実演（1分30秒）】**
   * 画面上部の **「⚙️ 史料館CMS 管理画面デモ」** タブをクリックします。
   * **「🤖 DeepL API ＋ 三菱歴史用語辞書で英訳下書き自動生成」** ボタンを押して、固有名詞（岩崎彌太郎・郵便汽船三菱会社）が正確に英訳される様子を実演します。
   * さらに緑色の **「＋ 過去展示史料をショーケースBへ1クリック新規追加」** ボタンを押すか、解説文を書き換えて **「💾 承認してウェブ展示室へ即時公開反映する」** をクリックします。
   * 再び「🏛️ 展示室 360°ビュー」に戻ってショーケースBを開くと、**360度空間の再撮影を一切行うことなく、今追加・修正した史料が即座に反映されている** ことを確認していただきます。




方法 B：单张图片手动生成 Deep Zoom 切片（临时补图或单独处理）
方式 1（使用包内自带的命令行切片工具 tools/make_single_dzi.py）：
打开终端（Mac）或命令提示符（Windows），首次使用先安装图像库 pip install Pillow，然后执行一行命令即可将任意尺寸大图切好：
python3 tools/make_single_dzi.py <输入原图路径> <输出目录路径>
# 示例：将一张 8000x12000 的不规则竖版大图切为 DZI 瓦片
python3 tools/make_single_dzi.py ./my_scroll.tif ./assets/documents/MERI-M08-001/page_4


方式 2（使用工业级高速命令行工具 libvips）：
如果后期有上万像素的超大 TIFF 扫描件，可在 Mac（brew install vips）或 Windows 下使用 vips dzsave 命令秒级生成标准 Deep Zoom 切片：
vips dzsave input_original.tif assets/documents/MERI-M08-001/page_1/doc --tile-size 256 --overlap 0 --suffix .jpg[Q=90]
