"""
适用于基于Mcsmanager的mc服务器
仅适配Nonebot2_a16版本
至于为什么没有适配beta版...因为没时间而且懒（）

首次使用需在Config/config.json中手动填入超级用户qq号、服务器url、专属apikey（root账号给出的API密钥（控制面板->个人信息->生成API密钥））
其余配置只需在q群中使用机器人指令自动配置

没学过编程更没学过py，小孩子瞎写着玩的，求轻喷
也求大佬可以帮助我改进一下代码（（

急需改进的地方：权限管理、消息转发中的信息过滤和格式化
"""
from queue import PriorityQueue
import nonebot
from nonebot import on_command,require
from nonebot.adapters.cqhttp import Message
# from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
import importlib
import os

scheduler = require("nonebot_plugin_apscheduler").scheduler

from .api import *

from .config import *


cfg = Config
# 重载配置文件 使用方法 global xxx = update_config(xxx)
def update_config(cfg):
    importlib.reload(config)    # 重载config.py
    from .config import Config  # 重载config.py内的Config类
    cfg = Config
    return cfg

json_path_r = os.path.abspath(os.path.join(__file__, "..", "config"))
json_path_r = os.path.join(json_path_r, "config.json")
json_path_w = json_path_r
dict={} # 用来存储数据
# 获取json文件数据
def get_json_data(json_path_r):
    with open(json_path_r,'rb') as fr:
        dict = json.load(fr)    # 加载json文件中的内容给dict
    fr.close()
    return dict # 返回dict字典内容
# 写入json文件
def write_json_data(dict):
    with open(json_path_w,'w') as fw:
        json.dump(dict,fw,indent=4) # 将dict格式化写入名称为fw的文件中
    fw.close()


# 帮助
mc_help = on_command('mc_help', aliases=set(['mchelp']), priority=cfg.priority)
@mc_help.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        await mc_help.finish(
            f"1. 指令 <指令>\n"
            f"2. 指令 say <内容>\n"
            f"3. mc消息转发\n"
            f"4. 更新服务器列表\n"
            f"5. 查询服务器列表\n"
            f"6. 绑定mc服务器 <服务器名称>\n"
            f"7. 解绑mc服务器\n"
            f"8. 服务器在线人数\n"
            f"--------------------\n"
            f"9. 添加超级用户 <qq账号>\n"
            f"10. 删除超级用户 <qq账号>\n"
            f"11. 超级用户列表\n"
            f"--------------------\n"
            f"12.mchelp"
            )


# 向实例发送指令
# say指令无需权限且自动添加署名，其余指令均需超级用户权限
mc_cmd = on_command('mc_cmd', aliases=set(['指令']), priority=cfg.priority)
@mc_cmd.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        if not args: await mc_cmd.send('至少输一条指令吧')
        else:
            if group_id not in cfg.group_id: pass
            else:
                for i in cfg.groups:
                    if i["group_id"] == group_id:
                        if args.startswith("say"):
                            infos = str(await bot.get_stranger_info(user_id=user_id))
                            nickname = json.loads(infos.replace("'", '"'))['nickname']
                            args = args.replace("say","say <"+nickname+">")
                            try:
                                await mc_command(i["group_config"]["instanceUuid"],i["group_config"]["uuid"],cfg.apikey,cfg.headers,cfg.url,args)
                            except httpx.TimeoutException:
                                await mc_cmd.finish('超时错误，请检查网络设置')
                        else:
                            if user_id not in cfg.superusers: await mc_cmd.finish('除“say”以外指令仅超级用户可使用')
                            else:
                                try:
                                    await mc_command(i["group_config"]["instanceUuid"],i["group_config"]["uuid"],cfg.apikey,cfg.headers,cfg.url,args)
                                except httpx.TimeoutException:
                                    await mc_cmd.finish('超时错误，请检查网络设置')
                        await mc_cmd.finish('已执行指令：'+args)


# 接收实例消息开关
# 仅超级用户
mc_msg_switch = on_command('mc_msg_switch', aliases=set(['mc消息转发']), priority=cfg.priority)
@mc_msg_switch.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    infos = event.get_session_id()
    if infos.startswith("group"):
        dict = get_json_data(json_path_r)
        _, group_id, user_id = event.get_session_id().split("_")
        if group_id not in cfg.group_id: await mc_msg_switch.finish('此群暂未绑定服务器')
        else:
            for i in dict["groups"]:
                if i["group_id"] == group_id:
                    if i["group_config"]["msgforward"]: i["group_config"]["msgforward"] = 0
                    else: i["group_config"]["msgforward"] = 1
                    write_json_data(dict)
                    cfg = update_config(cfg)
                    for i in cfg.groups:
                        if i["group_id"] == group_id:
                            if i["group_config"]["msgforward"]: state = '开启'
                            else: state = '关闭'
                            await mc_msg_switch.finish('本群mc服务器消息转发功能已'+state)

