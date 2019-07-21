import requests
from bs4 import BeautifulSoup
import chardet
from dataclasses import dataclass
import os
from sys import argv
from url import DISCORD_WEBHOOK_URL

url = r"http://t-board.office.tuat.ac.jp/T/boar/resAjax.php?&kfvGafu[]=1&kfvGafu[]=9&skip=0"
url_info = r"http://t-board.office.tuat.ac.jp/T/boar/vewAjax.php?i={}"
post_url = DISCORD_WEBHOOK_URL

num_db_filename = "num.db"


@dataclass
class Info:
    num: int
    important: bool
    about: str
    info: str
    to: str
    sender: str
    dates: str

    def format_info(self) -> str:
        s = ""
        s += "┌─────────────────────\n"
        if self.important:
            s += "**重要**\n"
        s += f"対象: `{self.to}`\n"
        s += f"件名: {self.about}\n"
        s += f"内容: \n```\n{self.info}\n```\n"
        s += f"from: {self.sender}\n"
        s += f"日付: {self.dates}\n"
        s += "└─────────────────────"
        return s


def main(only_update=False):
    page = requests.get(url).content

    encoding = chardet.detect(page)["encoding"]
    # print(encoding)
    if encoding != "utf-8":
        page = page.decode(encoding, "replace").encode("utf-8")

    soup = BeautifulSoup(page, "html.parser").table.tbody

    db = []
    if not os.path.exists(num_db_filename):
        open(num_db_filename, "x").close()
    with open(num_db_filename, "r") as f:
        db = f.readlines()

    db = list(map(lambda x: int(x.strip()), db))
    # print(db)
    with open(num_db_filename, "a")as f:
        try:
            for i in soup.find_all("tr"):
                s = str(i)
                num = int(str(i["alt"]).strip())
    
                if num in db:
                    continue
    
                soooup = BeautifulSoup(s, "html.parser")
                items = soooup.find_all("td")
                info, to = get_info(num)

                about = "".join(items[1].find_all('p')[1].strings)
                if about is None:
                    about = "".join(items[1].find_all('p')[0].string)
                about = about.replace("\n","").strip()
                
                sender = ""
                try:
                    sender = "".join(items[2].strings)
                except Exception:
                    pass
                dates = ""
                try:
                    dates="".join(items[3].string)
                except:
                    pass

                d = Info(
                    num=num,
                    important=items[0].string is None,
                    about=about,
                    info=info,
                    to=to,
                    sender=sender,
                    dates=dates
                )

                # print(d)
                if not only_update:
                    ret = requests.post(post_url, data={"content": d.format_info()})
                    # print(ret)
                f.write(str(num) + "\n")
        except Exception as e:
            requests.post(post_url, data={"content": str(e)})


def get_info(num: int) -> (str, str):
    u = url_info.format(num)
    c = requests.get(u).content
    info = ""
    to = ""
    for e in BeautifulSoup(c, "html.parser").table.find_all("tr"):
        soup = BeautifulSoup(str(e), "html.parser")
        l = soup.findChildren("td")

        # print(l)

        if str(l[0].string).find("本文") != -1:
            info = "".join(BeautifulSoup(str(l[1]), "html.parser").strings).strip()
        elif "".join(l[0].strings).find("対象") != -1:
            to = "".join(l[1].span.strings).strip()

    return info, to


if __name__ == "__main__":
    only_update = False
    if len(argv) > 1 and argv[1] == "update":
        print("only update mode")
        only_update = True
    main(only_update)
