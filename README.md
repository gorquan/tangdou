

#### QQMessage Frame

##### 使用方式

``` shell
    # 对于zsh
    bash start.sh
    # bash
    ./start.sh
```

##### 已知问题与未来功能规划

* 待处理问题 
    - [x] 添加好友会发生报错
    - [x] 糖豆APP分享出现空链接导致报错
    - [x] 统一消息格式（dict）
        - wsRecv(dict) -> queue(str) -> wsMiddle(dict) -> queue(str) -> wsSend(str) -> websocket(str) 
    - [x] 处理消息基类
    - [ ] 处理剩下消息
    - [ ] 列出站点提供支持
    - [ ] 添加数据库，提供历史数据查询
    - [ ] 中间件使用异步处理（requests和数据库)
    - [x] 详细化所抛出错误
    - [ ] 处理LOG文件位置
    - [x] 重构wsSend.py和MQReceive类
    - [ ] 重构wsRecv.py和MQSend类
    - [ ] 重构formatMessage 函数
    - [x] 重构wsMiddle和MQBase类
    - [x] 测试wsSend端websocket是否会断开
    - [x] 空消息会出现报错
    - [ ] 测试糖豆APP分享是否出现报错
    - [ ] 测试空消息是否报错
    - [ ] 多表情存在问题
    - [ ] 送礼物无法获取数据包
    - [ ] 文字加上表情存在问题
    - [ ] 补全APP分享属性
    - [ ] 讨论组情况未处理
    - [ ] 群聊情况未处理
    - [ ] 视频类未加try except
    - [ ] 通知类信息报错
    
* 未来功能
    - [ ] 下载ts文件
    - [ ] 合并mp4文件
    - [ ] 提供下载
    
##### 参与项目

* 使用过程中出现问题、Bug或有其他意见建议，欢迎提issue
* 如果有自己的想法并实现, 欢迎提pr

##### 感谢

  * [docker-wine-coolq](https://github.com/CoolQ/docker-wine-coolq) [@CoolQ](https://github.com/CoolQ)
  * [coolq-http-api](https://github.com/richardchien/coolq-http-api) [@richardchien](https://github.com/richardchien/)

##### 备注

* 仅为个人学习使用，勿用于商业用途

