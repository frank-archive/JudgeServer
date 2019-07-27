FROM python:3.7.3-alpine
RUN apk update && \
    apk add cmake linux-headers libffi-dev gcc g++ make py3-pip git openssl-dev libseccomp-dev
RUN adduser -D -u 1001 -s /bin/bash ctfd
RUN pip install gunicorn gevent flask -i https://pypi.tuna.tsinghua.edu.cn/simple

ARG CACHEBUST=1 
RUN git clone https://github.com/QingdaoU/Judger /opt/libjudger --depth=1
WORKDIR /opt/libjudger
RUN cmake .
RUN make; make install

WORKDIR /opt/libjudger/bindings/Python
RUN python3 setup.py install

WORKDIR /opt/judger
COPY . /opt/judger

USER 0
CMD ["gunicorn", "app:app", "-c", "gunicorn.conf"]
