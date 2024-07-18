#    ------------------------------------------------------------
#    Copyright (c) 2024 Rystal-Team
#  #
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#  #
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#  #
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.
#    ------------------------------------------------------------
#  #

import json

import requests


def treatContents(videoIds, contents):
    for content in contents:
        if 'playlistVideoRenderer' not in content:
            continue
        videoId = content['playlistVideoRenderer']['videoId']
        videoIds.add(videoId)
    return getContinuationToken(videoIds, contents)


def getContinuationToken(videoIds, contents):
    lastContent = contents[-1]
    if 'continuationItemRenderer' not in lastContent:
        return videoIds
    return lastContent['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']


def getPlaylistVideoIds(playlistId):
    url = f'https://www.youtube.com/playlist?list={playlistId}'
    response = requests.post(url)
    if response.status_code != 200:
        print(f"Failed to fetch playlist: {playlistId}")
        return set()

    try:
        json_data = response.json()
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON data: {e}")
        print(f"Response content: {response.content}")
        return set()

    contents = \
        json_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
            'sectionListRenderer'][
            'contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']

    videoIds = set()
    continuationToken = treatContents(videoIds, contents)
    if isinstance(continuationToken, set):
        return continuationToken

    while True:
        params = {
            'action_get_playlist_details': 1,
            'ajax'                       : 1,
            'continuation'               : continuationToken,
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch playlist continuation: {playlistId}")
            return videoIds

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON data: {e}")
            print(f"Response content: {response.content}")
            return videoIds

        if 'contents' not in data:
            print(f"Missing contents in playlist continuation: {playlistId}")
            return videoIds

        continuationItems = data['contents']['singleColumnWatchNextResults']['playlist']['playlist']['contents']
        continuationToken = treatContents(videoIds, continuationItems)
        if isinstance(continuationToken, set):
            return continuationToken


def fetchPlaylistVideos(playlistId):
    foundVideoIds = getPlaylistVideoIds(playlistId)
    print(f'Found {len(foundVideoIds)} videos in playlist: {playlistId}')


fetchPlaylistVideos("PL1zOoe1s6s3wBi-q9U5iMwQ3BNqJKoR_y")
