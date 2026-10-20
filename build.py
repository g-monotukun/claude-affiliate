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
import hashlib
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SITE = "AIツール比較ラボ"
TAGLINE = "AIツールを、目的から選ぶ。"
BASE_URL = "https://g-monotukun.github.io/claude-affiliate/"
# Google Search Console の所有権確認用
GSC_META = '\n<meta name="google-site-verification" content="g2Jn0JbKjPQR9hn0YPAHpSJyRZgExQNaeE51vIjmieE">'
SITE_DESC = "AIツール・業務効率化ツールを目的別に比較し、選び方と使い方をやさしく解説するサイトです。"

ICONS = {
    "school": '<path d="M3 9.5 12 5l9 4.5-9 4.5-9-4.5Z"/><path d="M7 11.5V16c0 1.2 2.2 2.5 5 2.5s5-1.3 5-2.5v-4.5"/><path d="M21 9.5V15"/>',
    "server": '<rect x="4" y="4" width="16" height="6.5" rx="2"/><rect x="4" y="13.5" width="16" height="6.5" rx="2"/><path d="M8 7.25h.01M8 16.75h.01M12 7.25h4M12 16.75h4"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.4 2.4 3.5 5.3 3.5 8.5s-1.1 6.1-3.5 8.5c-2.4-2.4-3.5-5.3-3.5-8.5s1.1-6.1 3.5-8.5Z"/>',
    "sparkle": '<path d="M12 3.5 13.8 9 19.5 11l-5.7 2-1.8 5.5-1.8-5.5L4.5 11l5.7-2L12 3.5Z"/><path d="M18.5 3.5v3M17 5h3"/>',
    "code": '<path d="m8.5 8-4 4 4 4M15.5 8l4 4-4 4M13.5 5.5l-3 13"/>',
    "receipt": '<path d="M6 3.5h12v17l-2.5-1.5-2 1.5-1.5-1.5-1.5 1.5-2-1.5L6 20.5v-17Z"/><path d="M9 8h6M9 11.5h6M9 15h3.5"/>',
    "video": '<rect x="3.5" y="6" width="12.5" height="12" rx="2.5"/><path d="m16 10.5 4.5-2.5v8L16 13.5"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "pen": '<path d="M4 20h4L19 9l-4-4L4 16v4Z"/><path d="m13.5 6.5 4 4"/>',
}


def version(name):
    """ファイル内容のハッシュ。URLに付けて、更新時にブラウザのキャッシュを無効にする。"""
    return hashlib.md5((ROOT / name).read_bytes()).hexdigest()[:8]


