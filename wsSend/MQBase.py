# author: gorquan <gorquanwu@gmail.com>
# date: 2019.7.19
import pika


class MQBase(object):
    def __init__(self, host, port, exchange, exchange_type, user, password, virtualhost, queue, ack=True, persist=True):
        # 链接
        self.conn = None
        # 信道
        self.channel = None
        # 消息持久化
        self.proprties = None
        # 主机
        self.host = host
        # 端口
        self.port = port
        # 交换机名称
        self.exchange = exchange
        # 交换机类型
        self.exchange_type = exchange_type
        # 用户名
        self.user = user
        # 密码
        self.password = password
        # virtual_host
        self.virtual_host = virtualhost
        # queue
        self.queue = queue
        # 手动确认信息
        self.ack = ack
        # 消息持久化
        self.persist = persist
        self.cerdentials = pika.PlainCredentials(self.user, self.password)
        self.param = pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=self.cerdentials, virtual_host=self.virtual_host)

    def open_channel(self):
        if self.check_alive():
            return
        else:
            self.clear()
        if not self.conn:
            # 建立链接
            self.conn = pika.BlockingConnection(self.param)
        if not self.channel:
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
            self.proprties = pika.BasicProperties(
                delivery_mode=(2 if self.persist else 0))

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
        close_channel()

    def check_alive(self):
        return self.conn and self.conn.is_open and self.channel and self.channel.is_open
