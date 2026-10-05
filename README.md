# 루멘콘덴서 계산기

오프라인 대전 카드게임 '루멘콘덴서'를 두 사람이 폰 한 대로 함께 쓰는 체력·토큰 계산기입니다.
앱 전체가 `lumencalc.html` 한 파일에 들어 있습니다.

**기능과 규칙의 전체 설명은 `lumencalc.html` 맨 위 주석에 있습니다.** 수정하거나 APK로 만들기 전에 먼저 읽어 주세요.

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `lumencalc.html` | 앱 본체 (HTML·CSS·JS 한 파일) |
| `lumencalc.apk` | 안드로이드 설치 파일 (캐릭터 그림을 뺀 GitHub용 버전) |
| `assets/characters/` | 캐릭터 전신·두상·특성 마크 이미지. 이름 규칙은 그 폴더의 `README.txt` |
| `assets/fonts/` | 앱에 넣는 글꼴 (`.woff2`). 원본 `.ttf`는 `assets/fonts/src/` |
| `app/` | APK를 만드는 Capacitor 안드로이드 프로젝트 |
| `app/build-apk.ps1` | APK 빌드 (GitHub용·릴리즈용 두 가지) |
| `app/build-aab.ps1` | 구글 플레이 업로드용 앱 번들(`.aab`) 빌드 |
| `app/make-fonts.py` | 한글 글꼴을 앱에 쓰인 글자만 남겨 줄임 (빌드 스크립트가 자동 실행) |

`assets/` 안의 파일(캐릭터 그림·글꼴)과 구글 플레이 릴리즈 폴더 `release/`는 GitHub에 올리지 않습니다(`.gitignore`).
저장소를 새로 받은 경우 아래 [글꼴](#글꼴)과 `assets/characters/README.txt`를 보고 `assets/`를 채워 주세요.
파일이 없어도 앱은 동작합니다. 그림은 캐릭터 색으로 만든 대체 그림, 글꼴은 시스템 글꼴로 나옵니다.

## APK 설치 · 다시 빌드

- **설치:** `lumencalc.apk`를 폰으로 옮겨 실행합니다. "출처를 알 수 없는 앱" 설치 허용이 필요할 수 있습니다.
- **다시 빌드:** `lumencalc.html`을 고친 뒤 아래를 실행합니다.
  ```
  powershell -ExecutionPolicy Bypass -File app\build-apk.ps1
  ```
  - GitHub용 `lumencalc.apk` (캐릭터 그림 제외)와 릴리즈용 `release/lumencalc-<버전>-vc<코드>.apk` (전부 포함)가 만들어집니다.
    하나만 만들려면 `-Only github` 또는 `-Only release`를 붙입니다.
  - 필요한 것: Node, JDK 21, Android SDK (경로는 스크립트 위쪽), Python + `pip install fonttools brotli`.
    처음 한 번은 `app/`에서 `npm install`이 필요합니다.
  - 새 버전을 낼 때는 `lumencalc.html`의 `APP.version`·`APP.build`와 `app/android/app/build.gradle`의 `versionName`을 같이 올리고,
    `versionCode`도 1씩 올려야 기존 앱 위에 업데이트 설치됩니다.
- **서명 키:** `app/android/release.keystore`와 `keystore.properties`는 git에 올리지 않습니다.
  이 키를 잃어버리면 기존 설치본 위에 업데이트할 수 없으니 따로 백업해 두세요.
- 아래 설정은 `app/`에 이미 모두 적용되어 있습니다.

## APK로 만들 때 꼭 지킬 것

1. **화면은 세로 고정.** 이 앱은 세로 전용이고, 폰을 옆으로 눕혀서 씁니다. 화면이 세로면 앱이 스스로 90° 돌아 가로 레이아웃을 그립니다(폰 윗부분 = 1P 쪽).
   - `AndroidManifest.xml`의 Activity에 `android:screenOrientation="portrait"`를 넣어 주세요.
   - OS가 화면을 돌리면 앱의 회전과 겹쳐서 화면이 틀어집니다.
2. **노치 대응:** `styles.xml`에 `android:windowLayoutInDisplayCutoutMode` = `shortEdges`. 여백은 HTML의 `env(safe-area-inset-*)`가 비켜 줍니다.
3. **처음부터 전체 화면:** `MainActivity`가 WebView를 시작부터 전체 화면으로 둡니다.
   Capacitor 기본 동작은 페이지를 읽기 전까지 시스템 바만큼 줄여 띄웠다가 키우기 때문에, 앱을 켤 때 화면이 한 번 커지며 버벅입니다.
   (WebView 140 미만인 폰은 Capacitor 기본 동작을 그대로 씁니다)
4. **글자 배율 고정:** `MainActivity`에서 `setTextZoom(100)`. 폰의 '글자 크기' 설정이 WebView 글자만 키워 숫자가 버튼과 겹치는 것을 막습니다.
5. **화면 꺼짐 방지:** JS Wake Lock과 함께 `MainActivity`에 `FLAG_KEEP_SCREEN_ON`.
6. **진동:** `VIBRATE` 권한이 필요합니다.
7. **저장:** localStorage 키 `lumencalc.v6` 하나에 모든 상태를 저장합니다. WebView의 DOM Storage를 켜 주세요.
8. **파일 복사:** `lumencalc.html`을 `index.html`로 넣고 `assets/` 폴더도 함께 복사합니다(`assets/fonts/src/` 제외). 빌드 스크립트가 해 줍니다.

## 글꼴

Black Han Sans(제목·이름), IBM Plex Sans KR(본문), Chakra Petch(숫자)를 앱에 넣어 씁니다. 모두 SIL OFL 1.1 라이선스입니다.
인터넷 없이도 바로 같은 화면이 나오고, 늦게 받은 글꼴로 바뀌면서 화면이 출렁이는 일이 없습니다.

- 한글 글꼴은 `lumencalc.html`에 쓰인 글자만 남겨 하나당 40~70KB로 줄였습니다. 빌드할 때마다 다시 만들기 때문에 캐릭터나 문구를 추가해도 글자가 빠지지 않습니다.
- 저장소를 새로 받았다면 [google/fonts](https://github.com/google/fonts) 저장소에서 아래 파일을 `assets/fonts/src/`에 넣고 `python app/make-fonts.py`를 실행합니다.
  - `ofl/blackhansans/BlackHanSans-Regular.ttf`
  - `ofl/ibmplexsanskr/IBMPlexSansKR-Regular.ttf`, `-SemiBold.ttf`, `-Bold.ttf`
- Chakra Petch는 `assets/fonts/ChakraPetch-500/600/700.woff2`로 넣습니다. 파일이 없으면 Google Fonts에서 받아 씁니다.

## 레이아웃 규칙

- 모든 크기는 화면 크기에서 나온 단위 `--u`로 정합니다. 화면 크기만 같으면 그림·글꼴과 상관없이 버튼과 칸 크기가 같습니다.
- 캐릭터 그림은 정해진 칸 안에 채우기만 하므로, 그림의 해상도나 비율은 레이아웃에 영향을 주지 않습니다.
- 글자 줄이 칸 높이를 정하는 곳은 `line-height`를 숫자로 줍니다. 기본값 `normal`은 글꼴마다 달라서 칸이 밀립니다.

## 폰 브라우저로 확인하기

`lumencalc.html`이나 아티팩트 링크를 폰에서 **세로로 들고** 열면 APK와 같은 회전 화면이 나옵니다. 폰의 자동 회전을 꺼 두면 APK와 완전히 같은 조건이 됩니다.

PC처럼 원래 가로인 화면에서는 회전하지 않습니다.