# 広告キーごとの商品紹介。記事中の <div class="aff" data-aff="キー"></div> が商品ボックスになる。
# テキストリンクは links.js の「キー_text」に登録するとボタンとして表示される。
PRODUCTS = {
    "freee": dict(
        name="freee会計", color="amber", icon="receipt", badge="クラウド会計ソフト",
        tagline="日々の記帳から確定申告の書類作成まで、クラウドでまとめて進められる",
        points=["銀行口座やクレジットカードと連携して取引を取り込める", "質問に答えながら確定申告の書類を作成できる", "パソコンでもスマートフォンでも使える"],
        article="side-job-tax-return"),
    "moneyforward": dict(
        name="マネーフォワード クラウド確定申告", color="sky", icon="receipt", badge="確定申告ソフト",
        tagline="初めての人でも、画面の案内に沿って確定申告の準備を進められる",
        points=["銀行口座やクレジットカードの明細を自動で取り込める", "確定申告の書類作成まで進められる", "スマートフォンのアプリからも使える"],
        article="side-job-tax-return"),
    "xserver": dict(
        name="エックスサーバー", color="sky", icon="server", badge="定番レンタルサーバー",
        tagline="長く使われている国内の定番。困ったときに情報が見つけやすい",
        points=["申込みと同時にWordPressを設定できる機能がある", "利用者が多く、設定方法の解説記事が豊富", "ブログから法人サイトまで幅広く使われている"],
        article="rental-server-choice"),
    "flexclip": dict(
        name="FlexClip", color="violet", icon="video", badge="無料で始められる動画編集",
        tagline="パソコンのブラウザだけで使える、オンラインの動画編集ツール",
        points=["ソフトのインストールが不要で、ブラウザから使える", "無料プランから試せる（機能や書き出しには制限がある場合あり）", "テンプレートを使って短い動画を作りやすい"],
        article="online-video-editor"),
    "jetboy": dict(
        name="JETBOY", color="coral", icon="server", badge="低価格から始められる",
        tagline="月額500円から使えるプランがある、クラウド型のSSDレンタルサーバー",
        points=["費用を抑えてブログを始めたい人向けのプランがある", "データの保存にSSDを採用", "必要に応じて上位プランに切り替えられる"],
        article="rental-server-choice"),
    "conoha_wing": dict(
        name="ConoHa WING", color="teal", icon="server", badge="サーバー＋ドメインを一括",
        tagline="サーバーとドメインをまとめて申し込めるWINGパックが特徴",
        points=["WINGパックでサーバーとドメインの手続きを一度に", "管理画面が分かりやすいと評判", "WordPressブログを始めたい初心者に人気"],
        article="rental-server-choice"),
    "onamae": dict(
        name="お名前.com", color="violet", icon="globe", badge="独自ドメイン",
        tagline="国内で広く使われているドメイン登録サービス",
        points=[".com や .net など定番のドメインを取得できる", "時期によってキャンペーン価格で取得できる", "GitHub Pagesのサイトにも独自ドメインを設定できる"],
        article="need-own-domain"),
    "dmm_ai_camp": dict(
        name="DMM 生成AI CAMP", color="coral", icon="school", badge="生成AIスクール",
        tagline="職種別のコースで、仕事に生かせる生成AIスキルを学べる",
        points=["営業・マーケティングなど職種別にコースを用意", "受講前に無料カウンセリングで相談できる", "条件を満たすと補助金の対象になるコースもある"],
        article="ai-school-checklist"),
}


def product_box(key, p, with_banner=True):
    pr = PRODUCTS[key]
    pts = "".join(f"<li>{icon('check', 16)}<span>{s}</span></li>" for s in pr["points"])
    banner = f'<div class="aff" data-aff="{key}"></div>' if with_banner else ""
    more = "" if with_banner else f'<a class="btn ghost" href="{p}articles/{pr["article"]}.html">解説記事を読む</a>'
    return f"""<div class="product c-{pr['color']}" id="p-{key}">
<span class="product-pr">PR</span>
<div class="product-head"><span class="product-icon">{icon(pr['icon'], 28)}</span>
<div><span class="product-badge">{pr['badge']}</span><p class="product-name">{pr['name']}</p></div></div>
<p class="product-tagline">{pr['tagline']}</p>
<ul class="product-points">{pts}</ul>
{banner}<div class="product-actions"><span class="aff-btn" data-aff="{key}_text"></span>{more}</div>
</div>"""


def products_in(body, p):
    return re.sub(r'<div class="aff" data-aff="([a-z_]+)"></div>',
                  lambda m: product_box(m.group(1), p) if m.group(1) in PRODUCTS else m.group(0), body)


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


def layout(title, description, body, p, is_home=False, path="", head=""):
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
<meta property="og:url" content="{BASE_URL}{path}">
<link rel="canonical" href="{BASE_URL}{path}">{GSC_META if is_home else ""}{head}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@700;800&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}style.css?v={version('style.css')}">
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
<script src="{p}links.js?v={version('links.js')}"></script>
</body>
</html>
"""


def card(a, p):
    return f"""<a class="card c-{a['color']}" href="{p}articles/{a['slug']}.html">
