'''
杜蕾斯 1.2.0
变量名 dls_Jewel
抓 vip.ixiliu.cn 域名中 access-token
多账号使用&分割
定时每天1次即可
'''

TOKEN = ""


import time
import requests
import os
import sendNotify
def lottery(token):
    url = "https://vip.ixiliu.cn/mp/activity.lottery/draw"
    url1 = "https://vip.ixiliu.cn/mp/sign/applyV2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) XWEB/8555",
        "content-type": "application/json;charset=utf-8",
        "sid": "10006",
        "xweb_xhr": "1",
        "platform": "MP-WEIXIN",
        "enterprise-hash": "10006",
        "access-token": f"{token}",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wxe11089c85860ec02/34/page-frame.html",
        "accept-language": "zh-CN,zh;q=0.9"
    }
    params = {
        "snId": "403868335815296",
        "channelSn": "0"
    }
    response = requests.get(url, headers=headers, params=params).json()
    if response["status"] == 200:
        #print(f"🎁抽奖成功 >>>>> {response['data']['prize']['prize_name']}")
        msg = f"🎁抽奖成功 >>>>> {response['data']['prize']['prize_name']}"
    else:
        #print(f"❌抽奖失败 >>>>> {response['message']}")
        msg = f"❌抽奖失败 >>>>> {response['message']}"
    response1 = requests.get(url1, headers=headers, params=params).json()
    print(f"🎁签到情况 >>>>> {response1['message']}")
    msg1 = f"🎁签到情况 >>>>> {response1['message']}"
    msg2 = msg + '\n' +msg1
    sendNotify.send('dls签到',msg1)
if __name__ == '__main__':
    env = os.getenv("dls_Jewel")
    if env:
        TOKEN = os.environ.get("dls_Jewel")
    else:
        print("未检测到环境变量 dls_Jewel 启用内置变量")
    tokenList = TOKEN.split("&")
    print(f"🔔 >>>>> 共检测到[{len(tokenList)}]个账号 开始运行杜蕾斯签到")
    for index, token in enumerate(tokenList):
        print(f"-------- 第[{index + 1}]个账号 --------")
        lottery(token)
        time.sleep(2)
