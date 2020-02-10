import requests
from bs4 import BeautifulSoup
import chardet
from dataclasses import dataclass
import os
from sys import argv
from url import DISCORD_WEBHOOK_URL
import json

url = r"https://api.ihavenojob.work/tuat/"
post_url = DISCORD_WEBHOOK_URL

num_db_filename = "num.db"


@dataclass
class Info:
    num: int
    important: bool
    about: str
    info: str
    sender: str
    dates: str

    def format_info(self) -> str:
        s = ""
        s += "┌─────────────────────\n"
        # if self.important:
        #     s += "**重要**\n"
        s += f"件名: {self.about}\n"
        s += f"内容: \n```\n{self.info}\n```\n"
        s += f"from: {self.sender}\n"
        s += f"日付: {self.dates}\n"
        s += "└─────────────────────"
        return s


def main(only_update=False):
    data = json.loads(requests.get(url).content)

    db = []
    if not os.path.exists(num_db_filename):
        open(num_db_filename, "x").close()
    with open(num_db_filename, "r") as f:
        db = f.readlines()

    db = list(map(lambda x: int(x.strip()), db))
    # print(db)
    with open(num_db_filename, "a")as f:
        for item in data:
            try:
                print(item)
                num = int(item["id"])
                if num in db:
                    continue

                d = Info(
                    num=num,
                    important=False,
                    about=item["data"]["タイトル"],
                    info=item["data"]["本文"],
                    sender=item["data"]["発信元"],
                    dates=item["data"]["最終更新日"]
                )

                # print(d)
                if not only_update:
                    ret = requests.post(post_url, data={"content": d.format_info()})
                    # print(ret)
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