<div class="thumb">{icon(a['icon'], 44)}<span class="thumb-cat">{a['category']}</span></div>
<div class="card-body"><h3>{a['title']}</h3><p>{a['description']}</p>
<span class="card-meta">{jdate(a['date'])}<span class="more">読む →</span></span></div>
</a>"""


def quick_compare(body):
    """記事に登場する商品の早見表。各行から商品ボックスへ移動できる。"""
    keys = [k for k in dict.fromkeys(re.findall(r'data-aff="([a-z_]+)"', body)) if k in PRODUCTS]
    if len(keys) < 2:
        return ""
    rows = "".join(
        f'<tr><th><span class="qc-name c-{PRODUCTS[k]["color"]}">{PRODUCTS[k]["name"]}</span></th>'
        f'<td>{PRODUCTS[k]["tagline"]}</td><td><a class="qc-go" href="#p-{k}">詳しく見る ↓</a></td></tr>'
        for k in keys)
    return (f'<div class="quick"><p class="quick-title">{icon("sparkle", 18)} この記事で紹介するサービス</p>'
            f'<div class="table-wrap"><table><tr><th>サービス</th><th>特徴</th><th></th></tr>{rows}</table></div></div>')


def faq_parts(a):
    if not a.get("faq"):
        return "", ""
    qa = [item.split("::", 1) for item in a["faq"].split("||")]
    items = "".join(f'<details class="faq-item"><summary>{q}</summary><p>{ans}</p></details>' for q, ans in qa)
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in qa]}
    return (f'<h2>よくある質問</h2><div class="faq">{items}</div>',
            f'\n<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>')


def build_article(a, articles):
    p = "../"
    faq_html, faq_ld = faq_parts(a)
    body, toc = add_toc(products_in(wrap_tables(a["body"] + faq_html), p))
    updated = a.get("updated", a["date"])
    dates = f'<span>公開 {jdate(a["date"])}</span>' + (f'<span>更新 {jdate(updated)}</span>' if updated != a["date"] else "")
    conclusion = (f'<div class="conclusion"><p class="conclusion-title">結論</p><p>{a["conclusion"]}</p></div>'
                  if a.get("conclusion") else "")
    article_ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
                  "description": a["description"], "datePublished": a["date"], "dateModified": updated,
                  "author": {"@type": "Organization", "name": f"{SITE} 編集部", "url": BASE_URL + "about.html"},
                  "mainEntityOfPage": f"{BASE_URL}articles/{a['slug']}.html"}
    head = f'\n<script type="application/ld+json">{json.dumps(article_ld, ensure_ascii=False)}</script>{faq_ld}'
    summary = "".join(f"<li>{icon('check', 18)}<span>{s}</span></li>" for s in a["summary"].split("|"))
    related = [r for r in articles if r["slug"] != a["slug"]]
    related.sort(key=lambda r: (r["category"] != a["category"], -int(r["order"])))
    rel_html = "".join(card(r, p) for r in related[:3])
    content = f"""<div class="article-hero c-{a['color']}"><div class="wrap narrow">
<nav class="crumbs"><a href="{p}index.html">ホーム</a><span>›</span><span>{a['category']}</span></nav>
<div class="hero-icon">{icon(a['icon'], 36)}</div>
<h1>{a['title']}</h1>
<p class="article-meta"><span class="chip">{a['category']}</span>{dates}<span>約{reading_minutes(a['body'])}分で読めます</span></p>
</div></div>
<main class="wrap narrow article">
{conclusion}
<div class="summary"><p class="summary-title">この記事でわかること</p><ul>{summary}</ul></div>
{quick_compare(a["body"])}
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
    return layout(a["title"], a["description"], content, p, path=f"articles/{a['slug']}.html", head=head)


