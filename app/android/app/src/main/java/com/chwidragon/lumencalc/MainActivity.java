package com.chwidragon.lumencalc;

import android.os.Bundle;
import android.view.WindowManager;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // JS Wake Lock의 보조: 경기 중 화면이 꺼지지 않게 함
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        // 폰의 '글자 크기' 설정이 WebView 글자만 키워서 토큰 숫자가 +/− 버튼과 겹치던 문제 방지.
        // 레이아웃은 화면 크기에 맞춰 스스로 커지고 작아지므로 글자 배율은 100%로 고정.
        if (getBridge() != null && getBridge().getWebView() != null) {
            getBridge().getWebView().getSettings().setTextZoom(100);
        }
    }
}
