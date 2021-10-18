import requests
from dataclasses import dataclass
import os
from sys import argv
from url import DISCORD_WEBHOOK_URL
from datetime import datetime, timedelta, timezone
import time

url = r"https://api.ihavenojob.work/tuat/"
# url = r"http://localhost:8000/"
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
    attachment: str

    def into_responce(self) -> dict:
        date_get = datetime.strptime(self.dates[0:-5], "%Y/%m/%d")
        date_now = datetime.now()
        date = datetime(
            date_get.year,
            date_get.month,
            date_get.day,
            date_now.hour,
            (date_now.min // 10) * 10,
            tzinfo=timezone(timedelta(hours=9)),
        )
        if self.attachment is not None:
            fields = [
                {
                    "name": "カテゴリ",
                    "value": self.category,
                },
                {"name": "添付ファイル", "value": self.attachment},
            ]
        else:
            fields = [
                {
                    "name": "カテゴリ",
                    "value": self.category,
                }
            ]

        return {
            "content": None,
            "embeds": [
                {
                    "title": self.about,
                    "description": self.info,
                    "color": 8912728,
                    "fields": fields,
                    "author": {
                        "name": self.sender,
                        "icon_url": "https://www.tuat.ac.jp/images/tuat/outline/disclosure/pressrelease/2013/201312061125161043231738.jpg",
                    },
                    "timestamp": date.isoformat(),
                }
            ],
        }


def main(only_update=False):
    data = requests.get(url).json()

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

                item_data = item["data"]

                d = Info(
                    num=num,
                    important=False,
                    about=item_data["タイトル"] if "タイトル" in item_data else None,
                    info=item_data["本文"] if "本文" in item_data else None,
                    category=item_data["カテゴリー"] if "カテゴリー" in item_data else None,
                    sender=item_data["発信元"] if "発信元" in item_data else None,
                    dates=item_data["最終更新日"] if "最終更新日" in item_data else None,
                    attachment=item_data["添付ファイル"] if "添付ファイル" in item_data else None,
                )

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
