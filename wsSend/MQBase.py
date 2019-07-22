# author: gorquan <gorquanwu@gmail.com>
# date: 2019.7.19
import pika
import logging
from queue import Queue

LOGGER = logging.getLogger(__name__)

class MQReceive(object):
    def __init__(self, MQServerHost, MQServerPort, MQServerExchange, MQServerExchange_type, MQServerUser, MQServerPassword, MQServerVirtualhost, MQServerQueue, MQServerPrefetch_count, MQServerAck=True, MQServerPersist=True):
         # 判断状态
        self.has_start = False
        # 声明消息接受条数
        self.prefetch_count = MQServerPrefetch_count
        # queue队列
        self.receive_queue = Queue(self.prefetch_count)
        # 链接
        self.conn = None
        # 信道
        self.channel = None
        # 消息持久化
        self.proprties = None
        # 主机
        self.host = MQServerHost
        # 端口
        self.port = MQServerPort
        # 交换机名称
        self.exchange = MQServerExchange
        # 交换机类型
        self.exchange_type = MQServerExchange_type
        # 用户名
        self.user = MQServerUser
        # 密码
        self.password = MQServerPassword
        # virtual_host
        self.virtual_host = MQServerVirtualhost
        # queue
        self.queue = MQServerQueue
        # 手动确认信息
        self.ack = MQServerAck
        # 消息持久化
        self.persist = MQServerPersist
        # 用户认证
        self.cerdentials = pika.PlainCredentials(self.user, self.password)
        # 链接
        self.param = pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=self.cerdentials, virtual_host=self.virtual_host)

    def open_channel(self):
        if self.check_alive():
            return
        else:
            self.clear()
        if not self.conn:
            # 建立链接
            try:
                self.conn = pika.BlockingConnection(self.param)
            except Exception as e:
                LOGGER.error("cant entablish connection is failed, the reason is %s" % e)
    
        if not self.channel: 
            try:
                # 开启信道
                self.channel = self.conn.channel()
                # 声明交换机
                self.channel.exchange_declare(
                    exchange=self.exchange, exchange_type=self.exchange_type, durable=self.persist)
                # 声明队列
                self.channel.queue_declare(queue=self.queue, durable=self.persist)
                # 绑定队列和交换机
                self.channel.queue_bind(
                    queue=self.queue, exchange=self.exchange, routing_key=self.queue)
                # 开启手动确认
                if self.ack:
                    self.channel.confirm_delivery()
                # 消息持久化
                if self.persist:
                    self.proprties = pika.BasicProperties(
                        delivery_mode=(2 if self.persist else 0))
            except Exception as e:
                LOGGER.error("cant entablish channel is failed, the reason is %s" % e)
                self.clear()
            
    def setQueue(self, queue_name):
        try:
            self.channel.basic_qos(prefetch_count=self.prefetch_count)
            self.channel.basic_consume(on_message_callback=self.handle,
                                   queue=queue_name)
            return True
        except Exception as e:
            LOGGER.error("cant set queue ,the reason is %s" % e)
            return False

    def start(self, queue_name):
        self.open_channel()
        if self.setQueue(queue_name):
            self.channel.start_consuming()

    def handle(self, channel, method, properties, body):
        self.receive_queue.put((body, self.conn, channel, method.delivery_tag))

    def clear(self):
        def close_conn():
            if self.conn and self.conn.is_open:
                self.conn.close()
            self.conn = None

        def close_channel():
            if self.channel and self.channel.is_open:
                self.channel.close()
            self.channel = None

        if not (self.conn and self.conn.is_open):
            close_conn()
        self.receive_queue = Queue(self.prefetch_count)
        close_channel()


    def check_alive(self):
        return self.conn and self.conn.is_open and self.channel and self.channel.is_open
