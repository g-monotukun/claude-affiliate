"""Threads の投稿ごとの閲覧数・反応を取得して、threads/insights.md にまとめる。

threads/queue.json に記録された投稿ID（thread_id・reposted_ids）について、
Threads API の insights（views / likes / replies / reposts / quotes / shares）を取得する。
アカウント全体のフォロワー数も取得する（取れなければ省略）。

必要な環境変数: THREADS_ACCESS_TOKEN（threads_manage_insights 権限付き）、THREADS_USER_ID（省略時 "me"）
"""
import collections
import datetime
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.threads.net/v1.0"
ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = ROOT / "threads" / "queue.json"
OUT_JSON = ROOT / "threads" / "insights.json"
OUT_MD = ROOT / "threads" / "insights.md"
JST = datetime.timezone(datetime.timedelta(hours=9))
METRICS = ["views", "likes", "replies", "reposts", "quotes", "shares"]
SITE_THEMES = {"claude-affiliate": "ai", "mens-care-lab": "mens", "parents-consultation": "parents"}
THEME_NAMES = {"ai": "AI", "mens": "メンズ", "parents": "実家"}
KIND_NAMES = {"tip": "豆知識", "question": "質問", "promo": "紹介"}
TAG_START = datetime.datetime(2026, 11, 17, tzinfo=JST)  # トピックタグ・リンク返信方式に変えた日


def get(path, params):
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode("utf-8", "replace"), "status": e.code}


def value_of(item):
    if "total_value" in item:
        return item["total_value"].get("value")
    vals = item.get("values") or []
    return vals[-1].get("value") if vals else None


def theme_of(p):
    if p.get("theme"):
        return p["theme"]
    for site, theme in SITE_THEMES.items():
        if f"/{site}/" in (p.get("link") or p.get("reply_link") or ""):
            return theme
    return "?"


def kind_of(p):
    return p.get("kind") or ("promo" if p.get("link") else "tip")


def parse(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z").astimezone(JST)


def main():
    token = os.environ["THREADS_ACCESS_TOKEN"]
    user = os.environ.get("THREADS_USER_ID") or "me"
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))

    rows, errors = [], []
    for p in queue:
        pairs = []
        if p.get("thread_id") and p.get("posted_at"):
            pairs.append((p["thread_id"], p["posted_at"]))
        pairs += list(zip(p.get("reposted_ids", []), p.get("reposted_at", [])))
        for tid, at in pairs:
            if not tid:
                continue
            res = get(f"{tid}/insights", {"metric": ",".join(METRICS), "access_token": token})
            if "error" in res:
                errors.append(f"{tid}: {res['error'][:200]}")
                continue
            m = {d["name"]: value_of(d) for d in res.get("data", [])}
            rows.append({"id": tid, "posted_at": at, "kind": kind_of(p), "theme": theme_of(p),
                         "text": p["text"].split("\n")[0][:40], **{k: m.get(k) or 0 for k in METRICS}})

    account = {}
    res = get(f"{user}/threads_insights", {"metric": "followers_count", "access_token": token})
    if "error" not in res:
        account = {d["name"]: value_of(d) for d in res.get("data", [])}

    now = datetime.datetime.now(JST)
    OUT_JSON.write_text(json.dumps({"fetched_at": now.isoformat(), "account": account, "posts": rows,
                                    "errors": errors}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def avg(group):
        g = [r["views"] for r in group]
        return round(sum(g) / len(g), 1) if g else 0

    def eng(r):
        return r["likes"] + r["replies"] + r["reposts"] + r["quotes"]

    lines = [f"# Threads 投稿の反応（{now:%Y-%m-%d %H:%M} 時点）", ""]
    if account.get("followers_count") is not None:
        lines += [f"フォロワー数: {account['followers_count']}", ""]
    total = sum(r["views"] for r in rows)
    lines += [f"取得できた投稿: {len(rows)} 件 / 閲覧数の合計: {total} / 1投稿あたり平均: {avg(rows)}", ""]

    for title, key, names in [("種類別", "kind", KIND_NAMES), ("テーマ別", "theme", THEME_NAMES)]:
        lines += [f"## {title}の平均閲覧数", "", "| | 件数 | 平均閲覧 | 平均反応 |", "|---|---|---|---|"]
        groups = collections.defaultdict(list)
        for r in rows:
            groups[r[key]].append(r)
        for k, g in sorted(groups.items(), key=lambda x: -avg(x[1])):
            lines.append(f"| {names.get(k, k)} | {len(g)} | {avg(g)} | {round(sum(map(eng, g)) / len(g), 1)} |")
        lines.append("")

    before = [r for r in rows if parse(r["posted_at"]) < TAG_START]
    after = [r for r in rows if parse(r["posted_at"]) >= TAG_START]
    lines += ["## 変更前後（11/17〜 トピックタグ・紹介のリンクを返信へ）", "",
              f"- 変更前: {len(before)} 件、平均閲覧 {avg(before)}",
              f"- 変更後: {len(after)} 件、平均閲覧 {avg(after)}", ""]

    lines += ["## 投稿ごと（閲覧数の多い順）", "",
              "| 投稿日時 | 種類 | テーマ | 閲覧 | いいね | 返信 | 再投稿 | 書き出し |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -r["views"]):
        lines.append(f"| {parse(r['posted_at']):%m/%d %H:%M} | {KIND_NAMES.get(r['kind'], r['kind'])} | "
                     f"{THEME_NAMES.get(r['theme'], r['theme'])} | {r['views']} | {r['likes']} | {r['replies']} | "
                     f"{r['reposts']} | {r['text'].replace('|', '／')} |")
    if errors:
        lines += ["", f"## 取得できなかった投稿（{len(errors)} 件）", ""] + [f"- {e}" for e in errors[:20]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
