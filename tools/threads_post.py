"""threads/queue.json の未投稿の投稿から1件を選び、Threads に投稿する。

選ぶ順番:
  1. リンク先の記事に、広告リンクが登録済みの案件（プログラム）がある投稿を優先
  2. 同じ条件なら、"season"（投稿に適した月のリスト）に今月（日本時間）が入っている投稿 →
     "season" がない通年の投稿 → 時期外の投稿 の順
  3. それも同じなら queue.json に書かれた順
案件の有無は、記事ページの data-aff と、そのサイトの links.js に登録されたリンクから判定する。

Threads アカウントは全サイト共通。link には投稿内容に対応するサイトの記事URLを完全な形で書く。

必要な環境変数（GitHub の Secrets に登録）:
  THREADS_ACCESS_TOKEN  threads_content_publish 権限付きの長期アクセストークン
  THREADS_USER_ID       Threads のユーザーID（省略時は "me"）
"hold": true の投稿は保留として飛ばす（順番は保ったまま、あとで外せば投稿される）。
DRY_RUN=1 のときは投稿せず、送る内容を表示するだけ。
"""
import datetime
import json
import re
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.threads.net/v1.0"
QUEUE = pathlib.Path(__file__).resolve().parent.parent / "threads" / "queue.json"


INVALID_LINK_ATTACHMENT = 4279047


class ThreadsError(Exception):
    def __init__(self, code, body):
        super().__init__(f"Threads API エラー（HTTP {code}）: {body}")
        try:
            self.subcode = json.loads(body)["error"].get("error_subcode")
        except (ValueError, KeyError, TypeError):
            self.subcode = None


def call(path, params):
    data = urllib.parse.urlencode(params).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(f"{API}/{path}", data=data), timeout=30) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        # Threads API はエラーの理由を本文の JSON で返す
        raise ThreadsError(e.code, e.read().decode("utf-8", "replace")) from None


def publish(user, params, token):
    container = call(f"{user}/threads", {**params, "access_token": token})["id"]
    time.sleep(10)  # コンテナの準備を待つ
    return call(f"{user}/threads_publish", {"creation_id": container, "access_token": token})


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as res:
            return res.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"取得できませんでした（案件なしとして扱います）: {url} {e}")
        return ""


def has_program(link, cache):
    """記事ページに、links.js でリンクが登録済みの広告枠があるか。"""
    if not link or "/articles/" not in link:
        return False
    base = link.split("/articles/")[0] + "/"
    if base not in cache:
        js = fetch(base + "links.js")
        cache[base] = {k for k, v in re.findall(r"(\w+):\s*`([^`]*)`", js) if v.strip()}
    keys = set(re.findall(r'data-aff="(\w+)"', fetch(link)))
    return bool(keys & cache[base])


def season_rank(post, month):
    season = post.get("season")
    if not season:
        return 1  # 通年
    return 2 if month in season else 0


def choose(queue, month, check=has_program):
    cache = {}
    ranked = []
    for i, p in enumerate(queue):
        if p.get("posted_at") or p.get("hold"):
            continue
        program = check(p.get("link"), cache)
        ranked.append(((not program, -season_rank(p, month), i), p))
    for key, p in sorted(ranked, key=lambda r: r[0]):
        mark = "案件あり" if not key[0] else "案件なし"
        print(f"  [{mark} / 時期{-key[1]}] {p.get('site')} {p.get('link') or '(リンクなし)'}")
    if not ranked:
        return None, 0
    chosen = min(ranked, key=lambda r: r[0])
    # 今回の投稿を除いた、案件つきの未投稿の数
    remaining = sum(1 for key, p in ranked if not key[0] and p is not chosen[1])
    return chosen[1], remaining


LOW_STOCK = 3


def report_stock(remaining):
    """案件つきの未投稿が少なくなったら、GitHub Actions に知らせる（Issue 作成に使う）。"""
    print(f"案件つきの未投稿: 残り {remaining} 件")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"remaining={remaining}\nlow_stock={'true' if remaining < LOW_STOCK else 'false'}\n")


def main():
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    month = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).month
    print(f"候補（上から優先、{month}月）:")
    post, remaining = choose(queue, month)
    report_stock(remaining)
    if post is None:
        print("未投稿の投稿がありません。threads/queue.json に追加してください。")
        return
    text = post["text"]
    if len(text) > 500:
        sys.exit(f"500文字を超えています（{len(text)}文字）: {text[:30]}…")
    params = {"media_type": "TEXT", "text": text}
    if post.get("link"):
        if not post["link"].startswith("https://"):
            sys.exit(f"link は https:// から始まる完全なURLで書いてください: {post['link']}")
        params["link_attachment"] = post["link"]

    if os.environ.get("DRY_RUN") == "1" or not os.environ.get("THREADS_ACCESS_TOKEN"):
        print("[DRY RUN] 次の内容を投稿します:")
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return

    token = os.environ["THREADS_ACCESS_TOKEN"]
    user = os.environ.get("THREADS_USER_ID") or "me"
    try:
        try:
            result = publish(user, params, token)
        except ThreadsError as e:
            if e.subcode != INVALID_LINK_ATTACHMENT or "link_attachment" not in params:
                raise
            # 公開直後のページなどで Threads がリンクカードを作れないことがある。
            # その場合はカードなしで、URL を本文に書いて投稿し直す（本文の URL も自動でリンクになる）
            print(f"リンクカードを付けられなかったため、URLを本文に入れて投稿し直します: {e}")
            link = params.pop("link_attachment")
            params["text"] = f"{params['text']}\n{link}"
            if len(params["text"]) > 500:
                raise
            result = publish(user, params, token)
    except ThreadsError as e:
        sys.exit(str(e))
    post["posted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    post["thread_id"] = result.get("id")
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"投稿しました: {post['thread_id']}")


if __name__ == "__main__":
    main()
