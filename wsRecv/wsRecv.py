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

Config = ''


def setLog(baseDir, filename):
    '''
    To set log
    :param filename: logging config filename
    :return:
    '''
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


def setConfig(baseDir, filename):
    '''
    To get Config
    :param filename: config filename
    :return:
    '''
    configPath = baseDir + '/' + filename
    try:
        with open(configPath, 'r') as f:
            global Config
            Config = yaml.load(f.read())
        log.debug("load the config success...")
    except IOError as e:
        log.error("load the config error! the reason: %s" % e)
        exit(1)


def outputMessage(ws, message):
    try:
        print(message)
        message = formatMessage(message)
        log.info("format message success! the message is %s" % message)
        Thread(target=producer, args=(str(message), )).start()
        log.debug(
            "recive the message, start a thread to save in the rabbitmq server"
        )
    except Exception as e:
        log.error("cant start the thread, the reason is %s" % e)


def outputError(ws, message):
    log.error(message)


def outputClose(ws):
    log.info("close the websocket connection, and then will reconnect")
    initConnect()


def initConnect():
    try:
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://" + Config['websocket']['host'] +
                                    ':' + str(Config['websocket']['port']) +
                                    Config['websocket']['uri'],
                                    on_message=outputMessage,
                                    on_error=outputError,
                                    on_close=outputClose)
        log.info("start the websocket connection success")
        ws.run_forever()
    except Exception as e:
        log.error("cant init the websocket connection, the reason is %s" % e)


class MQSender(MQBase):
    def send(self, route, msg):
        def sendMessage():
            try:
                self.open_channel()
                self.channel.basic_publish(exchange=self.exchange,
                                           routing_key=route,
                                           body=msg,
                                           properties=self.proprties)
                success = True
            except Exception as e:
                log.error("cant save the message to server,the reason is: %s" %
                          e)
                success = False
            return success

        result = sendMessage() or sendMessage()
        if not result:
            self.clear()
        return result


def producer(message):
    sender = MQSender(host=Config['receiveRabbitmq']['host'],
                      port=Config['receiveRabbitmq']['port'],
                      exchange=Config['receiveRabbitmq']['exchange'],
                      exchange_type=Config['receiveRabbitmq']['exchange_type'],
                      user=Config['receiveRabbitmq']['user'],
                      password=Config['receiveRabbitmq']['password'],
                      virtualhost=Config['receiveRabbitmq']['virtual_host'],
                      queue=Config['receiveRabbitmq']['queue'])
    sender.send(Config['receiveRabbitmq']['queue'], message)


