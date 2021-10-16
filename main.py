import requests
from dataclasses import dataclass
import os
from sys import argv
from url import DISCORD_WEBHOOK_URL
import json
from datetime import datetime
import time

url = r"https://api.ihavenojob.work/tuat/"
post_url = DISCORD_WEBHOOK_URL

num_db_filename = "num.db"


@dataclass
class Info:
    num: int
    important: bool
    about: str
    info: str
    category: str
    sender: str
    dates: str

    def into_responce(self) -> dict:
        date = datetime.strptime(self.dates[0:-5], "%Y/%m/%d")
        return {
            "content": None,
            "embeds": [
                {
                    "title": self.about,
                    "description": self.info,
                    "color": 8912728,
                    "fields": [
                        {
                            "name": "カテゴリ",
                            "value": self.category,
                        }
                    ],
                    "author": {
                        "name": self.sender,
                        "icon_url": "https://www.tuat.ac.jp/images/tuat/outline/disclosure/pressrelease/2013/201312061125161043231738.jpg",
                    },
                    "timestamp": date.isoformat(),
                }
            ],
        }


def main(only_update=False):
    data = json.loads(requests.get(url).content)

    db = []
    if not os.path.exists(num_db_filename):
        open(num_db_filename, "x").close()
    with open(num_db_filename, "r") as f:
        db = f.readlines()

    db = list(map(lambda x: int(x.strip()), db))
    # print(db)
    with open(num_db_filename, "a") as f:
        for item in data:
            try:
                num = int(item["id"])
                if num in db:
                    continue

                d = Info(
                    num=num,
                    important=False,
                    about=item["data"]["タイトル"],
                    info=item["data"]["本文"],
                    category=item["data"]["カテゴリー"],
                    sender=item["data"]["発信元"],
                    dates=item["data"]["最終更新日"],
                )

                # print(d)
                if not only_update:
                    while True:
                        ret = requests.post(post_url, json=d.into_responce())
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
