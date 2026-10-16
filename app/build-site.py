"""공개 웹사이트(GitHub 저장소 ChwiDragon/LumenCounter → GitHub Pages) 파일 만들기 — 캐릭터 그림·글꼴 포함

  이 저장소(LumenCalculator)는 assets/를 올리지 않지만, LumenCounter 사이트는 그림·글꼴까지 넣어 스토어 앱과 같은 화면을 보여 줌.
  결과  : site/  (이 저장소에서는 git에 올리지 않음. site/ 안에 LumenCounter 저장소가 따로 들어 있음)
          - lumencalc.html, index.html, manifest.webmanifest, sw.js, .nojekyll, PRIVACY.md
          - assets/characters/*.webp|png, assets/fonts/*.woff2  (원본 글꼴 src/·권리 문서 등은 넣지 않음)
          - pwa/ 아이콘: assets/icon/app-icon.(webp|png)(캐릭터 그림 아이콘)이 있으면 그것으로, 없으면 이 저장소의 pwa/ 그대로
          - sw.js 캐시 이름 = 넣은 파일 내용의 해시 → 그림·화면이 바뀌면 설치한 앱도 새 파일을 받음
          - site/ 안에서 위 목록에 없는 파일은 지움(.git 제외)
  실행  : python app/build-site.py   (한글 글꼴은 먼저 app/make-fonts.py로 다시 만듦)
  올리기: site/ 안에서 git add -A / commit / push (LumenCounter 저장소)
"""
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
TOP_FILES = ['lumencalc.html', 'index.html', 'manifest.webmanifest', 'sw.js', '.nojekyll', 'PRIVACY.md']
ART_EXTS = {'.webp', '.png', '.jpg', '.jpeg'}
BG = (0x0A, 0x0E, 0x1A, 255)
PWA_SIZES = {'icon-192.png': 192, 'icon-512.png': 512, 'apple-touch-icon.png': 180}

SITE_README = """# 루멘 카운터 (웹)

오프라인 대전 카드게임 '루멘콘덴서'를 두 사람이 폰 한 대로 함께 쓰는 체력·토큰 계산기의 웹 버전입니다.

**바로 쓰기:** https://chwidragon.github.io/LumenCounter/

- 폰을 테이블 가운데에 가로로 눕혀 두면 왼쪽은 1P, 오른쪽은 2P 화면이 됩니다.
- 홈 화면에 앱처럼 설치할 수 있습니다. 안드로이드 크롬은 메뉴(⋮) → **앱 설치**, 아이폰 사파리는 공유 → **홈 화면에 추가**.
- 원스토어: https://m.onestore.co.kr/v2/ko-kr/app/0001010466
- 개인정보처리방침: [PRIVACY.md](PRIVACY.md)

## 저작권

- 루멘콘덴서는 야오니코믹이 개발하고 대원미디어가 유통하는 카드게임입니다. 이 앱은 플레이를 돕기 위해 만든 비공식 도구입니다.
- 캐릭터 일러스트(`assets/characters/`)의 저작권은 야오니코믹에 있으며, 허락을 받아 사용합니다. 무단 복제 · 배포를 금지합니다.
- 글꼴 Black Han Sans, IBM Plex Sans KR, Chakra Petch는 SIL OFL 1.1 라이선스입니다.
"""


def wanted():
    """사이트에 들어갈 파일: {사이트 안 경로: 원본 경로 또는 bytes}"""
    out = {name: ROOT / name for name in TOP_FILES}
    out['README.md'] = SITE_README.encode('utf-8')
    for f in sorted((ROOT / 'assets' / 'characters').iterdir()):
        if f.suffix.lower() in ART_EXTS:
            out[f'assets/characters/{f.name}'] = f
    for f in sorted((ROOT / 'assets' / 'fonts').glob('*.woff2')):
        out[f'assets/fonts/{f.name}'] = f
    icon = next((p for p in (ROOT / 'assets' / 'icon' / f'app-icon.{e}' for e in ('webp', 'png')) if p.exists()), None)
    for name, size in PWA_SIZES.items():
        if icon is None:
            out[f'pwa/{name}'] = ROOT / 'pwa' / name
            continue
        art = Image.open(icon).convert('RGBA')
        side = min(art.size)
        art = art.crop(((art.width - side) // 2, (art.height - side) // 2, (art.width + side) // 2, (art.height + side) // 2))
        canvas = Image.new('RGBA', (size, size), BG)
        canvas.alpha_composite(art.resize((size, size), Image.LANCZOS))
        tmp = ROOT / 'site-tmp' / name
        tmp.parent.mkdir(exist_ok=True)
        canvas.convert('RGB').save(tmp, optimize=True)
        out[f'pwa/{name}'] = tmp
    return out


def main():
    subprocess.run([sys.executable, str(ROOT / 'app' / 'make-fonts.py')], check=True)
    files = wanted()
    SITE.mkdir(exist_ok=True)
    data = {}
    for rel, src in files.items():
        data[rel] = src if isinstance(src, bytes) else Path(src).read_bytes()
    # 서비스 워커 캐시 이름에 내용 해시를 넣음 (sw.js 자신은 빼고 계산)
    h = hashlib.sha256()
    for rel in sorted(data):
        if rel != 'sw.js':
            h.update(rel.encode() + b'\0' + data[rel])
    sw = data['sw.js'].decode('utf-8')
    assert "const CACHE = 'lumencalc-v1';" in sw, 'sw.js 캐시 이름 줄을 찾지 못함'
    data['sw.js'] = sw.replace("const CACHE = 'lumencalc-v1';", f"const CACHE = 'lumencounter-{h.hexdigest()[:12]}';").encode('utf-8')
    # 쓰기 + 목록에 없는 파일 지우기
    for rel, b in data.items():
        dst = SITE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != b:
            dst.write_bytes(b)
    for f in sorted(SITE.rglob('*'), reverse=True):
        rel = f.relative_to(SITE).as_posix()
        if rel == '.git' or rel.startswith('.git/'):
            continue
        if f.is_file() and rel not in data:
            f.unlink()
        elif f.is_dir() and not any(f.iterdir()):
            f.rmdir()
    shutil.rmtree(ROOT / 'site-tmp', ignore_errors=True)
    total = sum(len(b) for b in data.values())
    print(f'site/: {len(data)} files, {total / 1024 / 1024:.1f} MB, cache {data["sw.js"].decode().split("const CACHE = ")[1].split(";")[0]}')


if __name__ == '__main__':
    main()
