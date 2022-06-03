# nonebot_plugin_mcsmanager_a16
A nonebot2 a16 plugin for mc server based on mcsmanager.

一个适用于基于mcsmanager的mc服务器的Nonebot2插件，适配nonebot2 a16

是的，如果你也使用的是下面的版本那么肯定没有问题（心虚）：

- NoneBot2 a16
- MCSManager 9.4.4

## 目录

- [背景](#背景)
- [安装](#安装)
- [使用说明](#使用说明)
- [相关仓库](#相关仓库)


## 背景

也许是背景？这是我的第一个github项目，写的很烂（）

因为没学过编程更没学过py，这个README也是对着某个标准现学的（我甚至还不知道提交以后这个README会有多难看...）

代码真的很烂，能跑就行.jpg

因为没发现有人写这个插件，查了一下mcsmanager的文档发现只要简单的调用一下api就可以实现很多功能，于是就写了这样一个插件

不过真的会有人用吗，要不我还是继续用a16摆烂，不继续适配nonebot2beta版了（）

> 写完README又手痒去搜索了一下，原来其实还是有大佬写了，只是当初我眼瞎没看到（）
> 挖，原来还能给自己点star（）


## 安装

其实我只知道直接下载项目，所以......


首先需要安装python的httpx和json库（当然我相信大家都已经安装过了）

```sh
pip install httpx
pip install json
```


其次是这个插件还需要nonebot的[APScheduler定时任务插件](https://github.com/nonebot/plugin-apscheduler)


最后只要把nonebot_plugin_mcsmanager_a16塞到bot的plugins文件夹里就可以啦（我究竟在干什么）


## 使用说明
初次使用请在Config/config.json里手动填入superuser（你的qq号）、apikey（就是root账号生成的API密钥（控制面板->个人信息->生成API密钥））、url（你的mcsmanager服务器地址）

其他东西应该都可以在群里输指令完成配置

在群聊中输入“mchelp”来获取指令列表

（话说README该怎么添加图片来着，是引用库的图片吗，想加一条测试的截图）

- 获取指令列表：

![mchelp](https://github.com/Devin0113/nonebot_plugin_mcsmanager_a16/blob/main/img/01help.jpg)

- 向服务器发送讯息：

![mcsay](https://github.com/Devin0113/nonebot_plugin_mcsmanager_a16/blob/main/img/02say.jpg)

- 向服务器发送其他指令：

![mccmd](https://github.com/Devin0113/nonebot_plugin_mcsmanager_a16/blob/main/img/03cmd.jpg)

- 接收服务器信息开关：

![mcmsg](https://github.com/Devin0113/nonebot_plugin_mcsmanager_a16/blob/main/img/04msg.jpg)

- 服务器列表：

![mcs](https://github.com/Devin0113/nonebot_plugin_mcsmanager_a16/blob/main/img/05s.jpg)

- 群聊绑定服务器（一个群聊仅允许绑定一个服务器）：

![mcbind](https://github.com/Devin0113/nonebot_plugin_mcsmanager_a16/blob/main/img/06bind.jpg)

- 超级用户：

![mcsu](https://github.com/Devin0113/nonebot_plugin_mcsmanager_a16/blob/main/img/07su.jpg)

## 相关仓库
- [NoneBot2](https://github.com/nonebot/nonebot2)
- [APScheduler定时任务插件](https://github.com/nonebot/plugin-apscheduler)
- [MCSManager](https://github.com/MCSManager/MCSManager)