# 每5秒进行一次检测，转发日志更新的消息
# 还需要完善
# 将超出500字符的消息阻断，以免刷屏
@scheduler.scheduled_job("cron", second="*/5")
async def _():
        global cfg
        bots = nonebot.get_bots()
        for i in cfg.groups:
            if i["group_config"]["msgforward"]:
                i["sub"] = i["ss"]
                try:
                    i["ss"] = await mc_outputlog(i["group_config"]["instanceUuid"],i["group_config"]["uuid"],cfg.apikey,cfg.headers,cfg.url)
                    out = get_updates(i["ss"],i["sub"])
                    for bot in bots:
                            if len(out) <= 5: pass
                            elif len(out) <= 500: await bots[bot].send_msg(group_id=i["group_id"],message=out)
                            else: await bots[bot].send_msg(group_id=i["group_id"],message='消息过长')
                except: pass


# 过滤获得的服务器列表信息(写的什么勾八（）)
def server_info_filtering(raw:dict):
    for i in raw:
        for key in list(i.keys()):
            if key == "instances":
                for j in i[key]:
                    for key in list(j.keys()):
                        if key == "config":
                            for key in list(j["config"]):
                                if not key == "nickname": j["config"].pop(key)
                        elif not key == "instanceUuid": j.pop(key)
            elif not key == "uuid": i.pop(key)
    return raw


# 更新服务器列表至config.json
mc_update_S_list = on_command('mc_update_S_list', aliases=set(['更新服务器列表']), priority=cfg.priority)
@mc_update_S_list.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    infos = event.get_session_id()
    if infos.startswith("group"):
        dict = get_json_data(json_path_r)
        _, group_id, user_id = event.get_session_id().split("_")
        if user_id not in cfg.superusers: await mc_update_S_list.finish('权限不足：需要超级用户')
        else:
            dict = get_json_data(json_path_r)
            try:
                raw = await mc_remote_services(cfg.apikey,cfg.headers,cfg.url)
                dict["remote_services"] = server_info_filtering(raw)
                write_json_data(dict)
                await mc_update_S_list.finish('更新完成')
            except httpx.TimeoutException:
                await mc_update_S_list.finish('超时错误，请检查连接并重试')


# 从config.json查询服务器列表
mc_query_S_list = on_command('mc_query_S_list', aliases=set(['查询服务器列表']), priority=cfg.priority)
@mc_query_S_list.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        if user_id not in cfg.superusers: await mc_query_S_list.finish('权限不足：需要超级用户')
        else:
            dict = get_json_data(json_path_r)
            count = 0
            datalist = []
            datastr = ''
            for i in dict["remote_services"]:
                for j in i["instances"]:
                    count = count+1
                    datalist.append(str(count)+'. ')
                    datalist.append(str(j["config"]["nickname"])+'\n')
            datastr = ''.join(datalist)
            await mc_query_S_list.finish('已保存的服务器列表：\n'+datastr+'如需更新请发送“更新服务器列表”')


# 从config.json读取并绑定服务器
mc_bind = on_command('mc_bind', aliases=set(['绑定mc服务器']), priority=cfg.priority)
@mc_bind.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        if user_id not in cfg.superusers: await mc_bind.finish('权限不足：需要超级用户')
        else:
            if not args: await mc_bind.finish('请在指令后输入需要绑定的服务器名称\n若需要获取服务器列表请输入“查询服务器列表”')
            else:
                uuid = ''
                dict = get_json_data(json_path_r)
                for i in dict["remote_services"]:
                    for j in i["instances"]:
                        if j["config"]["nickname"] == args:
                            uuid = j["instanceUuid"]
                            remote_uuid = i["uuid"]
                if uuid == '': await mc_bind.finish('绑定失败！未查找到服务器：'+args+'\n请检查或更新服务器列表')
                if group_id not in cfg.group_id:
                    group = {
                                "group_id": group_id,
                                "group_config": {
                                    "msgforward": 0,
                                    "uuid": remote_uuid,
                                    "instanceUuid": uuid
                                }
                            }
                    dict["groups"].append(group)
                else:
                    for i in dict["groups"]:
                        if i["group_id"] == group_id:
                            i["group_config"]["instanceUuid"] = uuid
                            i["group_config"]["uuid"] = remote_uuid
                write_json_data(dict)
                cfg = update_config(cfg)
                await mc_bind.finish('绑定成功！本群已绑定服务器：'+args)


