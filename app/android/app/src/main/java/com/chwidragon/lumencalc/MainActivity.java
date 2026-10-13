package com.chwidragon.lumencalc;

import android.content.pm.PackageInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class MainActivity extends BridgeActivity {
    // 이 버전부터 WebView가 시스템 바 여백을 CSS env(safe-area-inset-*)로 직접 넘겨줌 (Capacitor SystemBars와 같은 기준)
    private static final int WEBVIEW_SAFE_AREA_FIX = 140;

    // 로그 TXT 내보내기: 안드로이드 '다른 이름으로 저장' 창(저장소 접근 프레임워크)으로 사용자가 고른 곳에 씀.
    // 사용자가 고른 파일 하나에만 쓰므로 저장소 권한이 필요 없음.
    private ActivityResultLauncher<String> saveLauncher;
    private String pendingText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // 결과 받기는 화면이 시작되기 전(onCreate)에 등록해야 함
        saveLauncher = registerForActivityResult(new ActivityResultContracts.CreateDocument("text/plain"), this::writePendingText);
        super.onCreate(savedInstanceState);
        // JS Wake Lock의 보조: 경기 중 화면이 꺼지지 않게 함
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        // 전체 화면: 상단바·하단바(내비게이션 바)를 숨김. 화면 가장자리에서 쓸어 넘기면 잠깐 나타났다가 다시 숨음.
        // 첫 화면을 그리기 전에 숨겨서 시작할 때 화면 크기가 바뀌지 않게 함
        hideSystemBars();
        if (getBridge() == null || getBridge().getWebView() == null) return;
        WebView webView = getBridge().getWebView();
        // 폰의 '글자 크기' 설정이 WebView 글자만 키워서 토큰 숫자가 +/− 버튼과 겹치던 문제 방지.
        // 레이아웃은 화면 크기에 맞춰 스스로 커지고 작아지므로 글자 배율은 100%로 고정.
        webView.getSettings().setTextZoom(100);
        // 시작할 때 화면이 한 번 커지며 버벅이던 문제 방지.
        // Capacitor는 페이지를 읽기 전까지 viewport-fit=cover인지 몰라서 WebView를 시스템 바만큼 줄여 띄웠다가,
        // 읽은 뒤에야 전체 화면으로 키움 → 화면 크기 기준인 레이아웃 전체가 다시 계산됨.
        // 이 앱은 항상 viewport-fit=cover이므로 처음부터 전체 화면으로 두고 여백은 HTML의 env()가 처리.
        // (WebView가 오래되어 env()가 안 되는 폰은 Capacitor 기본 동작을 그대로 씀)
        if (webViewMajorVersion() >= WEBVIEW_SAFE_AREA_FIX && webView.getParent() instanceof View) {
            ViewCompat.setOnApplyWindowInsetsListener((View) webView.getParent(), (v, insets) -> {
                v.setPadding(0, 0, 0, 0);
                return insets;
            });
        }
        // 페이지 JS에서 window.LumenNative.saveText(파일이름, 내용) 으로 부름 (앱 안의 로컬 페이지만 열림)
        webView.addJavascriptInterface(new NativeBridge(), "LumenNative");
    }

    private class NativeBridge {
        @JavascriptInterface
        public void saveText(String name, String text) {
            runOnUiThread(() -> {
                pendingText = text;
                try {
                    saveLauncher.launch(name);
                } catch (Exception e) {
                    pendingText = null;
                    notifySaved("fail");
                }
            });
        }
    }

    private void writePendingText(Uri uri) {
        String text = pendingText;
        pendingText = null;
        if (uri == null || text == null) {
            notifySaved("cancel");
            return;
        }
        try (OutputStream out = getContentResolver().openOutputStream(uri, "wt")) {
            if (out == null) throw new java.io.IOException("no stream");
            out.write(text.getBytes(StandardCharsets.UTF_8));
            notifySaved("ok");
        } catch (Exception e) {
            notifySaved("fail");
        }
    }

    private void notifySaved(String result) {
        if (getBridge() == null || getBridge().getWebView() == null) return;
        getBridge().getWebView().evaluateJavascript("window.onLogSaved && window.onLogSaved('" + result + "')", null);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        // 다른 앱·알림창에서 돌아왔을 때 다시 숨김
        if (hasFocus) hideSystemBars();
    }

    private void hideSystemBars() {
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        WindowInsetsControllerCompat controller = WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        controller.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
        controller.hide(WindowInsetsCompat.Type.systemBars());
    }

    private int webViewMajorVersion() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return 0;
        PackageInfo info = WebView.getCurrentWebViewPackage();
        if (info == null || info.versionName == null) return 0;
        try {
            return Integer.parseInt(info.versionName.split("\\.")[0]);
        } catch (NumberFormatException e) {
            return 0;
        }
    }
}
