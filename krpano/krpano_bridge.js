/**
 * Krpano `vtour` (tour.js / tour.xml) <-> OpenSeadragon & CMS Dynamic Bridge
 * 
 * 【自動認識ハイブリッド起動ロジック】
 * 1. `vtour/tour.js` が存在し、`embedpano` 関数がロードされた場合：
 *    貴社の本物の Krpano エンジン (`vtour/tour.xml`) を `#pano-viewport` にネイティブ起動します！
 *    さらに Krpano API (`krpano.call`) を通じて、既存のシーンを壊すことなく「ショーケースB」「パネル2」「古文書超拡大」の
 *    ホットスポットを自動注入します（もちろん `tour.xml` 側に手動記述することも可能です）。
 * 2. `vtour/tour.js` がまだコピーされていない場合（またはダブルクリックで直接開いた場合）：
 *    自動的に内蔵の 360° Canvas フォールバックエンジンが起動し、エラーゼロで動作します。
 */

window.KrpanoInstance = null;

window.initRealKrpanoIfAvailable = function() {
    if (typeof window.embedpano !== "function") {
        console.log("[KrpanoBridge] vtour/tour.js not detected. Running built-in 360 Canvas mode.");
        return false;
    }

    console.log("[KrpanoBridge] Real vtour/tour.js detected! Launching native Krpano engine via embedpano()...");

    // Hide fallback canvas & fallback HTML hotspots when real Krpano takes over
    const fallbackCanvas = document.getElementById("pano-canvas");
    const fallbackHotspots = document.getElementById("hotspot-layer");
    if (fallbackCanvas) fallbackCanvas.style.display = "none";
    if (fallbackHotspots) fallbackHotspots.style.display = "none";

    // Create dedicated div for real Krpano inside #pano-viewport
    let krpanoTarget = document.getElementById("krpano-real-target");
    if (!krpanoTarget) {
        krpanoTarget = document.createElement("div");
        krpanoTarget.id = "krpano-real-target";
        krpanoTarget.style.width = "100%";
        krpanoTarget.style.height = "100%";
        const viewport = document.getElementById("pano-viewport");
        viewport.insertBefore(krpanoTarget, viewport.firstChild);
    }

    window.embedpano({
        swf: "vtour/tour.swf",
        xml: "vtour/tour.xml",
        target: "krpano-real-target",
        html5: "only",
        mobilescale: 1.0,
        passQueryParameters: true,
        onready: function(krpanoInterface) {
            window.KrpanoInstance = krpanoInterface;
            console.log("[KrpanoBridge] Native Krpano ready! Injecting Mitsubishi Archives interactive hotspots...");
            injectDynamicHotspotsIntoRealKrpano(krpanoInterface);
        }
    });

    return true;
};

function injectDynamicHotspotsIntoRealKrpano(krpano) {
    if (!krpano || typeof krpano.call !== "function") return;

    // Register scene change event so hotspots persist even when moving between scenes in vtour
    krpano.call("set(events[meri_bridge_events].keep, true);");
    krpano.call("set(events[meri_bridge_events].onnewscene, js(window.injectHotspotsOnScene()));");
    window.injectHotspotsOnScene = function() {
        createKrpanoTextHotspot(
            krpano,
            "hs_meri_showcase_b",
            -14.0,
            14.0,
            "📦 ショーケースB（史料一覧・超拡大）",
            "0xB81C22",
            "window.ArchiveBridge.openShowcaseDrawer('SHOWCASE-B')"
        );
        createKrpanoTextHotspot(
            krpano,
            "hs_meri_doc_direct",
            6.0,
            12.0,
            "🔍 古文書『三菱会社社則』超拡大＋解説併記",
            "0xD97706",
            "window.ArchiveBridge.openDocumentModal('MERI-M08-001')"
        );
        createKrpanoTextHotspot(
            krpano,
            "hs_meri_panel_02",
            -16.0,
            -8.0,
            "🪧 展示パネル2（全画面拡大）",
            "0x0284C7",
            "window.ArchiveBridge.openPanelModal('PANEL-02')"
        );
        createKrpanoTextHotspot(
            krpano,
            "hs_meri_touch",
            32.0,
            -3.0,
            "🖥️ タッチパネル（過去の企画展）",
            "0x059669",
            "window.ArchiveBridge.openSpecialExhibitionModal()"
        );
    };
    window.injectHotspotsOnScene();
}

function createKrpanoTextHotspot(krpano, hsName, ath, atv, labelText, bgHex, jsCallbackStr) {
    krpano.call("addhotspot(" + hsName + ");");
    krpano.call("set(hotspot[" + hsName + "].type, 'text');");
    krpano.call("set(hotspot[" + hsName + "].ath, " + ath + ");");
    krpano.call("set(hotspot[" + hsName + "].atv, " + atv + ");");
    krpano.call("set(hotspot[" + hsName + "].html, '" + labelText + "');");
    krpano.call("set(hotspot[" + hsName + "].css, 'font-family:sans-serif; font-size:13px; font-weight:bold; color:#ffffff;');");
    krpano.call("set(hotspot[" + hsName + "].padding, '8 14');");
    krpano.call("set(hotspot[" + hsName + "].bg, true);");
    krpano.call("set(hotspot[" + hsName + "].bgcolor, " + bgHex + ");");
    krpano.call("set(hotspot[" + hsName + "].bgalpha, 0.92);");
    krpano.call("set(hotspot[" + hsName + "].bgroundedge, 10);");
    krpano.call("set(hotspot[" + hsName + "].bgborder, '2 0xFBBF24 0.9');");
    krpano.call("set(hotspot[" + hsName + "].onclick, js(" + jsCallbackStr + "));");
}
