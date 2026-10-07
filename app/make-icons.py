"""캐릭터 그림 앱 아이콘 만들기 (릴리즈 APK·AAB 전용, build-apk.ps1 / build-aab.ps1 이 실행)

  원본  : assets/icon/app-icon.webp (또는 .png) — 정사각형 그림. assets/ 라 GitHub에 올라가지 않음
  결과  : app/android/app/src/art/res/  (git에 올리지 않음)
          - mipmap-*/ic_launcher.png, ic_launcher_round.png  : 예전 안드로이드용 (둥근 네모 / 원)
          - mipmap-*/ic_launcher_foreground.png               : 적응형 아이콘 앞 레이어 (108dp 칸 가운데 84dp 크기)
          - values/ic_launcher_background.xml                 : 적응형 아이콘 뒤 색 = 그림 위쪽 가장자리 색
  빌드 때 -PwithArt 로 이 폴더가 release 리소스에 겹쳐져 기본(금색 마름모) 아이콘을 덮음.
  GitHub용 APK는 -PwithArt 없이 빌드되므로 그림 아이콘이 들어가지 않음.

  실행  : python app/make-icons.py   (원본이 없으면 아무것도 하지 않음)
"""
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = next((p for p in (ROOT / 'assets' / 'icon' / f'app-icon.{e}' for e in ('webp', 'png')) if p.exists()), None)
OUT = ROOT / 'app' / 'android' / 'app' / 'src' / 'art' / 'res'
DENSITIES = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}


def rounded(img, radius_ratio):
    s = img.size[0]
    mask = Image.new('L', (s * 4, s * 4), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s * 4 - 1, s * 4 - 1], radius=int(s * 4 * radius_ratio), fill=255)
    out = img.convert('RGBA')
    out.putalpha(mask.resize((s, s), Image.LANCZOS))
    return out


def main():
    if SRC is None:
        print('make-icons: assets/icon/app-icon.(webp|png) not found - skipped')
        return
    art = Image.open(SRC).convert('RGB')
    side = min(art.size)
    art = art.crop(((art.width - side) // 2, (art.height - side) // 2, (art.width + side) // 2, (art.height + side) // 2))
    # 뒤 색: 위쪽 가장자리 픽셀의 중간값
    top = sorted(art.getpixel((x, 0)) for x in range(0, side, max(1, side // 64)))
    bg = top[len(top) // 2]
    if OUT.exists():
        shutil.rmtree(OUT)
    for name, k in DENSITIES.items():
        d = OUT / f'mipmap-{name}'
        d.mkdir(parents=True)
        legacy = round(48 * k)
        rounded(art.resize((legacy, legacy), Image.LANCZOS), .18).save(d / 'ic_launcher.png')
        rounded(art.resize((legacy, legacy), Image.LANCZOS), .5).save(d / 'ic_launcher_round.png')
        canvas, inner = round(108 * k), round(84 * k)
        fg = Image.new('RGBA', (canvas, canvas), (0, 0, 0, 0))
        fg.paste(art.resize((inner, inner), Image.LANCZOS), ((canvas - inner) // 2,) * 2)
        fg.save(d / 'ic_launcher_foreground.png')
    (OUT / 'values').mkdir(parents=True)
    (OUT / 'values' / 'ic_launcher_background.xml').write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        f'    <color name="ic_launcher_background">#{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}</color>\n</resources>\n', encoding='utf-8')
    print(f'make-icons: {SRC.name} -> {OUT} (background #{bg[0]:02X}{bg[1]:02X}{bg[2]:02X})')


if __name__ == '__main__':
    main()