GOALS = [
    ("ブログを始めたい", "サーバーの選び方", "rental-server-choice", "server", "teal"),
    ("副業の確定申告が不安", "確定申告の基本", "side-job-tax-return", "receipt", "amber"),
    ("AIを仕事で使えるようになりたい", "スクールの選び方", "ai-school-checklist", "school", "coral"),
    ("自分に合うAIツールを知りたい", "ツールの選び方", "how-to-choose-ai-tools", "sparkle", "amber"),
    ("独自ドメインがほしい", "ドメインの基礎", "need-own-domain", "globe", "violet"),
]


def build_home(articles):
    p = ""
    goals = "".join(
        f'<a class="goal c-{c}" href="articles/{slug}.html"><span class="goal-icon">{icon(ic, 26)}</span>'
        f'<span class="goal-text"><strong>{q}</strong><small>{sub} →</small></span></a>'
        for q, sub, slug, ic, c in GOALS)
    products = "".join(product_box(k, p, with_banner=False) for k in PRODUCTS)
    cards = "".join(card(a, p) for a in articles)
    content = f"""<section class="hero"><div class="wrap hero-inner">
<div class="hero-text">
<p class="eyebrow">{icon('sparkle', 16)} AI時代の道具選びガイド</p>
<h1>AIツールを、<br><span class="hl">目的から</span>選ぶ。</h1>
<p class="lead">文章作成、画像生成、ブログ運営、AIの学び方まで。<br class="pc">増えすぎたツールの中から、あなたに合うものが見つかるように、選び方と確認ポイントをまとめています。</p>
<div class="hero-cta"><a class="btn" href="#goals">目的から探す</a><a class="btn ghost" href="#picks">おすすめサービスを見る</a></div>
</div>
<div class="goal-panel" id="goals">
<p class="goal-title">{icon('sparkle', 18)} あなたの目的は？</p>
{goals}
</div>
</div></section>
<section class="points"><div class="wrap points-grid">
<div class="point">{icon('check', 22)}<div><strong>目的別に整理</strong><p>やりたいことから逆算して選べます</p></div></div>
<div class="point">{icon('check', 22)}<div><strong>確認ポイントを明記</strong><p>契約前に見るべき条件をまとめています</p></div></div>
<div class="point">{icon('check', 22)}<div><strong>実践の記録</strong><p>このサイト自体もAIで作っています</p></div></div>
</div></section>
<section class="wrap" id="picks">
<h2 class="section-title">編集部おすすめのサービス</h2>
<p class="section-lead">このサイトの運営や記事づくりの中で調べた、目的別のおすすめです。</p>
<div class="products">{products}</div>
</section>
<main class="wrap" id="articles">
<h2 class="section-title">新着記事</h2>
<div class="grid">{cards}</div>
</main>
<section class="wrap"><div class="cta-band">
<div><p class="cta-title">まずは「何をしたいか」から。</p><p>目的が決まれば、選ぶべきツールは自然に絞れます。</p></div>
<a class="btn light" href="#goals">目的から探す</a>
</div></section>
"""
    return layout(SITE, SITE_DESC, content, p, is_home=True)


def build_page(meta):
    content = f"""<div class="article-hero c-teal"><div class="wrap narrow"><h1>{meta['title']}</h1></div></div>
<main class="wrap narrow article"><div class="prose">
{wrap_tables(meta['body'])}
</div></main>
"""
    return layout(meta["title"], meta["description"], content, "", path=meta["slug"] + ".html")


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
    pages = []
    for path in SRC.glob("*.html"):
        meta = parse(path)
        meta["slug"] = path.stem
        pages.append(path.stem + ".html")
        write(path.name, build_page(meta))
    write("index.html", build_home(articles))

    urls = [("", max(a.get("updated", a["date"]) for a in articles))]
    urls += [(f"articles/{a['slug']}.html", a.get("updated", a["date"])) for a in articles]
    urls += [(pg, None) for pg in sorted(pages)]
    entries = "".join(f"<url><loc>{BASE_URL}{u}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>\n"
                      for u, d in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n'
                         f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n')


if __name__ == "__main__":
    main()
