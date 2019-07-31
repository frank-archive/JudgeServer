# CTFd::JudgeServer

本项目是[为MSSCTF修改的CTFd](https://github.com/frankli0324/CTFd)的附属项目
用于评测ACM题目

## 说明

支持C++, Java, Python2/3 四种语言的评测  
评测参数在`worker.json`中配置。  
以C++为例，配置项分别为：
```jsonc
"cpp": { //语言名，即请求/judge时的"lang"参数
    "source_name": "Main.cpp", // 将代码写入此文件。主要用于规定后缀名
    "output_name": "Main", // 编译输出文件名(如果是解释型语言则可选)
    "compile": { // 编译选项
        "command": "/usr/bin/g++ {source_path} -o {output_path} -DONLINE_JUDGE -fno-asm -O2",
        /* 编译命令，目前能渲染进的变量有:
        source_path: 源码文件的绝对路径
        output_path: 输出文件的绝对路径
        output_dir: 输出文件所在目录的绝对路径
        */
        "max_cpu_time": 3000, // 编译时长/空间限制
        "max_real_time": 5000,
        "max_memory": 134217728
    },
    "execute": { // 执行选项
        "command": "{output_path}",
        /* 执行命令，目前能渲染进的变量有:
        source_path: 源码所在的绝对路径(解释型语言需要)
        output_path: 编译出的文件的绝对路径
        output_dir: 文件所在目录绝对路径
        max_memory: 空间限制
        */
        "weight": {
            // 此处可以设置六项限制的权重，如Java可以配置为:
            /*
            "max_cpu_time": 2,
            "max_real_time": 2,
            "max_memory": -1,
            "max_stack": -1
            */
            // -1表示没有限制
            // 注: Java的空间限制由java虚拟机的启动参数进行控制
        }
    }
}
```

## 部署

```bash
docker run -p {port}:5000 frankli0324/judge_server \
    --env JUDGE_BASEDIR=/opt/judger \
    --env JUDGE_TOKEN=your_token \
    --env DATABASE_URL=mysql+pymysql://username:password@$DB_URL/judge
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
      - DATABASE_URL=mysql+pymysql://username:password@db/judge
  db: 
    image: mariadb
    ...
```

## dev

```bash
docker-compose up
```
