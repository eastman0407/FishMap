package kr.fishmap.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
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
        setContentView(web);
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
                        code = 200;
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
                    if (stale != null) { code = 200; body = stale; }
                    else { code = -1; body = String.valueOf(e.getMessage()); }
                }
                final String js = "window.__nativeCb(" + JSONObject.quote(cbId) + "," + code + "," + JSONObject.quote(body) + ")";
                web.post(() -> web.evaluateJavascript(js, null));
            });
        }

        @JavascriptInterface
        public void dropCache(String url) { cacheFile(url).delete(); }

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
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            StringBuilder sb = new StringBuilder();
            for (byte b : md.digest(url.getBytes(StandardCharsets.UTF_8))) sb.append(String.format("%02x", b));
            return new File(dir, sb.toString());
        } catch (Exception e) {
            return new File(dir, Integer.toHexString(url.hashCode()));
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
