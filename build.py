"""src/ の本文から、共通のヘッダー・PR表記・フッター付きのページを生成する。

使い方: python3 build.py
本文ファイルの1行目に <!-- title: ページタイトル --> を書く。
広告リンクは <div class="aff" data-aff="キー"></div> と書き、links.js に登録する。
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
SITE = "AIツール比較ラボ"

TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="AIツール・業務効率化ツールを目的別に比較し、選び方を解説するサイトです。">
<link rel="stylesheet" href="{p}style.css">
</head>
<body>
<header><div class="wrap">
<a class="brand" href="{p}index.html">{site}</a>
<nav><a href="{p}index.html">記事一覧</a><a href="{p}about.html">運営者情報</a><a href="{p}privacy.html">プライバシーポリシー</a></nav>
</div></header>
<main class="wrap">
<p class="pr">本サイトはアフィリエイト広告（PR）を利用しています。</p>
{body}
</main>
<footer><div class="wrap">&copy; 2026 {site}</div></footer>
<script src="{p}links.js"></script>
</body>
</html>
"""


def main():
    for src in sorted(SRC.rglob("*.html")):
        rel = src.relative_to(SRC)
        text = src.read_text(encoding="utf-8")
        m = re.match(r"<!-- title: (.*?) -->\n", text)
        if not m:
            raise SystemExit(f"{rel}: 1行目に <!-- title: ... --> がありません")
        body = text[m.end():].strip()
        p = "../" * (len(rel.parts) - 1)
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(TEMPLATE.format(title=m.group(1), body=body, p=p, site=SITE), encoding="utf-8")
        print(f"built {rel}")


if __name__ == "__main__":
    main()
