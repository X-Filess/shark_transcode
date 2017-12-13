### Dependency

* ubuntu 16.04
* python3
* pymysql
* sqlalchemy
* ffmpeg
* apscheduler
* flask

### Installation

```
sudo pip3 install mysql-connector
sudo pip3 install pymsql
sudo pip3 install sqlalchemy
sudo pip3 install pyinstaller
sudo pip3 install apscheduler
sudo pip3 install flask
sudo apt-get install ffmpeg

```

### Usage

```
git clone https://github.com/djstava/shark_transcode
python3 main.py
```

### 转码配置文件

位于工程目录config下的settings.json，示例如下

```
{
  "service":
  {
    "13+1301": "udp://@225.0.0.100:9001",
    "13+1302": "udp://@225.0.0.101:9001",
    "15+1501": "udp://@225.0.0.102:9001",
    "23+2301": "udp://@225.0.0.103:9001",
    "26+2601": "udp://@225.0.0.104:9001",
    "26+2602": "udp://@225.0.0.105:9001",
    "30+3001": "udp://@225.0.0.106:9001",
    "38+3801": "udp://@225.0.0.107:9001",
    "38+3802": "udp://@225.0.0.108:9001",
    "38+3803": "udp://@225.0.0.109:9001",
    "39+3901": "udp://@225.0.0.110:9001",
    "39+3902": "udp://@225.0.0.111:9001",
    "39+3903": "udp://@225.0.0.112:9001",
    "40+4001": "udp://@225.0.0.113:9001",
    "40+4002": "udp://@225.0.0.114:9001",
    "40+4003": "udp://@225.0.0.115:9001",
    "29+2901": "udp://@225.0.0.116:9001",
    "29+2902": "udp://@225.0.0.117:9001",
    "27+2701": "udp://@225.0.0.118:9001",
    "27+2702": "udp://@225.0.0.119:9001"
  },

  "config":
  {
    "mysql":
    {
      "server": "10.0.0.166",
      "port": "3306",
      "username": "ljepg",
      "passwd": "videosys201",
      "dbname": "lj_video_sys",
      "charset": "utf8"
    },

    "srs":
    {
      "servermode": "local",
      "tsdir": "/home/longjing/record",
      "slicedir": "/home/longjing/lj_video_sys",
      "suffix": "index.m3u8",
      "spacethreshold" : "0.9",
      "vbitrate" : "4400k",
      "abitrate" : "128k",
      "interfacename": "enp2s0",
      "webport" : "8888"
    }
  }
}

```

##### 视频转码配置
视频组播地址同时也是TDT/TOT服务器地址，ts_id、service_id、start_time标识一个节目

```
    ts_id+service_id: udp组播地址
```

##### 视频服务器设置

```

"servermode": 切片模式
"tsdir": 录制文件存放路径
"slicedir": 切片后存放路径
"suffix": 切片索引文件后缀
"spacethreshold" : 磁盘监控峰值
"vbitrate" : 视频比特率
"abitrate" : 音频比特率
"interfacename": 网卡接口
"webport" : web接口端口

```

##### MySQL设置

```
"server": 数据库IP地址,
"port": 数据库端口,
"username": 数据库用户名,
"passwd": 数据库密码,
"dbname": 数据库名称,
"charset": 数据库编码格式
```

### 数据库结构
events表结构

| 字段          | 数据类型         | 备注           |
| ----------- | ------------ | ------------ |
| ts_id       | INT(11)      | PK、NN        |
| service_id  | INT(11)      | PK、NN        |
| event_id    | INT(11)      | NN           |
| event_name  | VARCHAR(100) | NN、节目名称      |
| start_time  | INT(11)      | PK、NN、节目开始时间 |
| end_time    | INT(11)      | NN、节目结束时间    |
| url         | VARCHAR(100) | 点播url        |
| record_flag | TINYINT(2)   | 是否已录标志位      |
| slice_flag  | TINYINT(2)   | 是否已切标志位      |

### Web接口查询系统状态
<http://ip:port>, 端口即为上文配置中的webport

### 多码率切片设置（TODO）

工程目录m3u8下variants.py

```

variants={}

variants["low480"]={"name":"low480","aspect": "480:360", "framerate" :15.0,"vbitrate": "365k",
		"bufsize" : "800k","maxrate":"450k","abitrate": "64k","bandwidth":432000,"infile":None}

variants["low640"]={"name":"low640","aspect": "640:360", "framerate" :29.97,"vbitrate": "730k",
		"bufsize" : "1600k", "maxrate":"800k","abitrate": "64k","bandwidth": 784000,"infile":None}

variants["med768"]={"name":"med768","aspect": "768:432", "framerate" :29.97,"vbitrate": "1100k",
		"bufsize" : "2200k","maxrate":"1200k","abitrate": "96k","bandwidth":1127000,"infile":None}

variants["med960"]={"name":"med960","aspect": "960x540", "framerate" :29.97,"vbitrate": "2000k",
		"bufsize" : "4400k","maxrate":"2200k","abitrate": "96k","bandwidth":1951000,"infile":None}

variants["hd720"]={"name":"hd720","aspect": "1280:720", "framerate" :29.97,"vbitrate": "4500k",
		"bufsize" : "9000k","maxrate":"5500k","abitrate": "128k","bandwidth":4224000,"infile":None}

variants["hd1080"]={"name":"hd1080","aspect": "1920:1080", "framerate" :29.97,"vbitrate": "7800k",
		"bufsize" : "15600k","maxrate":"8200k","abitrate": "128k","bandwidth":7483000,"infile":None}
```

### 程序打包
```
buildit.sh
```