def formatMessage(message):
    messageJson = {}
    message = html.unescape(message)
    message = message.replace('\\"', '')
    message = message.replace("'", '"')
    message = eval(message)
    messageJson['post_type'] = message['post_type']
    messageJson['time'] = message['time']
    postType = message['post_type']
    if postType == 'message':
        messageJson['user_id'] = message['user_id']
        messageJson['message_type'] = message['message_type']
        messageJson['id'] = message['message_id']
        messagebody = message['message']
        print('messagebody: ' + messagebody)
        if messagebody.startswith('[CQ'):
            messagebody = messagebody.lstrip('[')
            messagebody = messagebody.rstrip(']')
            # APP分享
            if messagebody.startswith('CQ:rich,content='):
                messageJson['msg_body_type'] = 'Shared'
                messagebody = (messagebody.split(',content='))[1]
                messagebody = (messagebody.split(',title='))[0]
                messageJson['message'] = {
                    "SharedTitle":
                    (messagebody.split(',desc:'))[0].lstrip("{news:{title:"),
                    "SharedTag":
                    (((messagebody.split(',tag:'))[1]).split(',jumpUrl'))[0],
                    "SharedJumpurl":
                    (((messagebody.split(',jumpUrl:'))[1]).split(',appid:'))[0]
                }
            # 文档
            elif messagebody.startswith('CQ:rich,text='):
                messageJson['msg_body_type'] = 'Document'
                messagebody = messagebody.split(',')
                messageJson['message'] = {
                    "DocumentText": messagebody[1].lstrip('text='),
                    "DocumentUrl": messagebody[2].lstrip('url=')
                }
            # 图片
            elif messagebody.startswith('CQ:image'):
                messageJson['msg_body_type'] = 'Image'
                messagebody = messagebody.split(',')
                messageJson['message'] = {
                    "ImageFile": messagebody[1].lstrip('file='),
                    "ImageUrl": messagebody[2].lstrip('url=')
                }
            # 语音
            elif messagebody.startswith('CQ:record'):
                messageJson['msg_body_type'] = 'Record'
                messagebody = messagebody.split(',')
                if len(messagebody) == 3:
                    RecordMagic = True
                else:
                    RecordMagic = False
                messageJson['message'] = {
                    "RecordFile": messagebody[1].lstrip('file='),
                    "RecordMagic": RecordMagic
                }
            # 表情
            elif messagebody.startswith('CQ:face'):
                messageJson['msg_body_type'] = 'Face'
                faceId = {}
                if '][' in messagebody:
                    messagebodys = messagebody.split('][')
                    for i in len(messagebodys):
                        messagebody = (messagebodys[i]).split(',')
                        faceId[i] = messagebody[1].lstrip('id=')
                else:
                    messagebody = messagebody.split(',')
                    faceId[0] = messagebody[1].lstrip('id=')
                messageJson['message'] = {"FaceId": faceId}
            # 官方表情包
            elif messagebody.startswith('CQ:bface'):
                messageJson['msg_body_type'] = 'Bface'
                messagebody = messagebody.split(',')
                messageJson['message'] = {
                    "FaceId": messagebody[1].lstrip('id='),
                    "FaceP": messagebody[2].lstrip('p=')
                }
            # 戳一戳
            elif messagebody.startswith('CQ:shake'):
                messageJson['msg_body_type'] = 'Shake'
                messagebody = messagebody.split(',')
                if len(message) == 3:
                    shakeType = (messagebody[2]).lstrip('type=')
                else:
                    shakeType = 'default'
                messageJson['message'] = {
                    "ShakeId": (messagebody[1]).lstrip('id='),
                    'ShakeType': shakeType
                }
            # 地理位置
            elif messagebody.startswith('CQ:location'):
                messageJson['msg_body_type'] = 'Location'
                messagebody = messagebody.split(',')
                messageJson['message'] = {
                    "LocationContent": (messagebody[1]).lstrip('content='),
                    "LocationLat": (messagebody[2]).lstrip('lat='),
                    "LocationLon": (messagebody[3]).lstrip('lon='),
                    "LocationStyle": (messagebody[4]).lstrip('style=')
                }
            # 名片
            elif messagebody.startswith('CQ:contact'):
                messageJson['msg_body_type'] = 'Contact'
                messagebody = messagebody.split(',')
                messageJson['message'] = {
                    "ContactId": (messagebody[1]).lstrip('id='),
                    "ContactType": (messagebody[2]).lstrip('type=')
                }
            # 厘米秀
            elif messagebody.startswith('CQ:show'):
                messageJson['msg_body_type'] = 'Show'
                messagebody = messagebody.split(',')
                messageJson['message'] = {
                    'ShowId': (messagebody[2]).lstrip('id=')
                }
        # 其他不支持的信息视为文本信息
        else:
            messageJson['msg_body_type'] = 'Text'
            messageJson['message'] = messagebody
    # 好友请求信息
    elif postType == 'request':
        messageJson['comment'] = message['comment']
        messageJson['flag'] = message['flag']
        messageJson['request_type'] = message['request_type']
        if message['request_type'] == 'friend':
            messageJson['message'] = {"Request_ID": message['user_id']}
        elif message['request_type'] == "group":
            messageJson['message'] = {
                "Group_ID": message['group_id'],
                "Invite_ID": message['user_id']
            }
    # 通知消息
    elif postType == 'notice':
        messageJson['notice_type'] = message['notice_type']
        # 群操作通知
        if message['notice_type']  in ('group_decrease', 'group_increase'):
            messageJson['message'] = {
                "sub_type": message['sub_type'],
                "group_id": message["group_id"],
                "operator_id": message['operator_id'],
                "process_id": message['process_id']
            }
        else:
            pass
    # 其他信息
    else:
        pass
    return messageJson


if __name__ == "__main__":
    baseDir = os.path.dirname(os.path.abspath(__file__))
    setLog(baseDir, "logConfig.yaml")
    setConfig(baseDir, 'config.yaml')
    initConnect()
