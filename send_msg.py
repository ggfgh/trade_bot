# -*- coding: utf-8 -*-

'''
企业微信推送机器人
'''
import requests
import json
import time
from rich.console import Console
import demo

# 企业id、key
console = Console()
CORP_ID = ''
CORP_SECRET = ''
AGENT_ID = 1000002
head = {"User-Agent":"baidu;"}
proxies = {
    'http':'http://127.0.0.1:33210',
    'https':'http://127.0.0.1:33210'
}
def getToken():
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={CORP_SECRET}"
    r = requests.get(url,headers=head)
    if r.status_code == 200:
        data = json.loads(r.text)
        if data["errcode"] == 0:
            return data["access_token"]
        else:
            print("Error")
    else:
        print("Error")  # 连接服务器失败

def sendMsg(content,touser):
    data = {
           "touser" : touser,
           "msgtype" : "text",
           "agentid" : AGENT_ID,
           "text" : {
               "content" : content
           },
           "safe":0
        }
    access_token = getToken()
    r = requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(access_token),headers=head,data=json.dumps(data))
    # print(r.text)
    if '"errmsg":"ok"' in r.text:
        console.log("[green][+] 消息发送成功！")

if __name__ == "__main__":
    while True:
                now_time = time.strftime("%Y-%m-%d %H:%M:%S")
                price = demo.get_close_kline_price('ETH/USDT', '30m')
        
                data = f"{now_time}, ETH/USDT当前价格: {price}"
                sendMsg(data,"@all")
                time.sleep(60*30)
    
