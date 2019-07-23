# author: gorquan <gorquanwu@gmail.com>
# date: 2019.7.21
import requests
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import ast
from message import Message


class SharedMessage(Message):
    def __init__(self, user_id, msg):
        super().__init__(user_id, msg)
        msg = ast.literal_eval(str(self.msg))
        print(msg)
        self.tag = msg['SharedTag']
        self.title = msg['SharedTitle']
        self.jumpUrl = msg['SharedJumpurl']

    def buildHeader(self, url, hostname):
        agentlist = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        agent = random.choice(agentlist)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": hostname,
            "Pragma": "no-cache",
            "User-Agent": agent
        }
        return headers

    def getVideoAddress(self, hostname, page):
        if hostname == 'share.tangdou.com':
            page = BeautifulSoup(page, 'lxml')
            videoAddress = (page.find('video')).get('src')
            analysisResult = True
        elif hostname == 'm.9igcw.com':
            page = BeautifulSoup(page, 'lxml')
            videoAddress = (page.find('video')).get('src')
            analysisResult = True
        # elif hostname == 'main.gcwduoduo.com':
        #     page = BeautifulSoup(page, 'lxml')
        #     print(page.find('video'))
        #     videoAddress = (page.find('video')).get('src')
        #     analysisResult = True
        # elif hostname == 'www.boosj.com':
        #     page = BeautifulSoup(page, 'lxml')
        #     videoAddress = (page.find('video')).get('src')
        #     analysisResult = True
        # elif hostname == '52op.net':
        #     page = BeautifulSoup(page, 'lxml')
        #     videoAddress = (page.find('video')).get('src')
        #     analysisResult = True
        # elif hostname == 'm.baidu.com':
        #     page = BeautifulSoup(page, 'lxml')
        #     videoAddress = (page.find('video')).get('src')
        #     analysisResult = True
        else:
            analysisResult = False
            videoAddress = ''
        return {"analysisResult": analysisResult, 'videoAddress': videoAddress}

    def dealMessage(self):
        if self.jumpUrl == '':
            self.msg = "你的分享链接为空！"
        else:
            shortUrlResp = requests.get(self.jumpUrl, allow_redirects=False)
            shortUrlCode = shortUrlResp.status_code
            if shortUrlCode == 404:
                self.msg = "你分享的内容无法打开"
            else:
                if shortUrlCode == 302:
                    realUrl = shortUrlResp.headers['Location']
                else:
                    realUrl = self.jumpUrl
                hostname = (urlparse(realUrl)).hostname
                headers = self.buildHeader(realUrl, hostname)
                realUrlResp = requests.get(realUrl, headers=headers)
                result = self.getVideoAddress(hostname, realUrlResp.text)
                if result['analysisResult']:
                    self.msg = "分享内容： " + self.title + '\n' + "分享平台： " + \
                        self.tag + "\n" + "视频链接: " + result['videoAddress']
                else:
                    self.msg = "暂不支持解析你的分享"

    def sendMessage(self):
        self.dealMessage()
        return super().sendMessage()
