"""캐릭터 그림 용량 줄이기 (build-apk.ps1 / build-aab.ps1 / build-site.py 가 빌드 때마다 실행)

  대상  : assets/characters/*.webp|png|jpg  (git에 올리지 않음)
  1) 중복 : 추가 일러스트({id}_{종류}2, 3 …)가 1번({id}_{종류})과 똑같은 파일이면 지움
            → 앱은 없는 번호를 1번으로 보여 주고, 일러스트 고르기 창에서는 그 칸을 숨김
  2) 압축 : 손실 WebP(품질 80, method 6)로 다시 저장해서 10% 이상 작아질 때만 바꿈
            (이미 이렇게 줄인 파일은 그대로 → 여러 번 실행해도 화질이 계속 떨어지지 않음)
            png·jpg 는 같은 이름의 .webp 로 바뀜 (앱은 .webp 를 먼저 찾음)
  원본  : 지우거나 바꾸기 전 파일은 release/asset-backup/characters-orig/ 에 남김 (이미 있으면 덮어쓰지 않음)

  필요  : pip install pillow
  실행  : python app/optimize-art.py
"""
import io
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'assets' / 'characters'
BACKUP = ROOT / 'release' / 'asset-backup' / 'characters-orig'
EXTS = ('.webp', '.png', '.jpg', '.jpeg')
QUALITY = 80
MIN_GAIN = 0.10


def backup(f):
    BACKUP.mkdir(parents=True, exist_ok=True)
    if not (BACKUP / f.name).exists():
        shutil.copy2(f, BACKUP / f.name)


def main():
    if not ART.exists():
        print('optimize-art: assets/characters not found - skipped')
        return
    files = sorted(f for f in ART.iterdir() if f.suffix.lower() in EXTS)
    before = sum(f.stat().st_size for f in files)
    dup = shrunk = 0

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

    # 2) 손실 WebP로 다시 저장 (10% 이상 줄 때만)
    for f in files:
        rgba = Image.open(f).convert('RGBA')
        im = rgba if rgba.getextrema()[3][0] < 255 else rgba.convert('RGB')  # 투명한 곳이 있을 때만 알파 유지
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=QUALITY, method=6)
        if buf.tell() < f.stat().st_size * (1 - MIN_GAIN):
            backup(f)
            f.unlink()
            f.with_suffix('.webp').write_bytes(buf.getvalue())
            shrunk += 1

    after = sum(f.stat().st_size for f in ART.iterdir() if f.suffix.lower() in EXTS)
    print(f'optimize-art: {before // 1024} KB -> {after // 1024} KB (duplicates removed {dup}, re-encoded {shrunk})')


if __name__ == '__main__':
    main()
