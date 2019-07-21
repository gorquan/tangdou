# author: gorquanwu <gorquanwu@gmail.com>
# date: 2019.7.20

import logging
import yaml
import os
import logging.config
from MQBase import MQBase
from queue import Queue
import threading
import json
from functools import partial
import ast

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


class MQRecver(MQBase):
    def __init__(self, *args, **kwargs):
        self.has_start = False
        self.prefetch_count = kwargs.get(
            'prefetch_count', Config['receiveRabbitmq']['prefetch_count'])
        self.revice_queue = Queue(self.prefetch_count)
        super().__init__(*args, **kwargs)

    def setQueue(self, queue_name):
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(
            on_message_callback=self.handle, queue=queue_name)
        return True

    def start(self, queue_name):
        if self.has_start:
            return
        self.open_channel()
        if self.setQueue(queue_name):
            self.channel.start_consuming()

    def handle(self, channel, method, properties, body):
        self.revice_queue.put((body, self.conn, channel, method.delivery_tag))

    def clear(self):
        self.revice_queue = Queue(self.prefetch_count)
        super().clear()


class MQSender(MQBase):
    def send(self, route, msg):
        def sendMessage():
            try:
                self.open_channel()
                self.channel.basic_publish(
                    exchange=self.exchange, routing_key=route, body=msg, properties=self.proprties)
                success = True
            except Exception as e:
                log.error(
                    "cant save the deal message to server, the resason is %s" % e)
                success = False
            return success
        result = sendMessage() or sendMessage()
        if not result:
            self.clear()
        return result


def SendMsg(message, revcConn, revcChannel, recvAck_tag):
    sender = MQSender(host=Config['sendRabbitmq']['host'], port=Config['sendRabbitmq']['port'], exchange=Config['sendRabbitmq']['exchange'], exchange_type=Config['sendRabbitmq']['exchange_type'],
                      user=Config['sendRabbitmq']['user'], password=Config['sendRabbitmq']['password'], virtualhost=Config['sendRabbitmq']['virtual_host'], queue=Config['sendRabbitmq']['queue'])
    result = sender.send(Config['sendRabbitmq']['queue'], str(message))
    if result:
        revcConn.add_callback_threadsafe(
            partial(revcChannel.basic_ack, recvAck_tag))


def consumer(receive):
    receive.start(Config['receiveRabbitmq']['queue'])


def getMsg(reveive):
    while True:
        recvMsg, recvConn, recvChannel, recvAck_tag = reveive.revice_queue.get()
        message = recvMsg.decode('utf8', errors='ignore')
        log.info('get message! message is %s, then will deal with new thread..' % message)
        threading.Thread(target=dealMsg, args=(
            message, recvConn, recvChannel, recvAck_tag,)).start()


def dealMsg(recvMsg, recvConn, recvChannel, recvAck_tag):
    messageList = ast.literal_eval(recvMsg)
    postType = messageList['post_type']
    msgType = messageList['msg_body_type']
    if postType == 'request':
        import requestMsg
        rMsg = requestMsg.RequestMsg(messageList['comment'], messageList['flag'])
        replyMessage = rMsg.accept()
    elif postType == 'message':
        if msgType == 'Shared':
            import messageShared
            msgShared = messageShared.SharedMessage(
                messageList['SharedTag'], messageList['SharedTitle'], messageList['SharedJumpurl'], messageList['user_id'])
            replyMessage = msgShared.sendMessage()
        elif msgType == 'Document':
            pass
        elif msgType == 'Image':
            pass
        elif msgType == 'Record':
            pass
        elif msgType == 'Face':
            pass
        elif msgType == 'Shake':
            pass
        elif msgType == 'Location':
            pass
        elif msgType == 'Contact':
            pass
        elif msgType == 'Show':
            pass
        elif msgType == 'Text':
            import message
            msgText = message.Message(messageList['user_id'],messageList['message'])
            replyMessage = msgText.sendMessage()
    SendMsg(replyMessage, recvConn, recvChannel, recvAck_tag)


if __name__ == "__main__":
    baseDir = os.path.dirname(os.path.abspath(__file__))
    setLog(baseDir, 'logConfig.yaml')
    setConfig(baseDir, 'config.yaml')
    receive = MQRecver(host=Config['receiveRabbitmq']['host'], port=Config['receiveRabbitmq']['port'], exchange=Config['receiveRabbitmq']['exchange'], exchange_type=Config['receiveRabbitmq']['exchange_type'],
                       user=Config['receiveRabbitmq']['user'], password=Config['receiveRabbitmq']['password'], virtualhost=Config['receiveRabbitmq']['virtual_host'], queue=Config['receiveRabbitmq']['queue'])
    threading.Thread(target=consumer, args=(receive,)).start()
    threading.Thread(target=getMsg, args=(receive,)).start()
