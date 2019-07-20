FROM alpine
LABEL maintainer="gorquanwu <gorquanwu@gmail.com>"

ENV TZ 'Asia/Shanghai'

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk update && apk upgrade
RUN apk add --no-cache python3 python3-dev

COPY ["MQBase.py", "wsRecv.py", "requirement.txt", "./"]

RUN pip3 install -i https://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com -r requirement.txt

CMD ["python3 wsclient.py"]


