"""threads/queue.json から投稿を選び、Threads に投稿する。

Threads アカウントは全サイト共通。1日3枠（日本時間）で、枠ごとに投稿の種類が決まっている。
  朝 7〜9時   tip      豆知識・気づき（リンクなし）
  昼 12〜14時 question 共感・問いかけ（リンクなし）
  夜 20〜23時 promo    記事の紹介（記事リンク付き）
ワークフローは1時間ごとに起動し、今が枠の中で、その枠でまだ投稿していなければ1件投稿する
（手動実行は FORCE=1 で時間帯を無視し、今の時刻に近い枠の種類で投稿する）。

queue.json の各投稿の項目:
  text         本文（500文字以内）
  kind         "tip" / "question" / "promo"（省略時は link があれば promo、なければ tip）
  theme        "ai" / "mens" / "parents"（tip・question のテーマ。季節で重みを付けて選ぶ）
  site         どのサイトの投稿かのメモ
  link         promo の記事URL（リンクカード付きで投稿）
  reply_link   tip・question に、あとから自分で返信して付ける記事URL
  reply_text   その返信の本文
  season       投稿に適した月のリスト（省略時は通年）
  hold         true なら保留

promo の選び方:
  1. リンク先の記事に、広告リンクが登録済みの案件（プログラム）がある投稿を優先
  2. 同じ条件なら、season に今月が入っている → 通年 → 時期外 の順
  3. それも同じなら queue.json に書かれた順
  案件つきの未投稿がなくなったら、時期が合い、前回から RECYCLE_DAYS 日以上たったものを再投稿する。
tip・question の選び方:
  THEME_WEIGHTS の月ごとの重みでテーマを選び、そのテーマの未投稿から season が合うものを優先する。
  なければ別のテーマ、それもなければ RECYCLE_DAYS 日以上たったものを再投稿する。
PR表記:
  記事リンクを付ける投稿（promo と、記事リンクの返信）には、本文の最後に「#PR」を自動で入れる。
返信:
  reply_link のある投稿は、投稿から REPLY_AFTER_MIN 分以上たった次の起動で、自分の投稿に返信して記事リンクを付ける。

必要な環境変数（GitHub の Secrets に登録）:
  THREADS_ACCESS_TOKEN  threads_content_publish 権限付きの長期アクセストークン
  THREADS_USER_ID       Threads のユーザーID（省略時は "me"）
DRY_RUN=1 のときは投稿せず、送る内容を表示するだけ。
"""
import datetime
import json
import os
import pathlib
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.threads.net/v1.0"
QUEUE = pathlib.Path(__file__).resolve().parent.parent / "threads" / "queue.json"
JST = datetime.timezone(datetime.timedelta(hours=9))
SLOTS = [(7, 9, "tip"), (12, 14, "question"), (20, 23, "promo")]  # 開始時〜終了時の前まで
RECYCLE_DAYS = 30
REPLY_AFTER_MIN = 40
LOW_STOCK = {"promo": 3, "tip": 3, "question": 3}
INVALID_LINK_ATTACHMENT = 4279047

# 月ごとのテーマの重み（ai, mens, parents）
THEME_WEIGHTS = {
    1: (3, 2, 2), 2: (3, 2, 1), 3: (3, 2, 1), 4: (2, 3, 1), 5: (2, 3, 2), 6: (2, 3, 2),
    7: (1, 3, 3), 8: (1, 2, 3), 9: (2, 3, 1), 10: (2, 3, 2), 11: (2, 2, 3), 12: (1, 2, 3),
}
THEMES = ("ai", "mens", "parents")


# ---- Threads API -------------------------------------------------------------

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


def publish_with_fallback(user, params, token):
    """リンクカードを付けられなかったら、URL を本文に入れて投稿し直す。"""
    try:
        return publish(user, params, token)
    except ThreadsError as e:
        if e.subcode != INVALID_LINK_ATTACHMENT or "link_attachment" not in params:
            raise
        # 公開直後のページなどで Threads がリンクカードを作れないことがある（本文の URL も自動でリンクになる）
        print(f"リンクカードを付けられなかったため、URLを本文に入れて投稿し直します: {e}")
        params = dict(params)
        link = params.pop("link_attachment")
        params["text"] = f"{params['text']}\n{link}"
        if len(params["text"]) > 500:
            raise
        return publish(user, params, token)


# ---- 案件の判定 ----------------------------------------------------------------

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
    if link not in cache:
        cache[link] = set(re.findall(r'data-aff="(\w+)"', fetch(link)))
    return bool(cache[link] & cache[base])


