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
- 記事の原稿は `src/articles/`、固定ページは `src/` に置き、`python3 build.py` で全ページを生成する（直接 `*.html` を編集しない）
- 原稿の先頭にメタ情報（タイトル・カテゴリ・アイコン・色・要約など）を書く。書き方は `build.py` 冒頭のコメント参照
- トップページの記事一覧・目次・関連記事は自動で作られる

## 人がやること
- GitHub Pages の有効化（Settings → Pages → Branch: main / root）
- ASP登録・本人確認・口座登録
- 公開前の内容チェック

## Threads 自動投稿
- 投稿の予定は `threads/queue.json`。未投稿（`posted_at` がない）ものから1日1件を選んで投稿する
- 選ぶ順番：①リンク先の記事に広告リンク登録済みの案件がある ②`season`（適した月のリスト）に今月が入っている → 通年 → 時期外 ③ queue.json の順
- 案件の有無は自動判定（記事の `data-aff` と各サイトの `links.js`）。案件を設置すれば、その記事の投稿が自動で優先される
- Threads アカウントは全サイト共通。投稿はすべてこの `threads/queue.json` で管理する
- `link` に該当サイトの記事URL（https:// から始まる完全なURL）を書くと、リンクカード付きで投稿される（500文字以内）
- `site` はどのサイトの投稿かのメモ
- `"hold": true` を付けた投稿は保留（飛ばして次を投稿）。外すと元の順番で投稿される
- 実行は GitHub Actions（`.github/workflows/threads.yml`、毎日21:17）。Actions タブから手動実行も可能
- Secrets `THREADS_ACCESS_TOKEN`（必須）と `THREADS_USER_ID`（任意）が未設定の間は、投稿せず内容を表示するだけ
- アクセストークンの有効期限は60日。期限前に作り直して Secrets を更新する
- A8.net の広告リンクを Threads に直接貼るのは、案件の「SNS掲載可」を確認してから。貼る場合は本文に「#PR」を入れる

## Search Console
`sitemap.xml` を Google Search Console に登録する（URL プレフィックス: https://g-monotukun.github.io/claude-affiliate/）
