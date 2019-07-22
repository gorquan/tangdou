# author: gorquanwu <gorquanwu@gmail.com>
# date: 2019.7.20

import logging
import yaml
import os
import logging.config
from MQBase import MQSender, MQReciver
from queue import Queue
import threading
import json
from functools import partial
import ast


def setLog(baseDir, filename):
    '''
    To set log
    :param filename: logging config filename
    :return:
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


def setConfig(baseDir, filename):
    '''
    To get Config
    :param filename: config filename
    :return:
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


def SendMsg(message, revcConn, revcChannel, recvAck_tag, sender, queue, log):
    result = sender.send(queue, str(message))
    if result:
        revcConn.add_callback_threadsafe(
            partial(revcChannel.basic_ack, recvAck_tag))
        log.info("message: %s add to queue success.." % message)
    else:
        log.error("message: %s add to failed, now exit the program" % message)
        exit(1)


def consumer(receiver, queue, log):
    try:
        receiver.start(queue)
    except Exception as e:
        log.error("the receiving end cant start. the reason is:%s" % e)


def getMsg(reveiver, sender, log):
    while True:
        recvMsg, recvConn, recvChannel, recvAck_tag = reveiver.revice_queue.get()
        message = recvMsg.decode('utf8', errors='ignore')
        log.info(
            'get message! message is %s, then will deal with new thread..' % message)
        threading.Thread(target=dealMsg, args=(
            message, recvConn, recvChannel, recvAck_tag, sender, log,)).start()


def dealMsg(recvMsg, recvConn, recvChannel, recvAck_tag, sender, queue, log):
    messageList = ast.literal_eval(recvMsg)
    postType = messageList['post_type']
    msgType = messageList['msg_body_type']
    if postType == 'request':
        import requestMsg
        rMsg = requestMsg.RequestMsg(
            messageList['comment'], messageList['flag'])
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
            msgText = message.Message(
                messageList['user_id'], messageList['message'])
            replyMessage = msgText.sendMessage()
    log.info(
        "deal message success, the message is: %s, will send to queue..." % replyMessage)
    SendMsg(replyMessage, recvConn, recvChannel,
            recvAck_tag, sender, queue, log)


if __name__ == "__main__":
    baseDir = os.path.dirname(os.path.abspath(__file__))
    log = setLog(baseDir, 'logConfig.yaml')
    Config = setConfig(baseDir, 'config.yaml')
    receiver = MQReciver(MQServerHost=Config['receiveRabbitmq']['host'], MQServerPort=Config['receiveRabbitmq']['port'], MQServerExchange=Config['receiveRabbitmq']['exchange'], MQServerExchange_type=Config['receiveRabbitmq']['exchange_type'],
                         MQServerUser=Config['receiveRabbitmq']['user'], MQServerPassword=Config['receiveRabbitmq']['password'], MQServerVirtualhost=Config['receiveRabbitmq']['virtual_host'], MQServerQueue=Config['receiveRabbitmq']['queue'], MQServerPrefetchCount=Config['receiveRabbitmq']['prefetch_count'])
    sender = MQSender(MQServerHost=Config['sendRabbitmq']['host'], MQServerPort=Config['sendRabbitmq']['port'], MQServerExchange=Config['sendRabbitmq']['exchange'], MQServerExchange_type=Config['sendRabbitmq']['exchange_type'],
                      MQServerUser=Config['sendRabbitmq']['user'], MQServerPassword=Config['sendRabbitmq']['password'], MQServerVirtualhost=Config['sendRabbitmq']['virtual_host'], MQServerQueue=Config['sendRabbitmq']['queue'])
    threading.Thread(target=consumer, args=(
        receiver, Config['receiveRabbitmq']['queue'], log,)).start()
    threading.Thread(target=getMsg, args=(receiver, sender,
                                          Config['sendRabbitmq']['queue'], log,)).start()