# ---- 投稿の選び方 --------------------------------------------------------------

def kind_of(post):
    return post.get("kind") or ("promo" if post.get("link") else "tip")


def season_rank(post, month):
    season = post.get("season")
    if not season:
        return 1  # 通年
    return 2 if month in season else 0


def posted_times(post):
    times = [post["posted_at"]] if post.get("posted_at") else []
    times += post.get("reposted_at", [])
    return [datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z").astimezone(JST) for s in times]


def recyclable(post, now):
    times = posted_times(post)
    return bool(times) and not post.get("hold") and (now - max(times)).days >= RECYCLE_DAYS


def choose_promo(queue, now, check=has_program):
    """返り値: (投稿, 再投稿か, 案件つきの未投稿の残り)"""
    cache = {}
    ranked = []
    for i, p in enumerate(queue):
        if kind_of(p) != "promo" or p.get("posted_at") or p.get("hold"):
            continue
        program = check(p.get("link"), cache)
        ranked.append(((not program, -season_rank(p, now.month), i), p))
    for key, p in sorted(ranked, key=lambda r: r[0]):
        mark = "案件あり" if not key[0] else "案件なし"
        print(f"  [{mark} / 時期{-key[1]}] {p.get('site')} {p.get('link')}")
    best = min(ranked, key=lambda r: r[0]) if ranked else None
    remaining = sum(1 for key, p in ranked if not key[0] and (best is None or p is not best[1]))
    if best is not None and not best[0][0]:
        return best[1], False, remaining
    # 案件つきの未投稿がない → 案件つきの投稿済みから、時期が合い、間があいたものを再投稿
    again = [((-season_rank(p, now.month), max(posted_times(p)), i), p)
             for i, p in enumerate(queue)
             if kind_of(p) == "promo" and recyclable(p, now) and check(p.get("link"), cache)]
    if again:
        return min(again, key=lambda r: r[0])[1], True, 0
    return (best[1] if best else None), False, 0


def pick_theme(now, slot_start):
    """月ごとの重みでテーマの順番を決める（同じ日・同じ枠なら同じ結果）。"""
    rng = random.Random(f"{now:%Y-%m-%d}-{slot_start}")
    weights = list(THEME_WEIGHTS[now.month])
    order = []
    themes = list(THEMES)
    while themes:
        t = rng.choices(themes, weights=weights)[0]
        i = themes.index(t)
        order.append(t)
        themes.pop(i)
        weights.pop(i)
    return order


def choose_daily(queue, kind, now, slot_start):
    """tip・question を選ぶ。返り値: (投稿, 再投稿か, その種類の未投稿の残り)"""
    pending = [p for p in queue if kind_of(p) == kind and not p.get("posted_at") and not p.get("hold")]
    order = pick_theme(now, slot_start)
    print(f"  テーマの順番（{now.month}月の重み）: {' → '.join(order)}")
    for theme in order:
        cands = [(-season_rank(p, now.month), i, p) for i, p in enumerate(pending) if p.get("theme") == theme]
        if cands:
            post = min(cands, key=lambda c: c[:2])[2]
            return post, False, len(pending) - 1
    if pending:
        return pending[0], False, len(pending) - 1
    again = [((-season_rank(p, now.month), max(posted_times(p))), p)
             for p in queue if kind_of(p) == kind and recyclable(p, now)]
    if again:
        return min(again, key=lambda r: r[0])[1], True, 0
    return None, False, 0


# ---- 時間帯 --------------------------------------------------------------------

def current_slot(now):
    return next((s for s in SLOTS if s[0] <= now.hour < s[1]), None)


def nearest_slot(now):
    return min(SLOTS, key=lambda s: min(abs(now.hour - s[0]), 24 - abs(now.hour - s[0])))


def already_posted_in_slot(queue, now, slot):
    start = now.replace(hour=slot[0], minute=0, second=0, microsecond=0)
    return any(start <= t <= now for p in queue for t in posted_times(p))


# ---- 在庫のお知らせ --------------------------------------------------------------

def report_stock(kind, remaining):
    """在庫が少なくなったら、GitHub Actions に知らせる（Issue 作成に使う）。"""
    names = {"promo": "記事紹介（案件つき）", "tip": "豆知識", "question": "問いかけ"}
    print(f"{names[kind]}の未投稿: 残り {remaining} 件")
    out = os.environ.get("GITHUB_OUTPUT")
    if out and remaining < LOW_STOCK[kind]:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"low_stock=true\nremaining={remaining}\nlow_kind={names[kind]}\n")


