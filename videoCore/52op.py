# author: gorquan <gorquanwu@gmail.com>
# date: 2019.8.16

import requests
from urllib.parse import urlparse


class op52(object):
    """获取52op广场舞视频类
    :param object: object
    """
    def __init__(self, url):
        self.success = False
        self.url = url
        self.videoUrl = None

    def __getvideoUrl(self):
        """解析网页获取视频地址
        :param self: self
        """
        videoID = ((urlparse(self.url).path).lstrip('/video/')).rstrip('.html')
        self.videoUrl = 'https://52op.net/flvData/d.aspx?id=' + videoID
        self.success = True

    def getVideoUrl(self):
        """获取视频地址
        :param self: self
        :param return: 返回视频地址videoUrl和解析状态success
        """
        self.__getvideoUrl()
        return {'success': self.success, 'videoUrl': self.videoUrl}