# 从config.json读取并解绑服务器
mc_unbind = on_command('mc_unbind', aliases=set(['解绑mc服务器']), priority=cfg.priority)
@mc_unbind.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        if user_id not in cfg.superusers: await mc_unbind.finish('权限不足：需要超级用户')
        else:
            dict = get_json_data(json_path_r)
            for i in list(dict["groups"]):
                if i["group_id"] == group_id:
                    dict["groups"].remove(i)
                    write_json_data(dict)
                    cfg = update_config(cfg)
                    await mc_unbind.finish('解绑成功')


# 获取服务器在线人数
# 突然发现好像没啥用，不如直接指令list然后格式化一下输出，下次再改（）
mc_online_P = on_command('mc_online_P', aliases=set(['服务器在线人数']), priority=cfg.priority)
@mc_online_P.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        try:
            dict = await mc_remote_services(cfg.apikey,cfg.headers,cfg.url)
            if group_id not in cfg.group_id: await mc_online_P.finish('此群暂未绑定服务器')
            else:
                for i in cfg.groups:
                    if i["group_id"] == group_id:
                        uuid = i["group_config"]["uuid"]
                        instanceUuid = i["group_config"]["instanceUuid"]
                for i in dict:
                    if i["uuid"] == uuid:
                        for j in i["instances"]:
                            if j["instanceUuid"] == instanceUuid:
                                currentPlayers = j["info"]["currentPlayers"]
                                maxPlayers = j["info"]["maxPlayers"]
            await mc_online_P.finish('服务器当前在线人数'+str(currentPlayers)+'/'+str(maxPlayers))
        except httpx.TimeoutException:
            await mc_online_P.finish('超时错误，请检查连接并重试')


# 从config.json读取并添加超级用户
mc_add_SU = on_command('mc_add_SU', aliases=set(['添加超级用户']), priority=cfg.priority)
@mc_add_SU.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        if user_id not in cfg.superusers: await mc_add_SU.finish('权限不足：需要超级用户')
        else:
            if not args: await mc_add_SU.finish('请在指令后输入qq账号')
            elif not args.isdigit(): await mc_add_SU.finish('请输入qq账号（纯数字组合）而非其他内容')
            elif args in cfg.superusers: await mc_add_SU.finish('请不要重复添加已有账号')
            else:
                datalist = []
                datastr = ''
                dict = get_json_data(json_path_r)
                dict["superusers"].append(args)
                write_json_data(dict)
                cfg = update_config(cfg)
                for i in cfg.superusers:
                    datalist.append(str(i)+'\n')
                datastr = ''.join(datalist)
                await mc_add_SU.finish('添加超级用户成功，目前超级用户列表：\n'+datastr+'若有误请使用指令“删除超级用户”')


# 从config.json读取并删除超级用户
mc_rm_SU = on_command('mc_rm_SU', aliases=set(['删除超级用户']), priority=cfg.priority)
@mc_rm_SU.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    args = str(event.get_message()).strip()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        if user_id not in cfg.superusers: await mc_rm_SU.finish('权限不足：需要超级用户')
        else:
            if not args: await mc_rm_SU.finish('请在指令后输入qq账号')
            elif not args.isdigit(): await mc_rm_SU.finish('请输入qq账号（纯数字组合）而非其他内容')
            elif args == user_id: await mc_rm_SU.finish('请不要尝试删除自己的账号')
            else:
                datalist = []
                datastr = ''
                dict = get_json_data(json_path_r)
                dict["superusers"].remove(args)
                write_json_data(dict)
                cfg = update_config(cfg)
                for i in cfg.superusers:
                    datalist.append(str(i)+'\n')
                datastr = ''.join(datalist)
                await mc_rm_SU.finish('删除超级用户成功，目前超级用户列表：\n'+datastr+'若误删除请使用指令“添加超级用户'+args+'”')


# 从Config.py读取超级用户列表
mc_read_SU = on_command('mc_read_SU', aliases=set(['超级用户列表']), priority=cfg.priority)
@mc_read_SU.handle()
async def handle(bot: Bot, event: Event, state: T_State):
    global cfg
    infos = event.get_session_id()
    if infos.startswith("group"):
        _, group_id, user_id = event.get_session_id().split("_")
        datalist = []
        datastr = ''
        for i in cfg.superusers:
            datalist.append(str(i)+'\n')
        datastr = ''.join(datalist)
        await mc_read_SU.finish('目前超级用户列表：\n'+datastr+'若需要操作请使用指令“添加\删除超级用户”')