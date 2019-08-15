# author: gorquan <gorquanwu@gmail.com>
# date: 2019.8.15

import requests
from headers import headers
from bs4 import BeautifulSoup


class gcw91(object):
    """获取就爱广场舞视频类
    :param object: object
    """
    def __init__(self,url):
        """gcw91 class  init
        :param url: 视频页面地址
        """
        self.url = url
        self.headers = None
        self.videoUrl = None
        self.success = False
    
    def __getvideoUrl(self):
        """解析页面获取视频地址
        :param self: self
        """
        urlResp = requests.get(self.url, headers=self.headers)
        if urlResp.status_code == 200:
            page = BeautifulSoup(urlResp.text,'lxml')
            self.videoUrl = (page.find('video')).get('src')
            self.success = True
        else:
            self.videoUrl = None

    
    def getVideoUrl(self):
        """获取视频地址
        :param self: self
        :param return: 返回视频地址videoUrl和解析状态success
        """
        self.headers = headers(self.url).buildHeader()
        self.__getvideoUrl()
        return {'success': self.success, 'videoUrl': self.videoUrl}
