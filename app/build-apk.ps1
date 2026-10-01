# Build the APKs from ../lumencalc.html
#   powershell -ExecutionPolicy Bypass -File app\build-apk.ps1            -> both APKs
#   powershell -ExecutionPolicy Bypass -File app\build-apk.ps1 -Only github
#   powershell -ExecutionPolicy Bypass -File app\build-apk.ps1 -Only release
#
#   github  : ../lumencalc.apk (committed to GitHub) - character images are LEFT OUT
#             (assets/characters/*.png|webp|jpg). Fonts and README stay in.
#   release : ../release/lumencalc-<ver>-vc<code>.apk (local only, git-ignored) - everything included
#
# Needs: Node, JDK 21, Android SDK (paths below), npm install once in app/,
#        android/keystore.properties + release.keystore for release signing (not in git).
# Remember to bump APP.version in lumencalc.html and versionName/versionCode in android/app/build.gradle.
param([ValidateSet('both', 'github', 'release')][string]$Only = 'both')
$ErrorActionPreference = 'Stop'
$tools = 'C:\Users\chris\android-build-tools'
$env:JAVA_HOME = "$tools\jdk21"
$env:Path = "$tools\node;$env:JAVA_HOME\bin;$env:Path"

$app = $PSScriptRoot
$root = Split-Path $app -Parent
$release = "$root\release"
$gradle = Get-Content "$app\android\app\build.gradle" -Raw
$ver = [regex]::Match($gradle, 'versionName "([^"]+)"').Groups[1].Value
$code = [regex]::Match($gradle, 'versionCode (\d+)').Groups[1].Value

function Build-Apk([bool]$withArt, [string]$dest) {
  # 1. web files -> www (lumencalc.html becomes index.html)
  New-Item -ItemType Directory -Force "$app\www" | Out-Null
  Copy-Item "$root\lumencalc.html" "$app\www\index.html" -Force
  if ($withArt) {
    robocopy "$root\assets" "$app\www\assets" /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
  } else {
    robocopy "$root\assets" "$app\www\assets" /MIR /XF *.png *.webp *.jpg *.jpeg /NFL /NDL /NJH /NJS /NP | Out-Null
  }
  # 2. copy into the Android project and build a signed release APK
  Set-Location $app
  npx cap sync android
  Set-Location "$app\android"
  # --no-daemon: a background Gradle daemon keeps the console pipe open and the calling shell never returns
  cmd /c ".\gradlew.bat assembleRelease --console=plain --no-daemon"
  if ($LASTEXITCODE -ne 0) { throw 'gradle build failed' }
  Copy-Item "$app\android\app\build\outputs\apk\release\app-release.apk" $dest -Force
  "built: $dest"
}

if ($Only -ne 'release') { Build-Apk $false "$root\lumencalc.apk" }
if ($Only -ne 'github') {
  New-Item -ItemType Directory -Force $release | Out-Null
  Build-Apk $true "$release\lumencalc-$ver-vc$code.apk"
}
