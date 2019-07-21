# author: gorquan <gorquanwu@gmail.com>
# date: 2019.7.21

import json


class Message():
    def __init__(self, user_id, msg):
        self.user_id = user_id
        self.msg = msg

    def sendMessage(self):
        replyMessage = {"action": "send_private_msg",
                        "params": {
                            "user_id": self.user_id,
                            "message": self.msg,
                        }}
        return json.dumps(replyMessage)

    def sendGroupMessage(self):
        replyMessage = {"action": "send_group_msg",
                        "params": {
                            "group_id": self.user_id,
                            "message": self.msg,
                        }}
        return json.dumps(replyMessage)

    def sendDiscussMessage(self):
        replyMessage = {"action": "send_discuss_msg",
                        "params": {
                            "discuss_id": self.user_id,
                            "message": self.msg
                        }}
        return json.dumps(replyMessage)
