# 루멘콘덴서 계산기

오프라인 대전 카드게임 '루멘콘덴서'를 두 사람이 폰 한 대로 함께 쓰는 체력·토큰 계산기입니다.
앱 전체가 `lumencalc.html` 한 파일에 들어 있습니다.

**기능과 규칙의 전체 설명은 `lumencalc.html` 맨 위 주석에 있습니다.** 수정하거나 APK로 만들기 전에 먼저 읽어 주세요.

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `lumencalc.html` | 앱 본체 (HTML·CSS·JS 한 파일) |
| `assets/characters/` | 캐릭터 전신·두상·특성 마크 이미지. 이름 규칙은 그 폴더의 `README.txt` |
| `lumencalc.apk` | 안드로이드 설치 파일 (캐릭터 그림을 뺀 GitHub용 버전) |
| `app/` | APK를 만드는 Capacitor 안드로이드 프로젝트 (`build-apk.ps1`로 다시 빌드, `build-aab.ps1`은 구글 플레이용 앱 번들) |

`assets/` 안의 파일(캐릭터 그림·글꼴)과 구글 플레이 릴리즈 폴더 `release/`는 GitHub에 올리지 않습니다(`.gitignore`).
저장소를 새로 받은 경우 `assets/`를 따로 채워야 하며, 글꼴이 없으면 인터넷에서 받아 씁니다.

## APK 설치 · 다시 빌드

- **설치:** `lumencalc.apk`를 폰으로 옮겨 실행합니다. "출처를 알 수 없는 앱" 설치 허용이 필요할 수 있습니다.
- **다시 빌드:** `lumencalc.html`을 고친 뒤 `powershell -ExecutionPolicy Bypass -File app\build-apk.ps1`을 실행하면 `lumencalc.apk`가 새로 만들어집니다.
  - 처음 한 번은 `app/`에서 `npm install`이 필요합니다.
  - 새 버전을 낼 때는 `lumencalc.html`의 `APP.version`과 `app/android/app/build.gradle`의 `versionName`을 같이 올리고, `versionCode`도 1씩 올려야 기존 앱 위에 업데이트 설치됩니다.
- **서명 키:** `app/android/release.keystore`와 `keystore.properties`는 git에 올리지 않습니다. 이 키를 잃어버리면 기존 설치본 위에 업데이트할 수 없으니 따로 백업해 두세요.
- 아래 1~5번 설정은 `app/`에 이미 모두 적용되어 있습니다.

## APK로 만들 때 꼭 지킬 것

1. **화면은 세로 고정.** 이 앱은 세로 전용이고, 폰을 옆으로 눕혀서 씁니다. 화면이 세로면 앱이 스스로 90° 돌아 가로 레이아웃을 그립니다(폰 윗부분 = 1P 쪽).
   - `AndroidManifest.xml`의 Activity에 `android:screenOrientation="portrait"`를 넣어 주세요.
   - OS가 화면을 돌리면 앱의 회전과 겹쳐서 화면이 틀어집니다.
2. **노치 대응:** `styles.xml`에 `android:windowLayoutInDisplayCutoutMode` = `shortEdges`를 권장합니다.
3. **화면 꺼짐 방지:** JS Wake Lock을 쓰고 있지만, `MainActivity`에 `FLAG_KEEP_SCREEN_ON`도 넣는 것을 권장합니다.
4. **진동:** `VIBRATE` 권한이 필요합니다.
5. **저장:** localStorage 키 `lumencalc.v6` 하나에 모든 상태를 저장합니다. WebView의 DOM Storage를 켜 주세요.
6. **파일 복사:** `lumencalc.html`을 `index.html`로 넣고 `assets/` 폴더도 함께 복사합니다.
7. **글꼴:** Google Fonts를 씁니다. 오프라인이면 시스템 글꼴로 대신 표시되며, 동작에는 문제가 없습니다.
8. **버전:** 새 버전을 낼 때 스크립트의 `APP.version`과 `APP.build`를 올려 주세요. 설정 > 버전 탭에 표시됩니다.

## 폰 브라우저로 확인하기

`lumencalc.html`이나 아티팩트 링크를 폰에서 **세로로 들고** 열면 APK와 같은 회전 화면이 나옵니다. 폰의 자동 회전을 꺼 두면 APK와 완전히 같은 조건이 됩니다.

PC처럼 원래 가로인 화면에서는 회전하지 않습니다.
