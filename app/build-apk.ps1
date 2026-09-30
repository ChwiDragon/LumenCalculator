# Rebuild lumencalc.apk from ../lumencalc.html
#   powershell -ExecutionPolicy Bypass -File app\build-apk.ps1
# Needs: Node, JDK 21, Android SDK (paths below), npm install once in app/,
#        android/keystore.properties + release.keystore for release signing (not in git).
# Remember to bump APP.version in lumencalc.html and versionName/versionCode in android/app/build.gradle.
$ErrorActionPreference = 'Stop'
$tools = 'C:\Users\chris\android-build-tools'
$env:JAVA_HOME = "$tools\jdk21"
$env:Path = "$tools\node;$env:JAVA_HOME\bin;$env:Path"

$app = $PSScriptRoot
$root = Split-Path $app -Parent

# 1. web files -> www (lumencalc.html becomes index.html)
New-Item -ItemType Directory -Force "$app\www" | Out-Null
Copy-Item "$root\lumencalc.html" "$app\www\index.html" -Force
robocopy "$root\assets" "$app\www\assets" /MIR /NFL /NDL /NJH /NJS /NP | Out-Null

# 2. copy into the Android project and build a signed release APK
Set-Location $app
npx cap sync android
Set-Location "$app\android"
# --no-daemon: a background Gradle daemon keeps the console pipe open and the calling shell never returns
cmd /c ".\gradlew.bat assembleRelease --console=plain --no-daemon"
if ($LASTEXITCODE -ne 0) { throw 'gradle build failed' }

# 3. result -> ../lumencalc.apk
Copy-Item "$app\android\app\build\outputs\apk\release\app-release.apk" "$root\lumencalc.apk" -Force
"built: $root\lumencalc.apk"
