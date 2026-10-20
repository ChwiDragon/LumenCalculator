# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# Uncomment this to preserve the line number information for
# debugging stack traces.
#-keepattributes SourceFile,LineNumberTable

# If you keep the line number information, uncomment this to
# hide the original source file name.
#-renamesourcefileattribute SourceFile

# ---- 루멘콘덴서 계산기 ----
# R8 전체 모드: 축소 · 최적화 · 이름 바꾸기(난독화) · 클래스 리패키징을 모두 켬 (플레이 콘솔 'DEX 코드 최적화' 점수).
# 오류 기록(스택 트레이스)은 매핑 파일(release/…-mapping.txt, AAB에도 들어감)로 되돌려 읽음. 줄 번호는 남김.
-keepattributes SourceFile,LineNumberTable,*Annotation*,Signature,InnerClasses,EnclosingMethod
-renamesourcefileattribute SourceFile
-repackageclasses
-allowaccessmodification

# Capacitor: 리플렉션으로 찾는 플러그인 클래스 · @PluginMethod 메서드는 Capacitor 라이브러리 자체 규칙
# (node_modules/@capacitor/android/capacitor/proguard-rules.pro, consumerProguardFiles)이 지켜 줌 → 나머지는 축소 · 난독화.
# 플러그인 목록(capacitor.plugins.json)은 비어 있고, 기본 플러그인은 클래스 리터럴로 등록되므로 이름이 바뀌어도 됨.

# WebView 자바스크립트 인터페이스 (Capacitor 브리지 postMessage, MainActivity의 LumenNative.saveText):
# 메서드 이름과 @JavascriptInterface 표시가 남아 있어야 웹 페이지에서 부를 수 있음
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
