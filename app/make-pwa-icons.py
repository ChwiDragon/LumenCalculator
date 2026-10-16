"""웹(GitHub Pages) 홈 화면 설치(PWA)용 아이콘 만들기

  원본  : app/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_foreground.png (금색 마름모, 캐릭터 그림 없음)
          + 뒤 색 #0A0E1A (ic_launcher_background.xml 과 같음)
  결과  : pwa/icon-192.png, pwa/icon-512.png      (manifest.webmanifest, purpose any·maskable 겸용: 꽉 찬 정사각형)
          pwa/apple-touch-icon.png (180)           (아이폰 홈 화면. 모서리는 iOS가 둥글게 깎음)
  적응형 아이콘 앞 레이어는 108dp 칸 가운데 안전 영역에 마름모가 있어서, 꽉 찬 정사각형으로 깔면
  PWA maskable 안전 영역(가운데 80% 원) 안에도 들어감.

  실행  : python app/make-pwa-icons.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FG = ROOT / 'app' / 'android' / 'app' / 'src' / 'main' / 'res' / 'mipmap-xxxhdpi' / 'ic_launcher_foreground.png'
OUT = ROOT / 'pwa'
BG = (0x0A, 0x0E, 0x1A, 255)
SIZES = {'icon-192.png': 192, 'icon-512.png': 512, 'apple-touch-icon.png': 180}


def main():
    fg = Image.open(FG).convert('RGBA')
    OUT.mkdir(exist_ok=True)
    for name, size in SIZES.items():
        icon = Image.new('RGBA', (size, size), BG)
        icon.alpha_composite(fg.resize((size, size), Image.LANCZOS))
        icon.convert('RGB').save(OUT / name, optimize=True)
        print(f'{name}: {size}x{size}')


if __name__ == '__main__':
    main()
