# author: gorquan <Email:gorquanwu@gmail.com>
# date: 2019.7.19

import websocket
import logging
import logging.config
import yaml
import os
from threading import Thread
from MQBase import MQBase
import pika
import html


log = ''


def setLog(filename):
    '''
    To set log
    :param filename: logging config filename
    :return:
    '''
    baseDir = os.path.dirname(os.path.abspath(__file__))
    logConfigPath = baseDir + '/' + filename
    try:
        global log
        if os.path.exists(logConfigPath):
            with open(logConfigPath, 'r') as f:
                logConfig = yaml.load(f.read())
            logging.config.dictConfig(logConfig)
            log = logging.getLogger("wsclientLog")
            log.info("set log success..")
        else:
            logging.basicConfig(level=logging.INFO)
            log = logging.getLogger("wsclientLog")
            log.info("set default success..")
    except IOError:
        exit(1)

def outputMessage(ws,message):
    try:
        message = formatMessage(message)
        log.info("format message success! the message is %s" % message)
        Thread(target=producer,args=(str(message), )).start()
        log.debug("recive the message, start a thread to save in the rabbitmq server")
    except Exception as e:
        log.error("cant start the thread, the reason is %s" % e)

def outputError(ws,message):
    log.error(message)

def outputClose(ws):
    log.info("close the websocket connection, and then will reconnect")
    initConnect()


def initConnect():
    try:
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://127.0.0.1:5800/event/",
                                    on_message = outputMessage,
                                    on_error = outputError,
                                    on_close = outputClose)
        ws.run_forever()
        log.info("start the websocket connection success")
    except Exception as e:
        log.error("cant init the websocket connection, the reason is %s" % e)


class MQSender(MQBase):
    def send(self,route,msg):
        def sendMessage():
            try:
                self.open_channel()
                success = self.channel.basic_publish(exchange=self.exchange,routing_key=route,body=msg,properties=self.proprties)
            except:
                success = False
            return success
        result = sendMessage() or sendMessage()
        if not result:
            self.clear()
        return result
    

def producer(message):
    sender = MQSender(host="127.0.0.1",port=5672,exchange="",exchange_type="direct",user='user', password='123456',virtualhost = '/', queue = 'test')
    sender.send('test', message)

def formatMessage(message):
    messageJson = {}
    message = html.unescape(message)
    message = message.replace('\\"', '')
    message = message.replace("'",'"') 
    message = eval(message)
    messageJson['post_type'] = message['post_type']
    messageJson['user_id'] = message['user_id']
    messageJson['time'] = message['time']
    if message['post_type'] == 'message':
        messageJson['message_type'] = message['message_type']
        messageJson['id'] = message['message_id']
        messagebody = message['message']
        print('messagebody: ' + messagebody)
        if messagebody.startswith('[CQ'):
            messagebody = messagebody.lstrip('[')
            messagebody = messagebody.rstrip(']')
            if messagebody.startswith('CQ:rich'):
                if messagebody.startswith('CQ:rich,content='):
                    messageJson['msg_body_type'] = 'Shared'
                    messagebody = (messagebody.split(',content='))[1]
                    messagebody = (messagebody.split(',title='))[0]
                    messageJson['SharedTitle'] = (messagebody.split(',desc:'))[0].lstrip("{news:{title:")
                    messageJson['SharedTag'] = (((messagebody.split(',tag:'))[1]).split(',jumpUrl'))[0]
                    messageJson['SharedJumpurl'] = (((messagebody.split(',jumpUrl:'))[1]).split(',appid:'))[0]
                # 文档
                elif messagebody.startswith('CQ:rich,text='):
                    messageJson['msg_body_type'] = 'Document'
                    messagebody = messagebody.split(',')
                    messageJson['DocumentText'] = messagebody[1].lstrip('text=')
                    messageJson['DocumentUrl'] = messagebody[2].lstrip('url=')
            # 图片
            elif messagebody.startswith('CQ:image'):
                messageJson['msg_body_type'] = 'Image'
                messagebody = messagebody.split(',')
                messageJson['ImageFile'] = messagebody[1].lstrip('file=')
                messageJson['ImageUrl'] = messagebody[2].lstrip('url=') 
            # 语音
            elif messagebody.startswith('CQ:record'):
                messageJson['msg_body_type'] = 'Record'
                messagebody = messagebody.split(',')
                messageJson['RecordFile'] = messagebody[1].lstrip('file=')
            # 大头贴
            elif messagebody.startswith('CQ:face') or messagebody.startswith('CQ:bface'):
                messageJson['msg_body_type'] = 'Face'
                messagebody = messagebody.split(',')
                messageJson['FaceId'] = messagebody[1].lstrip('id=')
            # 戳一戳
            elif messagebody.startswith('CQ:shake'):
                messageJson['msg_body_type'] = 'Shake'
                messagebody = messagebody.split(',')
                messageJson['ShakeId'] = (messagebody[1]).lstrip('id=')
            # 地理位置
            elif messagebody.startswith('CQ:location'):
                messageJson['msg_body_type'] = 'Location'
                messagebody = messagebody.split(',')
                messageJson['LocationContent'] = (messagebody[1]).lstrip('content=')
                messageJson['LocationLat'] = (messagebody[2]).lstrip('lat=')
                messageJson['LocationLon'] = (messagebody[3]).lstrip('lon=')
            # 名片
            elif messagebody.startswith('CQ:contact'):
                messageJson['msg_body_type'] = 'Contact'
                messagebody = messagebody.split(',')
                messageJson['ContactId'] = (messagebody[1]).lstrip('id=')
                messageJson['ContactType'] = (messagebody[2]).lstrip('type=')
            elif messagebody.startswith('CQ:show'):
                messageJson['msg_body_type'] = 'Show'
                messagebody = messagebody.split(',')
                messageJson['ShowId'] = (messagebody[2]).lstrip('id=')
        # 其他不支持的信息视为文本信息
        else:
            messageJson['msg_body_type'] = 'Text'
            messageJson['message'] = messagebody
    # 好友请求信息
    elif message['post_type'] == 'request':
        messageJson['comment'] = message['comment']
    # 其他信息
    else:
        pass
    return messageJson


if __name__ == "__main__":
    setLog("logConfig.yaml")
    initConnect()
