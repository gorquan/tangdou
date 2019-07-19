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
        Thread(target=producer,args=(message, )).start()
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

if __name__ == "__main__":
    setLog("logConfig.yaml")
    initConnect()
