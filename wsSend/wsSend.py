# author: gorquanwu <Email: gorquanwu@gmail.com>
# date: 2019.7.20

import yaml
import logging
import logging.config
import os
import websocket
import json
import threading
from MQBase import MQReceive
from functools import partial


def setLog(baseDir, filename):
    '''
    To set log
    :param filename: logging config filename
    :return: log
    '''
    logConfigPath = baseDir + '/' + filename
    try:
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
        return log
    except IOError:
        exit(1)


def setConfig(baseDir, filename, log):
    '''
    To get Config
    :param filename: config filename
    :return: Config
    '''
    configPath = baseDir + '/' + filename
    try:
        with open(configPath, 'r') as f:
            Config = yaml.load(f.read())
        log.debug("load the config success...")
        return Config
    except IOError as e:
        log.error("load the config error! the reason: %s" % e)
        exit(1)


def sendMessage(message, recvConn, recvChannel, recvAck_tag, ws, sendCount, log):
    try:
        sendCount = sendCount
        count = 0
        while True:
            ws.send(message)
            result = json.loads(ws.recv())
            if result['status'] == 'ok':
                log.info("message send success! the message id %s" %
                         result['data']['message_id'])
                recvConn.add_callback_threadsafe(
                    partial(recvChannel.basic_ack, recvAck_tag))
                break
            if sendCount <= count:
                log.error(
                    "the message : %s isn't send, now throw array the message" % message)
                recvConn.add_callback_threadsafe(
                    partial(recvChannel.basic_ack, recvAck_tag))
                break
            count += 1
            log.info(
                "the message : %s ,send error, send message again..." % message)
    except Exception as e:
        log.error("cant send the message: %s, the reason is %s" % (message,e))
        exit(1)


def consumer(receiver, queue, log):
    try:
        receiver.start(queue)
    except Exception as e:
        log.error("failed to start the rabbitmq customer,the reason is %s" % e)


def deal_message(receiver, WSHost, WSPort, WSUri, sendCount, log):
    try:
        ws = websocket.create_connection(
        "ws://" + WSHost + ':' + WSPort + WSUri)
        log.info("connect to websocket server: ws://%s:%s%s success" % (WSHost,WSPort,WSUri))
        while True:
            msg, recvConn, recvChannel, recvAck_tag = receiver.receive_queue.get()
            message = msg.decode('utf8', errors='ignore')
            threading.Thread(target=sendMessage, args=(message,recvConn,recvChannel,recvAck_tag,ws,sendCount,log,)).start()
    except Exception as e:
        log.error("connect to websocket server: ws://%s:%s%s failed, the reason is %s" % (WSHost,WSPort,WSUri,e))
        exit(1)


if __name__ == "__main__":
    baseDir = os.path.dirname(os.path.abspath(__file__))
    log = setLog(baseDir, 'logConfig.yaml')
    Config = setConfig(baseDir, 'config.yaml', log)
    receiver = MQReceive(MQServerHost=Config['sendRabbitmq']['host'], MQServerPort=Config['sendRabbitmq']['port'], MQServerExchange=Config['sendRabbitmq']['exchange'], MQServerExchange_type=Config['sendRabbitmq']['exchange_type'], MQServerUser=Config['sendRabbitmq']['user'], MQServerPassword=Config['sendRabbitmq']['password'], MQServerVirtualhost=Config['sendRabbitmq']['virtualhost'], MQServerQueue=Config['sendRabbitmq']['queue'], MQServerPrefetch_count=Config['sendRabbitmq']['prefetch_count'])
    threading.Thread(target=consumer, args=(
        receiver, Config['sendRabbitmq']['queue'], log,)).start()
    threading.Thread(target=deal_message, args=(
        receiver, Config['websocket']['host'], str(Config['websocket']['port']), Config['websocket']['uri'], Config['sendCount']['count'], log,)).start()
