# Build the Google Play upload bundle (.aab) from ../lumencalc.html into ../release/
#   powershell -ExecutionPolicy Bypass -File app\build-aab.ps1
# The release/ folder and assets/ are git-ignored: the bundle (with character art) never goes to GitHub.
# Signed with android/release.keystore (= Play "upload key"). Bump versionCode in android/app/build.gradle
# for every upload - Play rejects a versionCode it has already seen.
$ErrorActionPreference = 'Stop'
$tools = 'C:\Users\chris\android-build-tools'
$env:JAVA_HOME = "$tools\jdk21"
$env:Path = "$tools\node;$env:JAVA_HOME\bin;$env:Path"

$app = $PSScriptRoot
$root = Split-Path $app -Parent
$release = "$root\release"
New-Item -ItemType Directory -Force $release | Out-Null

# 1. web files -> www (same as build-apk.ps1)
New-Item -ItemType Directory -Force "$app\www" | Out-Null
Copy-Item "$root\lumencalc.html" "$app\www\index.html" -Force
robocopy "$root\assets" "$app\www\assets" /MIR /NFL /NDL /NJH /NJS /NP | Out-Null

# 2. sync + signed release bundle
Set-Location $app
npx cap sync android
Set-Location "$app\android"
cmd /c ".\gradlew.bat bundleRelease --console=plain --no-daemon"
if ($LASTEXITCODE -ne 0) { throw 'gradle bundleRelease failed' }

# 3. versioned copy into release/
$gradle = Get-Content "$app\android\app\build.gradle" -Raw
$ver = [regex]::Match($gradle, 'versionName "([^"]+)"').Groups[1].Value
$code = [regex]::Match($gradle, 'versionCode (\d+)').Groups[1].Value
$out = "$release\lumencalc-$ver-vc$code.aab"
Copy-Item "$app\android\app\build\outputs\bundle\release\app-release.aab" $out -Force
"built: $out"
