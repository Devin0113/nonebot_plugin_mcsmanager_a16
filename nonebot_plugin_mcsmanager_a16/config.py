"""
config.py保存一些配置
其实是读取json的
我也不知道为什么写成这样了，不伦不类的
插件初始化需要手动在config.json内填写superuser、apikey、url，其余内容可以在群内配置
"""
import json
import os

json_path_r = os.path.abspath(os.path.join(__file__, "..", "config"))
json_path_r = os.path.join(json_path_r, "config.json")
# 读取json文件内容,返回字典格式
with open(json_path_r,'r',encoding='utf8')as fp:
    json_data = json.load(fp)
fp.close()

class Config:
    # 超级用户
    superusers = json_data["superusers"]
    # 群组及其配置
    groups = json_data["groups"]
    # 群组列表
    group_id = []
    for i in groups:
        group_id.append(i["group_id"])
        # 用于消息转发
        i["ss"] = "" 
        i["sub"] = "" 
    # 插件执行优先级
    priority = json_data['priority']
    # api相关
    apikey = json_data["api_config"]["apikey"]  # 在config.json内填入root账号给出的API密钥（控制面板->个人信息->生成API密钥）
    url = json_data["api_config"]["url"]    # 在config.json内填入url
    headers = json_data["api_config"]["headers"]
    headers_UserAgent = json_data["api_config"]["headers"]["User-Agent"]
    headers_ContentType = json_data["api_config"]["headers"]["Content-Type"]
