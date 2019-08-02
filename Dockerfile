FROM alpine
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk update && \
    apk add cmake linux-headers libffi-dev\
            gcc g++ make git openjdk8 openssl-dev\
            libseccomp-dev python3-dev\
            python3 py3-pip python2

COPY requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN virtualenv /opt/pyenv2 --python=/usr/bin/python2 --no-setuptools --no-pip --no-wheel
RUN virtualenv /opt/pyenv3 --python=/usr/bin/python3 --no-setuptools --no-pip --no-wheel

RUN git clone https://github.com/QingdaoU/Judger /opt/libjudger --depth=1
WORKDIR /opt/libjudger
RUN cmake .
RUN make; make install

WORKDIR /opt/libjudger/bindings/Python
RUN python3 setup.py install

WORKDIR /opt/judger

COPY src /opt/judger
COPY docker-entrypoint.sh /opt/judger
COPY worker.json /opt/judger

RUN chmod +x /opt/judger/docker-entrypoint.sh

USER 0
ENTRYPOINT ["/opt/judger/docker-entrypoint.sh"]
