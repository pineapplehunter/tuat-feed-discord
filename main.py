import os
from sys import argv
from typing import Dict, List

from tuat_feed.post import Post
from url import DISCORD_WEBHOOK_URLS, DISCORD_ERR_URL
from datetime import datetime, timedelta, timezone
import time
import tuat_feed
import requests

import json

url = r"https://api.ihavenojob.work/tuat"
# url = r"http://localhost:8000/"
discord_urls: Dict[str, Dict[str, List[str]]] = DISCORD_WEBHOOK_URLS

num_db_filename = "num.db"


def format_post(post: Post, color: int):
    embed = {}
    embed["title"] = post.title
    embed["description"] = post.description[0:2000]
    embed["color"] = color
    fields = [
        {"name": "カテゴリー", "value": post.category},
        {
            "name": "対象",
            "value": post.target if len(post.target) <= 1024 else "長すぎるので省略します",
        },
    ]
    if len(post.attachment) != 0:
        if len(post.attachment) == 1:
            attachment = post.attachment[0]
            fields.append(
                {
                    "name": "添付ファイル",
                    "value": f"[{attachment.name}]({attachment.url})"
                    if len(attachment.url) <= 1024
                    else "URLが長すぎて表示できないので省略します",
                }
            )
        else:
            for i, attachment in enumerate(post.attachment):
                fields.append(
                    {
                        "name": f"添付ファイル{i+1}",
                        "value": f"[{attachment.name}]({attachment.url})"
                        if len(attachment.url) <= 1024
                        else "URLが長すぎて表示できないので省略します",
                    }
                )
    embed["fields"] = fields
    embed["author"] = {
        "name": post.origin,
        "icon_url": "https://www.tuat.ac.jp/images/tuat/outline/disclosure/pressrelease/2013/201312061125161043231738.jpg",
    }
    date_get = post.update_date
    date_now = datetime.now()
    date = datetime(
        date_get.year,
        date_get.month,
        date_get.day,
        date_now.hour,
        (date_now.minute // 10) * 10,
        tzinfo=timezone(timedelta(hours=9)),
    )
    embed["timestamp"] = date.isoformat()
    return {"content": "", "embeds": [embed]}


def main(only_update=False):
    db = []
    if not os.path.exists(num_db_filename):
        open(num_db_filename, "x").close()
    with open(num_db_filename, "r") as f:
        db = f.readlines()
    db = list(map(lambda x: int(x.strip()), db))

    with open(num_db_filename, "a") as f:

        for gakubu in ["technology", "agriculture"]:
            for category in ["academic", "campus"]:
                feed = tuat_feed.fetch(gakubu=gakubu, category=category, url=url)
                print(gakubu,category,feed[0])

                for post in feed:
                    try:
                        num = post.post_id
                        if num in db:
                            continue

                        global discord_urls

                        for post_url in discord_urls[gakubu][category]:
                            if not only_update:
                                for n in range(5):
                                    ret = requests.post(
                                        post_url,
                                        json=format_post(
                                            post,
                                            5814783
                                            if gakubu == "technology"
                                            else 8912728,
                                        ),
                                    )
                                    if ret.status_code // 100 == 2:
                                        print(f"{ret.status_code} Sent!")
                                        break
                                    try:
                                        if ret.status_code == 429:
                                            retry_after = ret.json()["retry_after"]
                                            print(f"sleep {retry_after}ms")
                                            time.sleep(retry_after / 1000)
                                    except:
                                        print(
                                            ret.status_code,
                                            ret.content,
                                            format_post(post, 0),
                                        )
                                        time.sleep(10)
                                if n == 10 - 1:
                                    requests.post(
                                        DISCORD_ERR_URL,
                                        json={
                                            "content": f"""エラー
                                            {ret.status_code} {ret.content}
                                            {post}"""
                                        },
                                    )
                        f.write(str(num) + "\n")     

                    except Exception as e:
                        if not only_update:
                            requests.post(post_url, data={"content": str(e)})


if __name__ == "__main__":
    only_update = False
    if len(argv) > 1 and argv[1] == "update":
        print("only update mode")
        only_update = True
    main(only_update)
