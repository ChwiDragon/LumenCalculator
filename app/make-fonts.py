"""한글 글꼴을 앱에 쓰이는 글자만 남겨 woff2로 만듦 (build-apk.ps1 / build-aab.ps1 이 빌드 때마다 실행)

  원본  : assets/fonts/src/*.ttf  (google/fonts 저장소의 OFL 글꼴, git에 올리지 않음)
  결과  : assets/fonts/BlackHanSans-400.woff2, IBMPlexSansKR-400/600/700.woff2
  글자  : lumencalc.html 에 들어 있는 모든 글자 + 영문·숫자·기호(ASCII)
          → 캐릭터나 문구를 추가해도 다음 빌드 때 자동으로 포함됨

  필요  : pip install fonttools brotli
  실행  : python app/make-fonts.py
"""
from pathlib import Path

from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'assets' / 'fonts' / 'src'
OUT = ROOT / 'assets' / 'fonts'
FONTS = {
    'BlackHanSans-Regular.ttf': 'BlackHanSans-400.woff2',
    'IBMPlexSansKR-Regular.ttf': 'IBMPlexSansKR-400.woff2',
    'IBMPlexSansKR-SemiBold.ttf': 'IBMPlexSansKR-600.woff2',
    'IBMPlexSansKR-Bold.ttf': 'IBMPlexSansKR-700.woff2',
}


def main():
    html = (ROOT / 'lumencalc.html').read_text(encoding='utf-8')
    chars = set(html) | {chr(c) for c in range(0x20, 0x7F)}
    chars = ''.join(sorted(c for c in chars if c.isprintable()))
    for src, dst in FONTS.items():
        opts = subset.Options()
        opts.flavor = 'woff2'
        opts.layout_features = ['*']
        opts.name_IDs = ['*']
        opts.notdef_outline = True
        font = subset.load_font(str(SRC / src), opts)
        sub = subset.Subsetter(opts)
        sub.populate(text=chars)
        sub.subset(font)
        subset.save_font(font, str(OUT / dst), opts)
        print(f'{dst}: {(OUT / dst).stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
