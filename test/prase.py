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

import json

import requests
from lxml import html


def treatContents(videoIds, contents):
    for content in contents:
        if not 'richItemRenderer' in content:
            break
        videoId = content['richItemRenderer']['content']['videoRenderer']['videoId']
        videoIds.add(videoId)
    return getContinuationToken(videoIds, contents)


def getContinuationToken(videoIds, contents):
    lastContent = contents[-1]
    if not 'continuationItemRenderer' in lastContent:
        return videoIds
    return lastContent['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']


def getChannelVideoIds(channelHandle):
    text = requests.get(f'https://www.youtube.com/{channelHandle}/videos').text
    tree = html.fromstring(text)

    ytVariableName = 'ytInitialData'
    ytVariableDeclaration = ytVariableName + ' = '
    for script in tree.xpath('//script'):
        scriptContent = script.text_content()
        if ytVariableDeclaration in scriptContent:
            ytVariableData = json.loads(scriptContent.split(ytVariableDeclaration)[1][:-1])
            break

    contents = ytVariableData['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content'][
        'richGridRenderer']['contents']

    videoIds = set()

    continuationToken = treatContents(videoIds, contents)
    if type(continuationToken) is set:
        return continuationToken

    url = 'https://www.youtube.com/youtubei/v1/browse'
    headers = {
        'Content-Type': 'application/json'
    }
    requestData = {
        'context': {
            'client': {
                'clientName'   : 'WEB',
                'clientVersion': '2.20240313.05.00'
            }
        }
    }
    while True:
        requestData['continuation'] = continuationToken
        try:
            data = requests.post(url, headers=headers, json=requestData).json()
        except requests.exceptions.SSLError:
            print('SSL error, retrying')
            continue
        # Happens not deterministically sometimes.
        if not 'onResponseReceivedActions' in data:
            print('Missing onResponseReceivedActions, retrying')
            with open('error.json', 'w') as f:
                json.dump(data, f, indent=4)
            continue
        continuationItems = data['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems']
        continuationToken = treatContents(videoIds, continuationItems)
        print(videoIds)
        if type(continuationToken) is set:
            return continuationToken
        print(len(continuationItems))


# Source: https://youtube.fandom.com/wiki/List_of_YouTube_channels_with_the_most_video_uploads?oldid=1795583
CHANNEL_HANDLES = [
    '@RoelVandePaar',
    '@Doubtnut',
    '@KnowledgeBaseLibrary',
    '@betterbandai4163',
    '@Hey_Delphi',
]

params = {
    'part': 'about',
}
for channelHandle in CHANNEL_HANDLES[::-1]:
    params['handle'] = channelHandle
    foundVideoIds = getChannelVideoIds(channelHandle)
    print(f'Found {len(foundVideoIds)} videos.')
