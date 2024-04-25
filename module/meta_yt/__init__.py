import requests, asyncio, re


def extract_info(videoId):
    response = requests.post(
        url="https://www.youtube.com/youtubei/v1/player",
        params={
            "videoId": videoId,
            "key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
            "contentCheckOk": "True",
            "racyCheckOk": "True",
        },
        json={
            "context": {
                "client": {"clientName": "MWEB", "clientVersion": "2.20211109.01.00"}
            },
            "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        },
    )

    data = response.json()["videoDetails"]

    videoId = data["videoId"]
    channelId = data["channelId"]

    url = f"https://youtu.be/{videoId}"
    title = data["title"]
    channel = data["author"]
    duration = int(data["lengthSeconds"])
    views = int(data["viewCount"])
    thumbnail = data["thumbnail"]["thumbnails"][
        len(data["thumbnail"]["thumbnails"]) - 1
    ]["url"]
    channel_url = f"https://www.youtube.com/channel/{channelId}"

    return url, title, views, duration, thumbnail, channel, channel_url


if __name__ == "__main__":
    print(asyncio.run(extract_info("hTqFFYX93yY")))
