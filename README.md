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
目前可以查看所有隐藏战绩，方便调试代码，后期不隐藏战绩和没有参与Parnrk社区的成员将不查询该召唤师的战绩。

登陆界面的账号和密码都是z12345678,第一次登陆会跳3个界面，关掉就好了，后续几次都不需要再登陆

```

## 代码逻辑和流程,对参与人员的建议
自己写了一个Parnrk包，是用willump  https://github.com/elliejs/Willump  和客户端通信，有订阅逻辑。可以先熟悉下，使用了一个单例模式，让willump 以及和英雄联盟服务端通信的client 都运行在一个叫做"Thread"的loop里。

主线程的worker执行一个异步函数async_task，在这个异步函数里持续循环，等待订阅信息的到来更新程序中的显示界面

现在是在用pyqt5写界面，用的是PyQt-Fluent-Widget中的例子界面直接更改过来的，
"pip install PyQt-Fluent-Widgets[full]"  可pip这个

我只修改了view 里面的basic_input_interface ，连接了我的Parnrk包，其他的都是原界面例子自带的。
目前希望把查战绩功能先运行起来，目标是自动查询BP界面战绩，同时匿名化显示数据库剧组。然后进入游戏查询十个人战绩并显示英雄技能

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
代码里有个error4 910 ,会抛出异常，但是没有什么大的影响
暂时没查出为什么会出现这个问题
```

```
登陆界面登陆时会跳出3个界面，还没改
```


```
QPixmap::scaled: Pixmap is a null pixmap
终端有个qt的类似于警告的内容，目前没什么影响
```


```
有时候获取战绩会出错，得到None的数据
```

## 将要实现的功能（待实现，不完全）
```
添加剧组黑名单以及和剧组有关的各种功能
```

```
查看对局英雄的技能cd，省得自己去查
```

```
上一把游戏结束后，进入下一场对局前清空10人的显示信息
```