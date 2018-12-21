import asyncio
import websockets
from slacker import Slacker
import json
from bs4 import BeautifulSoup
import urllib.request
import re
import time
import random

_url = "https://dhlottery.co.kr/gameResult.do?method=byWin"
add = "&drwNo="
imoticon = ["( ｯ◕ ܫ◕)ｯ'", "ฅ◕ᴥ◕ฅ", "ฅ( ̳• ·̫ • ̳ฅ) ", "(っ＇～＇)づ⌒☆", "ค^•ﻌ•^ค ", "๑'͡o_'͡o๑ "]

def ohaAsa(username):
    url = "https://twitter.com/Ohayoasa_"
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    res = soup.find("div",class_="user-pinned").find("p",class_="tweet-text").get_text()
    res +="\n오늘의 운세는 어떠신가요? 운은 하루를 멋지게할 목적으로만 봐주세요.\n\n오늘을 정하는것은 소중한 당신이에요."
    return res

def lottery(url):
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []

    result = soup.find("div", class_="win_result").find("h4").find("strong").get_text()
    date = soup.find("p", class_="desc").get_text()
    keywords.append(result+" 당첨결과 "+"`"+date+"`\n")

    for i in soup.find("div", class_="num win").find_all("span"):
        keywords.append(i.get_text())

    bonus = soup.find("div", class_="num bonus").find("span")
    keywords.append("`" + bonus.get_text()+"`")

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.

    return u' '.join(keywords)

def match(lotto):
    url = _url+add+lotto[0]
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")
    # 로또 당첨 번호
    numbers = []

    for i in soup.find("div", class_="num win").find_all("span"):
        numbers.append(i.get_text())

    bonus = soup.find("div", class_="num bonus").find("span")
    new_bonus = (bonus.get_text())

    #내가 넣은 로또 번호
    new_lotto = lotto[1:]

    win = set()

    for i in range(0, 6):
        for j in range(0, 6):
            if numbers[i] == new_lotto[j]:
                win.add(new_lotto[j])

    if len(win) == 6:
        price = "1등입니다!! 맞춰드린김에 2할만 떼주세요~"
    elif len(win) == 5 and new_bonus == lotto[-1]:
        price = "2등입니다~~!!"
    elif len(win) == 5:
        price = "3등입니다~!"
    elif len(win) == 4:
        price = "4등입니다~!"
    elif len(win) == 3:
        price = "5등입니다~!"
    else:
        price = "낙첨"

    return price


async def execute_bot():
    slack = Slacker('your token')
    res = slack.rtm.connect()
    endpoint = res.body['url']
    ws = await websockets.connect(endpoint)
    isCalled = False
    while True:
        message_json = await ws.recv()
        print(message_json)
        try:
            msg = json.loads(message_json)
            if 'text' in msg.keys():
                if "<@UEXL989S9>" in msg['text']:
                    text = msg['text'].strip().split()[1:]
                    compile_text = re.compile(r'\d+')
                    match_text = compile_text.findall(' '.join(text))
                    if "로또" in text or "이번주" in text:
                        print(match_text)
                        if match_text is not []:
                            key = lottery(_url+add+''.join(match_text))
                            slack.chat.post_message(msg['channel'], str(key))
                            continue
                        key = lottery(_url)
                        slack.chat.post_message(msg['channel'], str(key))
                        #오늘 로또 알려줘
                        #777회 로또 알려줘
                    elif "맞춰라" in text:
                        # slack.chat.post_message(msg['channel'], "회차, 숫자(6), 보너스 순으로 입력해주세요")
                        price = match(match_text)
                        slack.chat.post_message(msg['channel'], price)
                    elif "운세" in text:
                        text = ohaAsa(msg['user'])
                        slack.chat.post_message(msg['channel'], text)

                    else:
                        if msg['text'] == "<@UEXL989S9>":
                            print(msg['text'])
                            attachments_dict = dict()
                            attachments_dict['color'] = '#b847d1'
                            attachments_dict['pretext'] = "Bob은 이렇게 사용하세요"
                            attachments_dict['title'] = "Bob 사용법"
                            attachments_dict['text'] = "로또 알려줘, 이번주 로또, 로또: 이번주 로또 당첨번호를 알려드립니다.\n"\
                                                        "맞춰라 [회차](회) [숫자(6개)] [보너스 숫자]: 내 복권의 당첨을 알려드려요\n"\
                                                       "그 외에 다양한 챗봇들과의 상호작용도 존재합니다!"
                            attachments_dict['mrkdwn_in'] = ['text', 'pretext']
                            attachments = [attachments_dict]
                            slack.chat.post_message(msg['channel'], attachments=attachments)
                        else:
                            slack.chat.post_message(msg['channel'], "네에에??? '"+''.join(text)+"'라구요?")
                elif "사라져" in msg['text']:
                    slack.chat.post_message(msg['channel'], "위키야....")
                    time.sleep(1)
                    slack.chat.post_message(msg['channel'], "어떻게.. 저라도..")
                elif 'bot_id' not in msg:
                    if "뭐야?" in msg['text']:
                        slack.chat.post_message(msg['channel'], "ㅎㅎ? 위키는 알걸요")
                    if "고양이" in msg['text']and not "@UEWRZPF3K>" in msg['text']:
                        slack.chat.post_message(msg['channel'], "고양이는 donghyun_bot을 불러보세요")
                    if "wiki" in msg['text'] or "위키" in msg['text']:
                        slack.chat.post_message(msg['channel'], "위키야 너 부른다.")
                    if "운세" in msg['text']:
                        text = ohaAsa(msg['user'])
                        slack.chat.post_message(msg['channel'], text)
                        print("yes")
                elif 'KWiki' in msg['username']:
                    if "다." in msg['text'] or "요." in msg['text']:
                        ran_num = random.randrange(0, len(imoticon))

                        slack.chat.post_message(msg['channel'], imoticon[ran_num])



        except Exception as e:
            print("!!!error [errorname]: "+e)
            break



loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
asyncio.get_event_loop().run_until_complete(execute_bot())
asyncio.get_event_loop().run_forever()
