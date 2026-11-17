"""한글 글꼴을 앱에 쓰이는 글자만 남겨 woff2로 만듦 (build-apk.ps1 / build-aab.ps1 이 빌드 때마다 실행)

  원본  : assets/fonts/src/*.ttf  (google/fonts 저장소의 OFL 글꼴, git에 올리지 않음)
  결과  : assets/fonts/BlackHanSans-400.woff2, IBMPlexSansKR-400/600/700.woff2
  글자  : lumencalc.html 에서 화면에 나올 수 있는 글자(주석은 빼고) + 영문·숫자·기호(ASCII)
          → 캐릭터나 문구를 추가해도 다음 빌드 때 자동으로 포함됨.
            주석(<!-- -->, CSS /* */, JS // · /* */)에만 쓰인 한글은 화면에 안 나오므로 넣지 않음 (글꼴이 약 1/3 작아짐)
  주소  : lumencalc.html 의 글꼴 주소 뒤 ?v=해시 를 새 글꼴에 맞게 고침 (예전 글꼴 캐시 방지)

  필요  : pip install fonttools brotli
  실행  : python app/make-fonts.py
"""
import hashlib
import re
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


# JS에서 '/'가 나눗셈이 아니라 정규식의 시작이 되는 앞 글자 · 낱말 (그 밖에는 나눗셈)
REGEX_BEFORE = set('(,=:[!&|?{};+-*%<>~^') | {''}
REGEX_WORDS = ('return', 'typeof', 'case', 'in', 'of', 'void', 'delete', 'new')


def strip_js_comments(js):
    """JS의 // · /* */ 주석만 지움. 문자열 '…' · "…" · 템플릿 `…${…}…`(중첩 포함) · 정규식 /…/ 안의 글자는 그대로 둠"""
    out, i, n = [], 0, len(js)
    stack = []  # 템플릿 안의 ${ … } 중첩마다 그 안에서 열린 { 개수
    last = ''   # 공백이 아닌 직전 글자 (정규식인지 판단)
    while i < n:
        c = js[i]
        if stack and c == '}' and stack[-1] == 0:  # ${ … } 끝 → 다시 템플릿 글자
            stack.pop()
            out.append(c)
            i = scan_template(js, i + 1, out, stack)
            last = '`'
            continue
        if stack and c in '{}':
            stack[-1] += 1 if c == '{' else -1
        if js.startswith('//', i):
            j = js.find('\n', i)
            i = n if j < 0 else j
            continue
        if js.startswith('/*', i):
            j = js.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in '\'"':
            j = i + 1
            while j < n and js[j] != c:
                j += 2 if js[j] == '\\' else 1
            out.append(js[i:j + 1])
            i, last = j + 1, c
            continue
        if c == '`':
            out.append(c)
            i = scan_template(js, i + 1, out, stack)
            last = '`'
            continue
        if c == '/':
            word = re.search(r'([A-Za-z_$]+)\s*$', ''.join(out[-20:]))
            if last in REGEX_BEFORE or (word and word.group(1) in REGEX_WORDS):
                j, cls = i + 1, False
                while j < n and (cls or js[j] != '/'):
                    if js[j] == '\\':
                        j += 1
                    elif js[j] == '[':
                        cls = True
                    elif js[j] == ']':
                        cls = False
                    j += 1
                out.append(js[i:j + 1])
                i, last = j + 1, '/'
                continue
        out.append(c)
        if not c.isspace():
            last = c
        i += 1
    return ''.join(out)


def scan_template(js, i, out, stack):
    """템플릿 글자를 ` 또는 ${ 까지 그대로 옮기고 그 다음 위치를 돌려줌. ${ 를 만나면 중첩 단계를 하나 쌓음"""
    n = len(js)
    while i < n:
        if js[i] == '\\':
            out.append(js[i:i + 2])
            i += 2
        elif js[i] == '`':
            out.append('`')
            return i + 1
        elif js.startswith('${', i):
            out.append('${')
            stack.append(0)
            return i + 2
        else:
            out.append(js[i])
            i += 1
    return i


def visible_text(html):
    """화면에 나올 수 있는 글자만: HTML 주석, <style>의 /* */, <script>의 JS 주석을 뺀 나머지"""
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    html = re.sub(r'(<style>)(.*?)(</style>)', lambda m: m[1] + re.sub(r'/\*.*?\*/', '', m[2], flags=re.S) + m[3], html, flags=re.S)
    return re.sub(r'(<script>)(.*?)(</script>)', lambda m: m[1] + strip_js_comments(m[2]) + m[3], html, flags=re.S)


def main():
    html = visible_text((ROOT / 'lumencalc.html').read_text(encoding='utf-8'))
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
    stamp_urls()


def stamp_urls():
    """lumencalc.html 의 글꼴 주소에 파일 내용 해시(?v=)를 붙임.
    글자가 늘어 글꼴이 바뀌면 주소도 바뀌어서, 브라우저가 예전 글꼴(새 글자 없음)을 캐시에서 꺼내 쓰지 않음"""
    path = ROOT / 'lumencalc.html'
    html = path.read_text(encoding='utf-8')
    for dst in FONTS.values():
        v = hashlib.sha256((OUT / dst).read_bytes()).hexdigest()[:8]
        html = re.sub(rf'(assets/fonts/{re.escape(dst)})(\?v=[0-9a-f]+)?', rf'\g<1>?v={v}', html)
    path.write_text(html, encoding='utf-8', newline='')


if __name__ == '__main__':
    main()
