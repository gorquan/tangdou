# author: gorquan <gorquanwu@gmail.com>
# date: 2019.8.15

import json
from urllib.parse import urlparse
from urllib.parse import parse_qs


class baidu(object):
    """获取百度视频类
    :param object: object
    """
    def __init__(self,url):
        """baidu class init
        :param self: self
        :param url: 视频页面地址
        """
        self.success = False
        self.url = url
        self.videoUrl = None
    
    def __getvideoUrl(self):
        """解析url获取视频地址
        :param self: self
        """
        urlArray = json.loads(((parse_qs((urlparse(self.url)).query))['ext'])[0])
        self.videoUrl = urlArray['src']
        self.success = True

    def getVideoUrl(self):
        """获取视频地址
        :param self: self
        :param return: 返回视频地址videoUrl和解析状态success
        """
        self.__getvideoUrl()
        return self.videoUrl
