"""
基于httpx的异步请求
api调用参照mcsmanager官方文档
"""
import httpx
from httpx import AsyncClient
import json
import asyncio

# 发送命令到应用实例
async def mc_command(uuid:str, remote_uuid:str, apikey:str, headers, url:str, cmd: str):
        params={'uuid':uuid,
                'remote_uuid':remote_uuid,
                'apikey':apikey,
                'command':cmd}
        async with httpx.AsyncClient() as client:
                response = await client.get(
                        url+'/api/protected_instance/command',
                        params=params,
                        headers=headers
                        )

# 获取日志输出
async def mc_outputlog(uuid:str, remote_uuid:str, apikey:str, headers, url:str):
        params={'uuid':uuid,
                'remote_uuid':remote_uuid,
                'apikey':apikey}
        response = httpx.get(
                url+'/api/protected_instance/outputlog',
                params=params,
                headers=headers
                )
        data=response.json()
        data=data['data']
        return data

# 就是一个很简陋的获取日志更新内容的函数，写的非常不规范，但是能用就行（ssfd
def get_updates(ss:str, sub_str:str):        # 返回子串结尾在主串的位置后主串内容，ss主串，sub_str子串
        len_ss=len(ss)  # 获取字符串ss的长度len_ss
        len_sub=len(sub_str)    # 获取字符串的ssb_str长度len_sub
        b=min([100, len_sub])   # 最小长度取100
        if b==100:
                for n in range(len_ss-1,b-1,-1):
                        if ss[n-b:n]==sub_str[len_sub-b:len_sub]:
                                return ss[n:len_ss]
                        else:
                                continue
                return ''
        else: 
                for n in range(len_ss-1,b-1,-1):
                        if ss[n-len_sub:n]==sub_str:
                                return ss[n:len_ss]
                        else:
                                continue
                return ''

# 获取所有守护进程列表
async def mc_remote_services(apikey:str, headers, url:str):
        params={'apikey':apikey}# 填入root账号给出的API密钥（控制面板->个人信息->生成API密钥）
        response = httpx.get(
                url+'/api/service/remote_services',
                params=params,
                headers=headers
                )
        data=response.json()
        remote_services=data['data']
        return remote_services