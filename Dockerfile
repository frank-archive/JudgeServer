FROM alpine
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories
RUN apk update && \
    apk add cmake linux-headers libffi-dev\
            gcc g++ make git openjdk8 openssl-dev\
            libseccomp-dev python3-dev\
            python3 py3-pip python2
RUN adduser -D -u 1001 -s /bin/bash ctfd

WORKDIR /opt/judger
COPY ./requirements.txt /opt/judger
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN git clone https://github.com/frankli0324/Judger /opt/libjudger --depth=1
WORKDIR /opt/libjudger
RUN cmake .
RUN make; make install

WORKDIR /opt/libjudger/bindings/Python
RUN python3 setup.py install

WORKDIR /opt/judger
COPY . /opt/judger

USER 0
CMD ["gunicorn", "app:app", "-c", "gunicorn.conf"]
