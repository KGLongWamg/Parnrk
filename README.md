# Parnrk
一个为了电子竞技良好竞技环境而诞生的程序，从英雄联盟开始

基于PYQT5进行研发

## 下载方法

方法1.克隆项目并安装Parnrk

```
# 使用 Github 
git clone https://github.com/KGLongWamg/Parnrk.git

请根据网络情况如无法克隆建议开启VPN
```

方法2.下载zip解压缩

```
https://github.com/KGLongWamg/Parnrk/archive/refs/heads/main.zip
```

## 运行步骤
1. 安装并配置python 3.10环境
```
	https://www.python.org/
```
2. 下载依赖项 
```
pip install pip install -r requriements.txt
```
3. 运行demo.py

用的是pyqt5 和qtfluent 中示例界面代码改过来的。
诚邀有能力有意向的朋友一起学习，一起开发

## 代码大概
自己写了一个Parnrk包，是用willump和客户端通信，有订阅逻辑。可以先熟悉下，使用了一个单例模式，让willump 以及和服务端通信的client 都运行在一个叫做"Thread"的loop里。
现在是在用pyqt5写界面，用的是PyQt-Fluent-Widget中的例子界面直接更改过来的，
"pip install PyQt-Fluent-Widgets[full]"  可pip这个

我只修改了view 里面的basic_input_interface ，连接了我的Parnrk包，其他的都是原界面例子自带的。
目前希望把查战绩功能先运行起来，目标是自动查询BP界面战绩，同时匿名化显示数据库剧组。然后进入游戏查询十个人战绩并显示英雄技能

