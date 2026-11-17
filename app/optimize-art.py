"""캐릭터 그림 용량 줄이기 (build-apk.ps1 / build-aab.ps1 / build-site.py 가 빌드 때마다 실행)

  대상  : assets/characters/*.webp|png|jpg  (git에 올리지 않음)
  1) 중복 : 추가 일러스트({id}_{종류}2, 3 …)가 1번({id}_{종류})과 똑같은 파일이면 지움
            → 앱은 없는 번호를 1번으로 보여 주고, 일러스트 고르기 창에서는 그 칸을 숨김
  2) 크기 : 반신(body)은 한 변 1000px, 나머지(두상 · 특성 · 상태 · 토큰)는 512px보다 크면 줄임
            (화면에서 그보다 크게 보이는 곳이 없음 — 고해상도 폰 · 태블릿 기준)
            알파는 실제로 비치는 곳(불투명도 88% 미만)이 있을 때만 남김 (가장자리만 살짝 비치는 그림은 불투명으로)
  3) 압축 : 손실 WebP(품질 80, method 6)로 다시 저장해서 10% 이상 작아질 때만 바꿈 (크기를 줄인 그림은 항상)
            (이미 이렇게 줄인 파일은 그대로 → 여러 번 실행해도 화질이 계속 떨어지지 않음)
            png·jpg 는 같은 이름의 .webp 로 바뀜 (앱은 .webp 를 먼저 찾음)
  원본  : 지우거나 바꾸기 전 파일은 release/asset-backup/characters-orig/ 에 남김
          (같은 이름의 예전 원본은 {이름}.{날짜}.webp 로 옮겨 둠 → 그림을 교체해도 원본이 모두 남음)

  필요  : pip install pillow
  실행  : python app/optimize-art.py
"""
import io
import re
import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'assets' / 'characters'
BACKUP = ROOT / 'release' / 'asset-backup' / 'characters-orig'
EXTS = ('.webp', '.png', '.jpg', '.jpeg')
QUALITY = 80
MIN_GAIN = 0.10
MAX_SIDE = {'body': 1000}  # 종류별 최대 한 변(px). 없는 종류는 MAX_OTHER
MAX_OTHER = 512
ALPHA_MIN = 224            # 가장 투명한 곳의 알파가 이 값 이상이면 알파를 버림 (거의 안 비침)


def backup(f):
    """바꾸기 전 파일을 BACKUP/{이름}에 남김. 같은 이름의 다른 그림(예전 원본)이 이미 있으면
    그건 {이름}.{그 파일 날짜}.{확장자}로 옮겨 두고 새 원본을 남김 (그림을 교체해도 원본이 사라지지 않게)"""
    BACKUP.mkdir(parents=True, exist_ok=True)
    dst = BACKUP / f.name
    if dst.exists():
        if dst.read_bytes() == f.read_bytes():
            return
        stamp = datetime.fromtimestamp(dst.stat().st_mtime).strftime('%Y%m%d-%H%M%S')
        dst.rename(dst.with_name(f'{dst.stem}.{stamp}{dst.suffix}'))
    shutil.copy2(f, dst)


def main():
    if not ART.exists():
        print('optimize-art: assets/characters not found - skipped')
        return
    files = sorted(f for f in ART.iterdir() if f.suffix.lower() in EXTS)
    before = sum(f.stat().st_size for f in files)
    dup = shrunk = 0
    sizes_before = {f.name: (f.stat().st_size, Image.open(f).size) for f in files}

    # 1) 1번과 똑같은 추가 일러스트 지우기
    by_stem = {}
    for f in files:
        by_stem.setdefault(f.stem, f)
    for f in files:
        m = re.fullmatch(r'(.+_[a-z]+?)([2-9])', f.stem)
        first = m and by_stem.get(m.group(1))
        if first and first.read_bytes() == f.read_bytes():
            backup(f)
            f.unlink()
            dup += 1
    files = [f for f in files if f.exists()]

    # 2) 너무 큰 그림 줄이기 + 3) 손실 WebP로 다시 저장 (10% 이상 줄 때만, 줄인 그림은 항상)
    for f in files:
        rgba = Image.open(f).convert('RGBA')
        im = rgba if rgba.getextrema()[3][0] < ALPHA_MIN else rgba.convert('RGB')  # 실제로 비치는 곳이 있을 때만 알파 유지
        kind = re.sub(r'\d+$', '', f.stem.split('_', 1)[-1])
        side = MAX_SIDE.get(kind, MAX_OTHER)
        resized = max(im.size) > side
        if resized:
            im.thumbnail((side, side), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=QUALITY, method=6)
        if resized or buf.tell() < f.stat().st_size * (1 - MIN_GAIN):
            backup(f)
            f.unlink()
            f.with_suffix('.webp').write_bytes(buf.getvalue())
            shrunk += 1

    for f in sorted(ART.iterdir()):
        if f.name in sizes_before and f.stat().st_size != sizes_before[f.name][0]:
            (b, d) = sizes_before[f.name]
            print(f'  {f.name}: {d[0]}x{d[1]} {b // 1024} KB -> {Image.open(f).size[0]}px {f.stat().st_size // 1024} KB')
    after = sum(f.stat().st_size for f in ART.iterdir() if f.suffix.lower() in EXTS)
    print(f'optimize-art: {before // 1024} KB -> {after // 1024} KB (duplicates removed {dup}, re-encoded {shrunk})')


if __name__ == '__main__':
    main()
