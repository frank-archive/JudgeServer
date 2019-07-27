# CTFd::JudgeServer

本项目是[为MSSCTF修改的CTFd](https://github.com/frankli0324/CTFd)的附属品
用于评测ACM题目

## 部署

```bash
docker run -p {port}:5000 frankli0324/judge_server
```

与魔改CTFd一同通过docker-compose启动:
```yaml
services:
  ctfd:
    environment:
      - JUDGE_ADDR=judger
      - JUDGE_PORT=5000
    ...
  judger:
    image: frankli0324/judge_server
    restart: always
    environment:
      - JUDGE_BASEDIR=/opt/judger
      - JUDGE_TOKEN=your_token
      - DATABASE_URL=mysql+pymysql://username:password@localhost/judge
```

## dev

```bash
docker build .
...
```