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
# 코드 축소·최적화만 하고 이름 바꾸기(난독화)는 하지 않음 → 오류 기록(스택 트레이스)을 그대로 읽을 수 있음
-dontobfuscate
-keepattributes SourceFile,LineNumberTable,*Annotation*,Signature,InnerClasses,EnclosingMethod

# Capacitor 브리지는 플러그인·메서드를 리플렉션으로 찾으므로 통째로 유지 (크기가 작음)
-keep class com.getcapacitor.** { *; }
-keep class org.apache.cordova.** { *; }

# WebView 자바스크립트 인터페이스 (Capacitor SystemBars 등 @JavascriptInterface 메서드)
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
