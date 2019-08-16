# author: gorquan <gorquanwu@gmail.com>
# date: 2019.8.16

import requests
import json
import time
from headers import headers
from urllib.parse import urlparse
import random
from bs4 import BeautifulSoup
import re
from hyper.contrib import HTTP20Adapter
from slimit.parser import Parser
from slimit.visitors import nodevisitor
from slimit import ast
import ast as listast




# 思路： 1. 先爬取页面，获得vid等信息 2. 根据vid、referer以及时间戳，访问https://my.tv.sohu.com/play/videonew.do，获取视频信息json 3. 根据获取到的json，构造参数，访问https://data.vod.itc.cn/ip获取


class sohu(object):
    """获取搜狐视频类
    :param object: object
    """
    def __init__(self, url):
        """sohu class init
        :param self: self
        :param url: 视频页面地址
        """
        self.pageHeaders = None
        self.jsonHeaders = None
        self.url = url
        self.videoUrl = None
        self.vid = None
        self.ssl = '1' # 需要分析代码
        self.ver = '31' # 需要分析代码
        self.new = None
        self.num = None
        self.key = None
        self.ch = None
        self.pt = '1' # 需要分析代码
        self.pg = '2' # 需要分析代码
        self.prod = 'h5n' # 需要分析代码
        self.uid = None
        self.videoInfoUrl = 'https://my.tv.sohu.com/play/videonew.do'
        self.videoServerUrl = 'https://data.vod.itc.cn/ip'

    def __getvid(self):
        """访问页面获取视频vid
        :param self: self
        """
        # 因为搜狐页面采用了HTTP/2，但是python的requests不支持HTTP/2，此处采取requests+hyper方式访问
        session = requests.session()
        session.mount('https://'+(urlparse(self.url)).hostname, HTTP20Adapter())
        pageResp = session.get(self.url,headers=self.pageHeaders)
        if pageResp.status_code == 200:
            page = BeautifulSoup(pageResp.text,'lxml')
            script = page.find('script',text=lambda text: text and "var vid" in text)
            parser = Parser()
            tree = parser.parse(script.text)
            for node in nodevisitor.visit(tree):
                if isinstance(node,ast.VarDecl) and node.identifier.value == 'vid':
                    self.vid = int((node.initializer.value).strip("'"))

            
    def __getvideoJson(self):
        """获取视频详细信息,构建获取视频链接参数
        :param self: self
        """
        params = {
            'vid': self.vid,
            'ver': self.ver,
            'ssl': self.ssl,
            'referer': self.url,
            't': int(round(time.time() * 1000))
        }
        print(params)
        videoJsonResp = requests.get(self.videoInfoUrl,params=params, headers=self.jsonHeaders)
        if videoJsonResp.status_code == 200:
            videoJson = json.loads(videoJsonResp.text)
            self.new = videoJson['data']['su'][0]
            self.num = videoJson['data']['num']
            self.key = videoJson['data']['ck'][0]
            self.ch = videoJson['data']['ch'] 
            


    def __getvideoUrl(self):
        """获取视频地址
        :param self: self
        """
        # 目前参数缺少一个uid，但是发现uid不存在也可以获取视频地址
        # pt、pg、prod均需要重新分析js获取
        params = {
            'new': self.new,
            'num': self.num,
            'key': self.key,
            'ch': self.ch,
            'pt': self.pt,
            'pg': self.pg,
            'prod': self.prod
        }
        videoUrlResp = requests.get(self.videoServerUrl,params=params)
        if videoUrlResp.status_code == 200:
            self.videoUrl = (((json.loads(videoUrlResp.text))['servers'])[0])['url']
            print(self.videoUrl)

    def getVideoUrl(self):
        """获取搜狐视频文件链接
        :param self: self
        :param return: 返回视频文件链接
        """
        self.pageHeaders = PageHeaders(self.url).buildHeader()
        self.jsonHeaders = JsonHeaders(self.url).buildHeader()
        self.__getvid()
        self.__getvideoJson()
        self.__getvideoUrl()
        


class JsonHeaders(headers):
    """构建搜狐json的headers类
    :param headers: 父类，构建headers类
    """
    def buildHeader(self):
        """构建搜狐json的headers函数
        :param self: self
        :param return: 返回构建完成的headers
        """
        self.hostname = (urlparse(self.url)).hostname
        self.agent = random.choice(self.agentlist)
        self.headers = {
            'Origin': 'http://' + self.hostname,
            'Referer': self.url,
            'User-Agent': self.agent
        }
        return self.headers


class PageHeaders(headers):
    """构建搜狐页面的headers类
    :param headers: 父类，构建headers类
    """
    def buildHeader(self):
        """构建搜狐页面的headers函数
        :param self: self
        :param return: 返回构建完成的headers
        """
        urlArray = urlparse(self.url)
        self.hostname = urlArray.hostname
        path = urlArray.path
        self.agent = random.choice(self.agentlist)
        self.headers = {
            ':authority': self.hostname,
            ':method': 'GET',
            ':path': path,
            ':scheme': 'https',
            'accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language':
            'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': self.agent
        }
        return self.headers

# debug信息，先保留，完成调试后删除
# if __name__ == "__main__":
#     Sohu = sohu('https://tv.sohu.com/v/cGwvOTU0MDAzOC8xNDc4MDMwMTMuc2h0bWw=.html')
#     Sohu.getVideoUrl()