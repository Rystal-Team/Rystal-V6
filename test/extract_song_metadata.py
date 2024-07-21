#  ------------------------------------------------------------
#  Copyright (c) 2024 Rystal-Team
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#  ------------------------------------------------------------
#

import time

import requests
from termcolor import colored

print(colored(text="(FROM URL)", color="dark_grey"))
timer = time.time()

r = requests.post(
    url="https://www.youtube.com/youtubei/v1/player",
    params={
        "videoId"       : "k7D6CguCXqc",
        "key"           : "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        "contentCheckOk": "True",
        "racyCheckOk"   : "True",
    },
    headers={"User-Agent": "com.google.android.apps.youtube.music/"},
    json={
        "context": {
            "client": {"clientName": "MWEB", "clientVersion": "2.20211109.01.00"}
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
)

video_Detail = {
    "videoId"          : "k7D6CguCXqc",
    "title"            : "クリス・ハート - I LOVE YOU",
    "lengthSeconds"    : "361",
    "keywords"         : [
        "pv",
        "mv",
        "universal",
        "music",
        "japan",
        "ユニバーサル",
        "ミュージック",
        "ジャパン",
        "live",
        "ライブ",
        "youtube",
        "ようつべ",
        "新曲",
        "歌詞",
        "lyrics",
        "高画質",
        "オフィシャル",
        "official",
        "クリスハート",
        "クリス・ハート",
        "クリス",
        "ハート",
        "松田聖子",
        "デュエット",
        "duet",
        "matsuda",
        "seiko",
        "i love you",
        "LOVE",
        "紅白",
        "紅白歌合戦",
        "泣ける",
        "泣き歌",
        "切ない",
        "恋",
        "バレンタイン",
        "ホワイトデー",
        "クリスマス",
        "泣ける歌",
        "失恋",
        "失 恋ソング",
        "VEVO",
        "まもりたい～magic of a touch～",
        "まもりたい",
        "夢がさめて",
        "home",
        "たしかなこと",
        "旅立つ日",
        "スマスマ",
        "SMAP",
        "SMAP×SMAP",
        "UCl2aT0nRejTCQO_LHZAftBw",
        "UNIVERSAL MUSIC JAPAN",
        "音楽",
    ],
    "channelId"        : "UCl2aT0nRejTCQO_LHZAftBw",
    "isOwnerViewing"   : False,
    "shortDescription" : '2020年、ついに再始動が決定！\n\n【クリス・ハート 全国ツアー2020～Love is Love（愛を歌う）】\n2020年4月10日（金）千葉県 市川市文化会館\n2020年4月12日（日）愛知県 日本特殊陶業市民会館 フォレストホール\n2020年4月19日（日）福岡県 福岡国際会議場 メインホール\n2020年4月25日（土）東京都 LINE CUBE SHIBUYA（渋谷公会堂）\n2020年5月3日（日・祝）大阪府 グランキューブ大阪（大阪府立国際会議場）\n\nチケット好評発売中！\nhttps://t.pia.jp/pia/event/event.do?eventBundleCd=b2052654\n\n世界一泣ける"愛"のうた。"心"に沁みる感動のラブストーリー\n【泣】話題のクリス・ハートの新曲「I LOVE YOU」\niTunes Store好評配信中：http://smarturl.it/ILoveYou_iTunes\n\n2014.2.26 IN STORES\nクリス・ハート、初のオリジナル・シングル「I LOVE YOU」\n「僕も過去には失恋もありましたが、その度に強くなれました。\n恋人との幸せな時間は、別れた後きっ と良い経験になって、未来の素敵な出会いに繋がっていると思います。」\n（クリス・ハート）\n\n★NEW★\nあれから2年・・・\n前作「アイ ラブ ユー」では語られなかった感動のラストメッセージが今、 明かされる。\n「アイ ラブ ユー」の続編作、「Still loving you」 短編ドラマ、全編公開中!\nhttps://www.youtube.com/watch?v=q9kn0mErR9Q\n\n\nオフィシャルサイト\nhttp://chris-hart.net/\n\nユニバーサルミュージックサイト\nhttp://www.universal-music.co.jp/chris-hart\n\nクリス・ハート iTunes Storeアーティストページ\nhttp://smarturl.it/ILoveYou_iTunes',
    "isCrawlable"      : True,
    "thumbnail"        : {
        "thumbnails": [
            {
                "url"   : "https://i.ytimg.com/vi/k7D6CguCXqc/default.jpg",
                "width" : 120,
                "height": 90,
            },
            {
                "url"   : "https://i.ytimg.com/vi/k7D6CguCXqc/mqdefault.jpg",
                "width" : 320,
                "height": 180,
            },
            {
                "url"   : "https://i.ytimg.com/vi/k7D6CguCXqc/hqdefault.jpg",
                "width" : 480,
                "height": 360,
            },
            {
                "url"   : "https://i.ytimg.com/vi/k7D6CguCXqc/sddefault.jpg",
                "width" : 640,
                "height": 480,
            },
            {
                "url"   : "https://i.ytimg.com/vi/k7D6CguCXqc/hq720.jpg?sqp=-oaymwEhCK4FEIIDSFryq4qpAxMIARUAAAAAGAElAADIQj0AgKJD&rs=AOn4CLD-__TABqHhWDUhPTPzLytbLdWnWw",
                "width" : 686,
                "height": 386,
            },
        ]
    },
    "allowRatings"     : True,
    "viewCount"        : "46230718",
    "author"           : "UNIVERSAL MUSIC JAPAN",
    "isPrivate"        : False,
    "isUnpluggedCorpus": False,
    "isLiveContent"    : False,
}

data = r.json()["videoDetails"]
videoId = data["videoId"]
print(f"https://youtu.be/{videoId}")
print(data["author"])
print(data["title"])
print(data["lengthSeconds"])
print(data["viewCount"])
print(data[-1][-1][-1])

print(colored(text=f"Time taken: {time.time() - timer}", color="dark_grey"))
