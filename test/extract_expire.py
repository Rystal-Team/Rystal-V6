

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

url = "https://rr1---sn-aigl6nsr.googlevideo.com/videoplayback?expire=1719847124&ei=dHSCZqfkIq3vir4Pw6SBqA4&ip=78.108.218.193&id=o-AKbMWrsERUQwKKuLKOxfEx7zqFxN6wiKpcf9hrnvtmWl&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&bui=AbKP-1NbZ0bc8AM6lkRILy95muF0W3OxOotGGYXYkbPKIaC64ozgj9sFogUSlpHdywtjanDWNJ16A0F8&spc=UWF9fyyrT03J2KE0xQtmrxRtwfQDp8JKhrO1-nT-GNn8K0jWJGGqatpzfTXy&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=lKXKemaSTxyDwgIzJH_C1FEQ&rqh=1&gir=yes&clen=5629738&dur=317.321&lmt=1718048738260822&keepalive=yes&c=WEB&sefc=1&txp=6208224&n=a6obJsPksYPGrQ&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRQIgPfZW8Pz5uWKGEqx0NaFpwaxRRxjrrz0cnfd_tRvqPaUCIQCRftL-8L8rlSBsCVJgWQiGwD02c9OPaD4KP6wT3mEebg%3D%3D&rm=sn-vgqel676&fexp=24350517&req_id=46bab091cf37a3ee&ipbypass=yes&redirect_counter=2&cm2rm=sn-uigxx03-n1qe7e&cms_redirect=yes&cmsv=e&mh=O6&mip=92.40.190.107&mm=29&mn=sn-aigl6nsr&ms=rdu&mt=1719825423&mv=m&mvi=1&pl=23&lsparams=ipbypass,mh,mip,mm,mn,ms,mv,mvi,pl&lsig=AHlkHjAwRgIhAMISxSJZm5WB9-KdRPCr3F96TQT9Ar02IBnK5i6PwjeRAiEAkxhevQ67aS5na8CC3R9qyGPSojTaQrQzp3BpD86J_aQ%3D"


def get_expire(url):
    start = url.find("expire=")
    if start == -1:
        return None
    end = start + len("expire=")
    while end < len(url) and url[end].isdigit():
        end += 1
    return int(url[start + len("expire="): end])


def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


expire_time = get_expire(url)
if expire_time:
    sec = [60, 3600, 86400, 31536000]
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    year = 1970
    month = 1

    while expire_time >= sec[3] + (is_leap(year) * sec[2]):
        expire_time -= sec[3] + (is_leap(year) * sec[2])
        year += 1
    days_in_month[1] = 29 if is_leap(year) else 28
    while expire_time >= days_in_month[month - 1] * sec[2]:
        expire_time -= days_in_month[month - 1] * sec[2]
        month += 1

    day = expire_time // sec[2] + 1
    expire_time %= sec[2]
    hour = expire_time // sec[1]
    expire_time %= sec[1]
    minute = expire_time // sec[0]
    expire_time %= sec[0]
    second = expire_time

    print(f"{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02} utc")
else:
    print("expire param not found")
