# AIツール比較ラボ

AIツール・業務効率化ツールの比較サイト（GitHub Pagesで公開する静的HTML）。

## 公開URL
https://g-monotukun.github.io/claude-affiliate/

## A8.net サイト登録に入力する内容（例）
| 項目 | 入力例 |
|---|---|
| サイト名 | AIツール比較ラボ |
| URL | https://g-monotukun.github.io/claude-affiliate/ |
| サイトの種類 | ブログ・Webサイト |
| カテゴリ | インターネット・IT／ビジネス |
| サイト紹介文 | AIツールや業務効率化ツールを目的別に比較し、選び方・使い方を解説するサイトです。 |
| 月間PV・UU | 開設直後のため最小の選択肢 |

## 広告リンクの貼り方（A8.net）
1. A8.netの管理画面で、提携中の案件の「広告リンク作成」を開く
2. 使いたい広告（テキストまたはバナー）のHTMLをコピー
3. `links.js` の該当キー（例: `xserver`）の `` ` ` `` の間に貼り付けてコミット
4. 空のキーの広告枠は記事上に表示されない

## ページの更新方法
本文は `src/` に置き、`python3 build.py` で各ページを生成する（直接 `*.html` を編集しない）。

## 人がやること
- GitHub Pages の有効化（Settings → Pages → Branch: main / root）
- ASP登録・本人確認・口座登録
- 公開前の内容チェック
