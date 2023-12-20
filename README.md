# Parnrk
一个为了电子竞技良好竞技环境而诞生的程序，从英雄联盟开始

基于PYQT5进行研发

## 下载方法

方法1.克隆项目并安装Parnrk

```
# 使用 Github 
git clone https://github.com/KGLongWamg/Parnrk.git
或者
git clone git@github.com:KGLongWamg/Parnrk.git

请根据网络情况如无法克隆建议开启魔法
```

方法2.下载zip解压缩

```
https://github.com/KGLongWamg/Parnrk/archive/refs/heads/main.zip
```

## 运行步骤
1. 安装并配置python 3.10以及更新版本的环境
```
	https://www.python.org/
```
2. 下载依赖项 
```
pip install pip install -r requriements.txt
```



3. 运行demo.py
```
先打开联盟客户端
然后在终端中执行
python demo.py
就会打开程序界面，开始检测对局开始。
终端目前会打印各种信息方便调试
每次对局开始，bp阶段会显示我方战绩，等游戏开始了会显示敌方战绩
如果对方近50把对局里没有进行过排位那么会显示'未使用Parnrk授权或隐私设置'

登陆界面的账号和密码都是z12345678,可以自己注册，第一次登陆会跳3个界面，关掉就好了，后续几次都不需要再登陆

```

## 代码逻辑和流程,对参与人员的建议
写了一个Parnrk包，里面是放置的交互lcuapi以及订阅的功能，可以直接调用。
是用willump  https://github.com/elliejs/Willump 和客户端通信。可以先熟悉下，使用了一个单例模式，让willump 以及和英雄联盟服务端通信的client 都运行在一个叫做"Thread"的loop里。


主线程的worker执行一个异步函数async_task，在这个异步函数里持续循环，等待订阅信息的到来更新程序中的显示界面

现在是在用pyqt5写界面，用的是PyQt-Fluent-Widget中的例子界面直接更改过来的，
安装请使用"pip install PyQt-Fluent-Widgets[full]" 

想要参与的小伙伴需要学习以下知识点和框架的使用
```
asynico
pyqt 5
PyQt-Fluent-Widget
lcu 	(这部分代码有人会负责，可以不管)
willump	(这部分代码有人会负责，可以不管)
```
大家都是边学边做的，大家都是菜鸡，不懂就问

## 目前bug


```
登陆界面登陆后会跳出3个界面，需要会pyqt5的大佬看下是哪里的问题
```



```
QPixmap::scaled: Pixmap is a null pixmap
终端有个qt的类似于警告的内容，目前没什么影响
```




## 将要实现的功能（待实现，不完全）
```
当前对局遇到剧组的匿名化显示
```

```
查看游戏所在所有英雄的详细技能介绍
```

```
上一把游戏结束后，清空10人的显示信息
```

```
等级系统，用户会拥有自己的等级。除人机外，当对局收到来自非队友的点赞，可以加100经验，5000经验升为1级。账号1级视为白名单，当排位BP时，可以被对方看到。脚本，剧组不能获得白名单
```

