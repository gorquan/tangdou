# author: gorquanwu <Email: gorquanwu@gmail.com>
# date: 2019.7.20

import yaml
import logging
import logging.config
import os
import websocket
import json
import threading
from MQBase import MQBase
from queue import Queue
from functools import partial
import ast


log = ''

Config = ''
# websocket client
wsApp = ''


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


def sendMessage(message, rabbitmqConn, channel, ack_tag):
    try:
        ws = websocket.create_connection("ws://" + Config['websocket']['host'] + ':' + str(
            Config['websocket']['port']) + Config['websocket']['uri'])
        while True:
            ws.send(message)
            result = json.loads(ws.recv())
            if result['status'] == 'ok':
                log.info("message send success! the message id %s" %
                         result['data']['message_id'])
                rabbitmqConn.add_callback_threadsafe(
                    partial(channel.basic_ack, ack_tag))
                ws.close
                break
            # TODO:限定次数
            log.info(
                "the message : %s ,send error, send message again..." % message)
    except Exception as e:
        log.error("cant send the websocket data, the reason is %s" % e)


class MQReceive(MQBase):
    def __init__(self, *args, **kwargs):
        # 判断状态
        self.has_start = False
        # 声明消息接受条数
        self.prefetch_count = kwargs.get(
            'prefetch_count', Config['sendRabbitmq']['prefetch_count'])
        # queue队列
        self.receive_queue = Queue(self.prefetch_count)
        super().__init__(*args, **kwargs)

    def setQueue(self, queue_name):
        # Todo: try... except
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(on_message_callback=self.handle,
                                   queue=queue_name)
        return True

    def start(self, queue_name):
        self.open_channel()
        if self.setQueue(queue_name):
            self.channel.start_consuming()

    def handle(self, channel, method, properties, body):
        self.receive_queue.put((body, self.conn, channel, method.delivery_tag))

    def clear(self):
        self.receive_queue = Queue(self.prefetch_count)
        super().clear()


def consumer(receive):
    receive.start(Config['sendRabbitmq']['queue'])


def deal_message(receive):
    while True:
        msg, conn, channel, ack_tag = receive.receive_queue.get()
        message = msg.decode('utf8', errors='ignore')
        sendMessage(message, conn, channel, ack_tag)


if __name__ == "__main__":
    baseDir = os.path.dirname(os.path.abspath(__file__))
    setLog(baseDir, 'logConfig.yaml')
    setConfig(baseDir, 'config.yaml')
    receive = MQReceive(host=Config['sendRabbitmq']['host'], port=Config['sendRabbitmq']['port'], exchange=Config['sendRabbitmq']['exchange'], exchange_type=Config['sendRabbitmq']['exchange_type'],
                        user=Config['sendRabbitmq']['user'], password=Config['sendRabbitmq']['password'], virtualhost=Config['sendRabbitmq']['virtualhost'], queue=Config['sendRabbitmq']['queue'])
    threading.Thread(target=consumer, args=(receive,)).start()
    threading.Thread(target=deal_message, args=(receive,)).start()
