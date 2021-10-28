from dataclasses import dataclass
import os
from sys import argv

from tuat_feed.post import Post
from url import DISCORD_WEBHOOK_URL
from datetime import datetime, timedelta, timezone
import time
import tuat_feed
import requests

url = r"https://api.ihavenojob.work/tuat/"
# url = r"http://localhost:8000/"
post_url = DISCORD_WEBHOOK_URL

num_db_filename = "num.db"


def format_post(post: Post):
    embed = {}
    embed["title"] = post.title
    embed["description"] = post.description
    embed["color"] = 8912728
    fields = [{"name": "カテゴリー", "value": post.category}]
    if len(post.attachment) != 0:
        attachment_txts = []
        for attachment in post.attachment:
            attachment_txts.append(f"({attachment.name})[{attachment.url}]")
        fields.append({"name": "添付ファイル", "value": "\n".join(attachment_txts)})
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
    return {"content": None, "embeds": [embed]}


def main(only_update=False):
    feed = tuat_feed.fetch()

    db = []
    if not os.path.exists(num_db_filename):
        open(num_db_filename, "x").close()
    with open(num_db_filename, "r") as f:
        db = f.readlines()

    db = list(map(lambda x: int(x.strip()), db))
    with open(num_db_filename, "a") as f:
        for post in feed:
            try:
                num = post.post_id
                if num in db:
                    continue

                if not only_update:
                    while True:
                        ret = requests.post(post_url, json=format_post(post))
                        print(ret.status_code, ret.content)
                        if ret.status_code // 100 == 2:
                            break
                        time.sleep(10)
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
