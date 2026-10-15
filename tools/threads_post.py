"""threads/queue.json の未投稿の先頭1件を Threads に投稿する。

Threads アカウントは全サイト共通。link には投稿内容に対応するサイトの記事URLを完全な形で書く。

必要な環境変数（GitHub の Secrets に登録）:
  THREADS_ACCESS_TOKEN  threads_content_publish 権限付きの長期アクセストークン
  THREADS_USER_ID       Threads のユーザーID（省略時は "me"）
DRY_RUN=1 のときは投稿せず、送る内容を表示するだけ。
"""
import json
import os
import pathlib
import sys
import time
import urllib.parse
import urllib.request

API = "https://graph.threads.net/v1.0"
QUEUE = pathlib.Path(__file__).resolve().parent.parent / "threads" / "queue.json"


def call(path, params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(urllib.request.Request(f"{API}/{path}", data=data), timeout=30) as res:
        return json.load(res)


def main():
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    post = next((p for p in queue if not p.get("posted_at")), None)
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
    container = call(f"{user}/threads", {**params, "access_token": token})["id"]
    time.sleep(10)  # コンテナの準備を待つ
    result = call(f"{user}/threads_publish", {"creation_id": container, "access_token": token})
    post["posted_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    post["thread_id"] = result.get("id")
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"投稿しました: {post['thread_id']}")


if __name__ == "__main__":
    main()