# ---- 返信（記事リンク） -----------------------------------------------------------

def latest_thread_id(post):
    ids = [post.get("thread_id")] + post.get("reposted_ids", [])
    return [i for i in ids if i][-1] if any(ids) else None


def due_reply(queue, now):
    """投稿から REPLY_AFTER_MIN 分以上たち、まだ返信していない reply_link 付きの投稿。"""
    for p in queue:
        times = posted_times(p)
        if not p.get("reply_link") or not times:
            continue
        last = max(times)
        replied = [datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z") for s in p.get("replied_at", [])]
        if any(r >= last for r in replied):
            continue
        if (now - last).total_seconds() >= REPLY_AFTER_MIN * 60 and latest_thread_id(p):
            return p
    return None


# ---- メイン --------------------------------------------------------------------

def with_pr(text):
    """記事リンク（広告のあるページ）を付ける投稿には、PR 表記を入れる（ステマ規制・広告主の規約への対応）。"""
    return text if "#PR" in text or "【PR】" in text else f"{text}\n\n#PR"


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def save(queue):
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    now = datetime.datetime.now(JST)
    dry = os.environ.get("DRY_RUN") == "1" or not os.environ.get("THREADS_ACCESS_TOKEN")
    token = os.environ.get("THREADS_ACCESS_TOKEN", "")
    user = os.environ.get("THREADS_USER_ID") or "me"

    # 1. 返信の時間になった投稿があれば、記事リンクを返信で付ける（1回の起動で1件）
    reply_post = due_reply(queue, now)
    if reply_post is not None:
        params = {"media_type": "TEXT", "reply_to_id": latest_thread_id(reply_post),
                  "text": with_pr(reply_post.get("reply_text") or "まとめた記事はこちらです👇"),
                  "link_attachment": reply_post["reply_link"]}
        if dry:
            print("[DRY RUN] 返信:", json.dumps(params, ensure_ascii=False))
        else:
            try:
                publish_with_fallback(user, params, token)
                reply_post.setdefault("replied_at", []).append(stamp())
                save(queue)
                print(f"返信で記事リンクを付けました: {reply_post['reply_link']}")
            except ThreadsError as e:
                print(f"返信に失敗しました（投稿は続けます）: {e}")

    # 2. 時間帯の確認
    if os.environ.get("FORCE") == "1":
        slot = current_slot(now) or nearest_slot(now)
    else:
        slot = current_slot(now)
        if slot is None:
            print(f"{now:%H:%M} は投稿の時間帯ではありません。")
            return
        if already_posted_in_slot(queue, now, slot):
            print(f"{slot[0]}時台の枠では投稿済みです。")
            return
    kind = slot[2]

    # 3. 投稿を選ぶ
    print(f"{slot[0]}時台の枠（{kind}）の候補:")
    if kind == "promo":
        post, recycled, remaining = choose_promo(queue, now)
    else:
        post, recycled, remaining = choose_daily(queue, kind, now, slot[0])
        if post is None:
            print("この種類の投稿がないため、記事紹介を投稿します。")
            post, recycled, remaining = choose_promo(queue, now)
            kind = "promo"
    report_stock(kind, remaining)
    if post is None:
        print("投稿できるものがありません。threads/queue.json に追加してください。")
        return
    if recycled:
        print(f"未投稿がないため、前回から{RECYCLE_DAYS}日以上たった投稿をもう一度使います。")

    text = post["text"]
    if len(text) > 500:
        sys.exit(f"500文字を超えています（{len(text)}文字）: {text[:30]}…")
    params = {"media_type": "TEXT", "text": text}
    if post.get("link"):
        if not post["link"].startswith("https://"):
            sys.exit(f"link は https:// から始まる完全なURLで書いてください: {post['link']}")
        params["link_attachment"] = post["link"]
        params["text"] = with_pr(text)
        if len(params["text"]) > 500:
            sys.exit(f"PR表記を入れると500文字を超えます（{len(params['text'])}文字）: {text[:30]}…")

    if dry:
        print("[DRY RUN] 次の内容を投稿します:")
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return

    try:
        result = publish_with_fallback(user, params, token)
    except ThreadsError as e:
        sys.exit(str(e))
    if recycled:
        post.setdefault("reposted_at", []).append(stamp())
        post.setdefault("reposted_ids", []).append(result.get("id"))
    else:
        post["posted_at"] = stamp()
        post["thread_id"] = result.get("id")
    save(queue)
    print(f"投稿しました: {result.get('id')}")


if __name__ == "__main__":
    main()
