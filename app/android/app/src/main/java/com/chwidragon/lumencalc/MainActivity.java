package com.chwidragon.lumencalc;

import android.content.pm.PackageInfo;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebView;
import androidx.core.view.ViewCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    // 이 버전부터 WebView가 시스템 바 여백을 CSS env(safe-area-inset-*)로 직접 넘겨줌 (Capacitor SystemBars와 같은 기준)
    private static final int WEBVIEW_SAFE_AREA_FIX = 140;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // JS Wake Lock의 보조: 경기 중 화면이 꺼지지 않게 함
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
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
