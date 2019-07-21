# author: gorquan <gorquanwu@gmail.com>
# date: 2019.7.21

import json



class RequestMsg():
    def __init__(self, comment, flag):
        self.comment = comment
        self.flag = flag

    def accept(self):
        replyMessage = {"action": "set_friend_add_request",
                        "params": {
                            "flag": self.flag,
                            "approve": "true"
                        }}
        return json.dumps(replyMessage)

    def refuse(self):
        replyMessage = {"action": "set_friend_add_request",
                        "params": {
                            "flag": self.flag,
                            "approve": "false"
                        }}
        return json.dumps(replyMessage)


class GroupRequestMsg(RequestMsg):
    def __init__(self, subType, flag):
        self.subType = subType
        super().__init__(flag)

    def accept(self):
        replyMessage = {"action": "set_group_add_request",
                        "params": {
                            "flag": self.flag,
                            "sub_type": self.subType,
                            "approve": "true"
                        }}
        return json.dumps(replyMessage)

    def refuse(self):
        replyMessage = {"action": "set_group_add_request",
                        "params": {
                            "flag": self.flag,
                            "sub_type": self.subType,
                            "approve": "false"
                        }}
        return json.dumps(replyMessage)
