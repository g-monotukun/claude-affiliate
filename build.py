"""src/ の原稿から、サイト全体のHTMLを生成する。

使い方: python3 build.py

原稿の先頭には次の形式でメタ情報を書く。
<!--
title: 記事タイトル
description: 検索結果やカードに出す説明文
category: カテゴリ名
icon: school | server | globe | sparkle | code
color: violet | teal | sky | amber | coral
order: 並び順（大きいほど上）
summary: この記事でわかること1|わかること2|わかること3
date: 2026-10-15
-->
src/articles/ の原稿は記事、src/ 直下の原稿は固定ページになる。
トップページ（index.html）は記事のメタ情報から自動で作られる。
広告リンクは <div class="aff" data-aff="キー"></div> と書き、links.js に登録する。
"""
import datetime
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SITE = "AIツール比較ラボ"
TAGLINE = "AIツールを、目的から選ぶ。"
SITE_DESC = "AIツール・業務効率化ツールを目的別に比較し、選び方と使い方をやさしく解説するサイトです。"

ICONS = {
    "school": '<path d="M3 9.5 12 5l9 4.5-9 4.5-9-4.5Z"/><path d="M7 11.5V16c0 1.2 2.2 2.5 5 2.5s5-1.3 5-2.5v-4.5"/><path d="M21 9.5V15"/>',
    "server": '<rect x="4" y="4" width="16" height="6.5" rx="2"/><rect x="4" y="13.5" width="16" height="6.5" rx="2"/><path d="M8 7.25h.01M8 16.75h.01M12 7.25h4M12 16.75h4"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.4 2.4 3.5 5.3 3.5 8.5s-1.1 6.1-3.5 8.5c-2.4-2.4-3.5-5.3-3.5-8.5s1.1-6.1 3.5-8.5Z"/>',
    "sparkle": '<path d="M12 3.5 13.8 9 19.5 11l-5.7 2-1.8 5.5-1.8-5.5L4.5 11l5.7-2L12 3.5Z"/><path d="M18.5 3.5v3M17 5h3"/>',
    "code": '<path d="m8.5 8-4 4 4 4M15.5 8l4 4-4 4M13.5 5.5l-3 13"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "pen": '<path d="M4 20h4L19 9l-4-4L4 16v4Z"/><path d="m13.5 6.5 4 4"/>',
}


def icon(name, size=24):
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"<!--\n(.*?)\n-->\n", text, re.S)
    if not m:
        raise SystemExit(f"{path}: 先頭にメタ情報のコメントがありません")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    meta["body"] = text[m.end():].strip()
    return meta


def jdate(s):
    d = datetime.date.fromisoformat(s)
    return f"{d.year}年{d.month}月{d.day}日"


def add_toc(body):
    """h2 に id を振り、目次のHTMLを返す。"""
    items = []

    def repl(m):
        n = len(items) + 1
        items.append(m.group(1))
        return f'<h2 id="s{n}">{m.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", repl, body)
    if len(items) < 3:
        return body, ""
    lis = "".join(f'<li><a href="#s{i}">{t}</a></li>' for i, t in enumerate(items, 1))
    return body, f'<nav class="toc" aria-label="目次"><p class="toc-title">目次</p><ol>{lis}</ol></nav>'


def wrap_tables(body):
    """スマホで表を横スクロールできるように囲む。"""
    return body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")


def reading_minutes(body):
    chars = len(re.sub(r"<[^>]+>|\s", "", body))
    return max(1, round(chars / 500))


def layout(title, description, body, p, is_home=False):
    full_title = SITE if is_home else f"{title} | {SITE}"
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="{'website' if is_home else 'article'}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@700;800&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%230f766e'/%3E%3Ctext x='16' y='21' font-size='13' font-family='sans-serif' font-weight='700' fill='white' text-anchor='middle'%3EAI%3C/text%3E%3C/svg%3E">
</head>
<body>
<div class="prbar">本サイトはアフィリエイト広告（PR）を利用しています</div>
<header class="site-header"><div class="wrap header-inner">
<a class="brand" href="{p}index.html"><span class="logo">AI</span><span class="brand-text">{SITE}<small>{TAGLINE}</small></span></a>
<nav class="gnav"><a href="{p}index.html#articles">記事一覧</a><a href="{p}about.html">運営者情報</a></nav>
</div></header>
{body}
<footer class="site-footer"><div class="wrap">
<div class="footer-brand"><span class="logo">AI</span><div><strong>{SITE}</strong><p>{SITE_DESC}</p></div></div>
<nav class="footer-nav"><a href="{p}index.html">トップ</a><a href="{p}about.html">運営者情報</a><a href="{p}privacy.html">プライバシーポリシー</a></nav>
<p class="copy">&copy; 2026 {SITE}</p>
</div></footer>
<script src="{p}links.js"></script>
</body>
</html>
"""


def card(a, p):
    return f"""<a class="card c-{a['color']}" href="{p}articles/{a['slug']}.html">
