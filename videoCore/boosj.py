# author : gorquan <gorquanwu@gmail.com>
# date: 2019.8.15

import requests
import download
from headers import headers
import random
from urllib.parse import urlparse
import json
import time

# 思路 1.先访问http://gslb.boosj.com/ips.json，获取json 2. 根据第一步获取的json，构造第一部分参数，访问第一部分的json的glsb,获取json 3.根据第二部分获取的json，构造第二部分参数，访问第二部分json中的url，获取m3u8列表
# 此处返回ts文件列表,还需要使用插件进行下载和合并

class boosj(object):
    """获取播视广场舞视频类
    :param object: object
    """
    def __init__(self, url):
        """boosj class init
        :param self: self 
        :param url: 视频页面地址
        """
        self.video_id = None
        self.country = None
        self.area = None
        self.region = None
        self.isp = None
        self.ip = None
        self.s = None
        self.t = None
        self.url = None
        self.vtype = None
        self.headers = None
        self.gslb = None
        self.baseurl = url
        self.infoUrl = 'http://gslb.boosj.com/ips.json'
        self.tsList = set()
        self.success = True

    def __getipsJson(self):
        """获取并构造第一部分参数
        :param self: self
        """
        ipsResp = requests.get(self.infoUrl, headers=self.headers)
        if ipsResp.status_code == 200:
            ipsJson = json.loads(ipsResp.text)
            self.country = ipsJson['country']
            self.area = ipsJson['area']
            self.region = ipsJson['region']
            self.isp = ipsJson['isp']
            self.ip = ipsJson['ip']
            self.s = ipsJson['s']
            self.gslb = ipsJson['gslb']
            self.extplaylist = dict()

    def __getvideoUrl(self):
        """获取视频链接,并构造第二部分参数
        :param self: self
        """   
        params = {
            '_id': self.video_id,
            'country': self.country,
            'area': self.area,
            'region': self.region,
            'isp': self.isp,
            'ip': self.ip,
            's': self.s,
            'gslb': self.gslb,
            '_': int(round(time.time() * 1000))
        }
        urlResp = requests.get(self.gslb, params=params)
        if urlResp.status_code == 200:
            urlJson = json.loads(urlResp.text)
            self.url = urlJson['url']
            self.vtype = urlJson['vtype']
            self.t = urlJson['t']

    def __getvideoList(self):
        """获取ts文件列表链接
        :param self: self
        """   
        listResp = requests.get(self.url, params=self.t)
        line = (listResp.text).split('\n')
        if line[0] == '#EXTM3U':
            for i in line:
                if 'http://' in i or 'https://' in i:
                    self.tsList.add(i)
                else:
                    continue

    def getVideoUrl(self):
        """获取播视广场舞视频文件链接
        :param self: self
        :param return: 返回ts文件列表链接
        """   
        Header = Headers(self.baseurl)
        self.video_id = (((urlparse(
            self.baseurl)).path).lstrip('/')).rstrip('.html')
        self.headers = Header.buildHeader()
        self.__getipsJson()
        self.__getvideoUrl()
        self.__getvideoList()
        return {'success': self.success, 'videoUrl': self.tsList}


class Headers(headers):
    """构建播视广场舞网站的headers类
    :param headers: 父类，构建headers类
    """
    def buildHeader(self):
        """构建播视广场舞的headers函数
        :param self: self
        :return self.headers： 返回构建完成的headers
        """
        self.hostname = (urlparse(self.url)).hostname
        self.agent = random.choice(self.agentlist)
        self.headers = {
            'Origin': 'http://' + self.hostname,
            'Referer': self.url,
            'User-Agent': self.agent
        }
        return self.headers