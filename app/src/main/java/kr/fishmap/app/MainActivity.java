package kr.fishmap.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.WindowInsets;
import android.widget.FrameLayout;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final String START_URL = "https://appassets.androidplatform.net/assets/index.html";
    private WebView web;
    private WebViewAssetLoader assets;
    private GeolocationPermissions.Callback pendingGeoCb;
    private String pendingGeoOrigin;
    private final ExecutorService pool = Executors.newFixedThreadPool(4);

    @SuppressLint({"SetJavaScriptEnabled", "AddJavascriptInterface"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        assets = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        web = new WebView(this);
        // 안드 15+(목표 36)는 화면이 상태 표시줄·아래 버튼 줄 밑까지 그려짐 → 그만큼 여백 (REQ-51)
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(0xFF0A1520);
        root.addView(web);
        setContentView(root);
        root.setOnApplyWindowInsetsListener((v, ins) -> {
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets b = ins.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout() | WindowInsets.Type.ime());
                v.setPadding(b.left, b.top, b.right, b.bottom);
                return WindowInsets.CONSUMED;
            }
            v.setPadding(ins.getSystemWindowInsetLeft(), ins.getSystemWindowInsetTop(), ins.getSystemWindowInsetRight(), ins.getSystemWindowInsetBottom());
            return ins.consumeSystemWindowInsets();
        });
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setGeolocationEnabled(true);
        s.setAllowFileAccess(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);

        web.addJavascriptInterface(new Bridge(), "AndroidBridge");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                return assets.shouldInterceptRequest(req.getUrl());
            }
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if ("appassets.androidplatform.net".equals(u.getHost())) return false;
                // 바깥 링크는 브라우저로
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) {}
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback cb) {
                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
                    cb.invoke(origin, true, false);
                } else {
                    pendingGeoCb = cb;
                    pendingGeoOrigin = origin;
                    requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}, 7);
                }
            }
        });

        if (savedInstanceState != null) web.restoreState(savedInstanceState);
        else web.loadUrl(START_URL);
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] results) {
        if (code == 7 && pendingGeoCb != null) {
            boolean ok = false;
            for (int r : results) if (r == PackageManager.PERMISSION_GRANTED) ok = true;
            pendingGeoCb.invoke(pendingGeoOrigin, ok, false);
            pendingGeoCb = null;
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public void onBackPressed() {
        web.evaluateJavascript("window.__onBack ? window.__onBack() : false", v -> {
            if (!"true".equals(v)) MainActivity.super.onBackPressed();
        });
    }

    /** 화면(자바스크립트)에서 부르는 기능들 */
    class Bridge {
        private SharedPreferences prefs() { return getSharedPreferences("fishmap", Context.MODE_PRIVATE); }

        /** 앱 버전 (진단용): "1.19 (20)" */
        @JavascriptInterface public String appVersion() {
            try { android.content.pm.PackageInfo pi = getPackageManager().getPackageInfo(getPackageName(), 0);
                @SuppressWarnings("deprecation") int vc = pi.versionCode; return pi.versionName + " (" + vc + ")"; } catch (Throwable e) { return "?"; }
        }
        /** 안전 알림: 알림 권한 확인(없으면 요청). "ok" / "asked"(지금 물어봄) / "off"(꺼져 있음) */
        @JavascriptInterface public String notifyPrep() {
            AlarmReceiver.ensureChannel(MainActivity.this);
            if (android.os.Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                runOnUiThread(() -> requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 8));
                return "asked";
            }
            android.app.NotificationManager nm = (android.app.NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            return nm.areNotificationsEnabled() ? "ok" : "off";
        }
        @JavascriptInterface public String scheduleAlarm(int id, String atMs, String title, String text) {
            try { return AlarmReceiver.schedule(MainActivity.this, id, Long.parseLong(atMs), title, text); } catch (Exception e) { return "err:" + e.getMessage(); }
        }
        @JavascriptInterface public void cancelAlarm(int id) { AlarmReceiver.cancel(MainActivity.this, id); }
        /** 정확한 시각 알람 허용 여부: "yes" / "no"(안드 12+에서 '알람 및 리마인더' 꺼짐) */
        @JavascriptInterface public String exactAlarmOk() {
            if (Build.VERSION.SDK_INT < 31) return "yes";
            android.app.AlarmManager am = (android.app.AlarmManager) getSystemService(Context.ALARM_SERVICE);
            return am.canScheduleExactAlarms() ? "yes" : "no";
        }
        @JavascriptInterface public void openExactAlarmSettings() {
            if (Build.VERSION.SDK_INT < 31) return;
            runOnUiThread(() -> { try { startActivity(new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM, Uri.parse("package:" + getPackageName()))); } catch (Exception ignored) { } });
        }
        @JavascriptInterface public String getPref(String k) { return prefs().getString(k, ""); }
        @JavascriptInterface public void setPref(String k, String v) { prefs().edit().putString(k, v).apply(); }

        /** 인터넷 주소 내용을 받아서 window.__nativeCb(id, 상태코드, 내용) 으로 돌려줌. maxAgeMin 동안은 저장된 것 사용 */
        @JavascriptInterface
        public void httpGet(final String url, final String cbId, final int maxAgeMin) {
            pool.execute(() -> {
                int code;
                String body;
                File cache = cacheFile(url);
                try {
                    if (maxAgeMin > 0 && cache.exists() && System.currentTimeMillis() - cache.lastModified() < maxAgeMin * 60000L) {
                        // 2000000 + 경과 분 = '기간 안의 저장본'이라는 표시 (진단·빈 대답 재확인용)
                        code = 2000000 + (int) ((System.currentTimeMillis() - cache.lastModified()) / 60000L);
                        body = read(new FileInputStream(cache));
                    } else {
                        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
                        c.setConnectTimeout(15000);
                        c.setReadTimeout(30000);
                        c.setRequestProperty("Accept", "application/json");
                        code = c.getResponseCode();
                        InputStream in = code >= 400 ? c.getErrorStream() : c.getInputStream();
                        body = in == null ? "" : read(in);
                        c.disconnect();
                        if (code == 200 && maxAgeMin > 0) {
                            try (FileOutputStream o = new FileOutputStream(cache)) { o.write(body.getBytes(StandardCharsets.UTF_8)); }
                        }
                    }
                } catch (Exception e) {
                    // 인터넷이 안 될 때(갯바위 등): 오래됐더라도 저장된 자료가 있으면 그걸 사용
                    String stale = null;
                    try { if (cache.exists()) stale = read(new FileInputStream(cache)); } catch (Exception ignored) {}
                    // 1000 + 경과 분 = '오래된 저장 자료'라는 표시 (화면에서 "N시간 전 받음" 표시용)
                    if (stale != null) {
                        long ageMin = Math.max(1, (System.currentTimeMillis() - cache.lastModified()) / 60000L);
                        code = 1000 + (int) Math.min(ageMin, 500000L);
                        body = stale;
                    }
                    else { code = -1; body = String.valueOf(e.getMessage()); }
                }
                final String js = "window.__nativeCb(" + JSONObject.quote(cbId) + "," + code + "," + JSONObject.quote(body) + ")";
                web.post(() -> web.evaluateJavascript(js, null));
            });
        }

        @JavascriptInterface
        public void dropCache(String url) { cacheFile(url).delete(); }

        /** 즐겨찾기 백업 글을 카톡·메모 등으로 보내기 */
        @JavascriptInterface
        public void shareText(final String text) {
            runOnUiThread(() -> {
                Intent i = new Intent(Intent.ACTION_SEND);
                i.setType("text/plain");
                i.putExtra(Intent.EXTRA_TEXT, text);
                i.putExtra(Intent.EXTRA_SUBJECT, "바다흐름지도 백업");
                try { startActivity(Intent.createChooser(i, "즐겨찾기 백업 보내기")); } catch (Exception ignored) {}
            });
        }

        /** 지난 자료 청소: rules = "roms:11520,tide:2880,wind:4320,misc:43200,legacy:0" (종류:보관 분). 결과 "지운 개수,바이트" */
        @JavascriptInterface
        public String cleanCache(String rules) {
            java.util.Map<String, Long> keep = new java.util.HashMap<>();
            for (String r : rules.split(",")) { String[] kv = r.split(":"); if (kv.length == 2) try { keep.put(kv[0].trim(), Long.parseLong(kv[1].trim())); } catch (Exception ignored) {} }
            File[] fs = new File(getCacheDir(), "http").listFiles();
            int n = 0; long bytes = 0; long now = System.currentTimeMillis();
            if (fs != null) for (File f : fs) {
                String nm = f.getName(); int u = nm.indexOf('_');
                String cat = u > 0 ? nm.substring(0, u) : "legacy";
                Long k = keep.get(cat); if (k == null) k = keep.get("misc"); if (k == null) continue;
                if (now - f.lastModified() > k * 60000L) { long len = f.length(); if (f.delete()) { n++; bytes += len; } }
            }
            return n + "," + bytes;
        }

        @JavascriptInterface
        public void clearCache() {
            File[] fs = new File(getCacheDir(), "http").listFiles();
            if (fs != null) for (File f : fs) f.delete();
        }
    }

    private File cacheFile(String url) {
        File dir = new File(getCacheDir(), "http");
        dir.mkdirs();
        try {
            // 종류별 이름표 → 지난 자료 청소 때 종류마다 보관 기간을 다르게
            String cat = url.contains("/roms/") ? "roms" : url.contains("tideFcst") ? "tide" : url.contains("VilageFcst") ? "wind" : "misc";
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            StringBuilder sb = new StringBuilder();
            for (byte b : md.digest(url.getBytes(StandardCharsets.UTF_8))) sb.append(String.format("%02x", b));
            return new File(dir, cat + "_" + sb);
        } catch (Exception e) {
            return new File(dir, "misc_" + Integer.toHexString(url.hashCode()));
        }
    }

    private static String read(InputStream in) throws Exception {
        ByteArrayOutputStream bo = new ByteArrayOutputStream();
        byte[] buf = new byte[16384];
        int n;
        while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
        in.close();
        return bo.toString("UTF-8");
    }
}