<div class="thumb">{icon(a['icon'], 44)}<span class="thumb-cat">{a['category']}</span></div>
<div class="card-body"><h3>{a['title']}</h3><p>{a['description']}</p>
<span class="card-meta">{jdate(a['date'])}<span class="more">読む →</span></span></div>
</a>"""


def build_article(a, articles):
    p = "../"
    body, toc = add_toc(wrap_tables(a["body"]))
    summary = "".join(f"<li>{icon('check', 18)}<span>{s}</span></li>" for s in a["summary"].split("|"))
    related = [r for r in articles if r["slug"] != a["slug"]]
    related.sort(key=lambda r: (r["category"] != a["category"], -int(r["order"])))
    rel_html = "".join(card(r, p) for r in related[:3])
    content = f"""<div class="article-hero c-{a['color']}"><div class="wrap narrow">
<nav class="crumbs"><a href="{p}index.html">ホーム</a><span>›</span><span>{a['category']}</span></nav>
<div class="hero-icon">{icon(a['icon'], 36)}</div>
<h1>{a['title']}</h1>
<p class="article-meta"><span class="chip">{a['category']}</span><span>{jdate(a['date'])}</span><span>約{reading_minutes(a['body'])}分で読めます</span></p>
</div></div>
<main class="wrap narrow article">
<div class="summary"><p class="summary-title">この記事でわかること</p><ul>{summary}</ul></div>
{toc}
<div class="prose">
{body}
</div>
<aside class="author">
<span class="logo big">AI</span>
<div><p class="author-name">{SITE} 編集部</p>
<p>AIツールや副業ツールを実際に試し、目的別の選び方をまとめています。記事はAIを活用して作成し、公開前に運営者が内容を確認しています。</p></div>
</aside>
</main>
<section class="related"><div class="wrap"><h2 class="section-title">あわせて読みたい</h2><div class="grid">{rel_html}</div></div></section>
"""
    return layout(a["title"], a["description"], content, p)


def build_home(articles):
    p = ""
    cats = {}
    for a in articles:
        cats.setdefault(a["category"], a)
    chips = "".join(f'<span class="cat c-{a["color"]}">{icon(a["icon"], 18)}{name}</span>' for name, a in cats.items())
    cards = "".join(card(a, p) for a in articles)
    content = f"""<section class="hero"><div class="wrap hero-inner">
<div class="hero-text">
<p class="eyebrow">{icon('sparkle', 16)} AI時代の道具選びガイド</p>
<h1>AIツールを、<br><span class="hl">目的から</span>選ぶ。</h1>
<p class="lead">文章作成、画像生成、議事録、ブログ運営まで。<br class="pc">増えすぎたAIツールの中から、あなたの目的に合うものを見つけるための比較と選び方をまとめています。</p>
<div class="cats">{chips}</div>
</div>
<div class="hero-art" aria-hidden="true">
<div class="bubble b1">{icon('pen', 30)}<span>文章</span></div>
<div class="bubble b2">{icon('sparkle', 30)}<span>画像</span></div>
<div class="bubble b3">{icon('code', 30)}<span>開発</span></div>
<div class="bubble b4">{icon('school', 30)}<span>学習</span></div>
<div class="orb"></div>
</div>
</div></section>
<section class="points"><div class="wrap points-grid">
<div class="point">{icon('check', 22)}<div><strong>目的別に整理</strong><p>やりたいことから逆算して選べます</p></div></div>
<div class="point">{icon('check', 22)}<div><strong>確認ポイントを明記</strong><p>契約前に見るべき条件をまとめています</p></div></div>
<div class="point">{icon('check', 22)}<div><strong>実践の記録</strong><p>このサイト自体もAIで作っています</p></div></div>
</div></section>
<main class="wrap" id="articles">
<h2 class="section-title">新着記事</h2>
<div class="grid">{cards}</div>
</main>
"""
    return layout(SITE, SITE_DESC, content, p, is_home=True)


def build_page(meta):
    content = f"""<div class="article-hero c-teal"><div class="wrap narrow"><h1>{meta['title']}</h1></div></div>
<main class="wrap narrow article"><div class="prose">
{wrap_tables(meta['body'])}
</div></main>
"""
    return layout(meta["title"], meta["description"], content, "")


def write(rel, text):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"built {rel}")


def main():
    articles = []
    for path in (SRC / "articles").glob("*.html"):
        a = parse(path)
        a["slug"] = path.stem
        articles.append(a)
    articles.sort(key=lambda a: (a["date"], int(a["order"])), reverse=True)

    for a in articles:
        write(f"articles/{a['slug']}.html", build_article(a, articles))
    for path in SRC.glob("*.html"):
        write(path.name, build_page(parse(path)))
    write("index.html", build_home(articles))


if __name__ == "__main__":
    main()
