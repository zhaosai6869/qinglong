#脚本来源 妖火论坛 By将军
#完成每天两个视频任务获取会员时长
#抓取https://m.jr.开头的包请求头的cookie
#变量xmqb 多账号新建
#内容cUserId=xxx;jrairstar_serviceToken=xxx;

import os
import time
from typing import Optional, Dict, Any, Union

import requests
import urllib3
from loguru import logger

# logger.add('app.log', rotation='10 MB', retention=5)

class RnlRequest:
    def __init__(self, cookies: Union[str, dict]):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        """
        初始化
        :param cookies: 浏览器复制的完整cookie字符串
        """
        self.session = requests.Session()
        self._base_headers = {
            'Host': 'm.jr.airstarfinance.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }
        self.update_cookies(cookies)

    def request(
            self,
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Union[Dict[str, Any], str, bytes]] = None,
            json: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        发送请求
        :param method: HTTP方法 (GET/POST等)
        :param url: 请求URL
        :param params: URL参数
        :param data: 表单数据
        :param json: JSON数据
        :return: 解析后的JSON数据或None
        """
        headers = {**self._base_headers, **kwargs.pop('headers', {})}

        try:
            resp = self.session.request(
                verify=False,
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                **kwargs
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"[Request Error] {e}")
        except ValueError as e:
            print(f"[JSON Parse Error] {e}")
        return None

    def update_cookies(self, cookies: Union[str, dict]) -> None:
        """更新cookie字典"""
        if cookies:
            if isinstance(cookies, str):
                str_cookie = cookies
                dict_cookies = self._parse_cookies(cookies)
            else:
                dict_cookies = cookies
                str_cookie = self.dict_cookie_to_string(cookies)
            self.session.cookies.update(dict_cookies)
            self._base_headers['Cookie'] = str_cookie

    @staticmethod
    def _parse_cookies(cookies_str: str) -> Dict[str, str]:
        """解析cookie字符串为字典"""
        return dict(
            item.strip().split('=', 1)
            for item in cookies_str.split(';')
            if '=' in item
        )

    @staticmethod
    def dict_cookie_to_string(cookie_dict):
        """
        将字典形式的 cookie 转换为字符串
        :param cookie_dict: 包含 cookie 信息的字典
        :return: 转换后的 cookie 字符串
        """
        cookie_list = []
        for key, value in cookie_dict.items():
            cookie_list.append(f"{key}={value}")
        return "; ".join(cookie_list)
    # 快捷方法
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('GET', url, params=params, **kwargs)

    def post(self, url: str, data: Optional[Union[Dict[str, Any], str, bytes]] = None,
             json: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        return self.request('POST', url, data=data, json=json, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


class RNL:
    def __init__(self, c):
        self.t_id = None
        self.options = {
            "task_list": True,  # 获取任务列表
            "complete_task": True,  # 完成任务
            "receive_award": True,  # 领取奖励
            "task_item": True,  # 任务详情
            "UserJoin": True,  # 任务记录
        }
        self.activity_code = '2211-videoWelfare'
        self.rr = RnlRequest(c)

    # 任务列表
    def get_task_list(self):
        data = {
            'activityCode': self.activity_code,
        }
        try:
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTaskList',
                data=data,
            )
            if response['code'] != 0:
                logger.error(response)
                return None
            target_tasks = []
            for task in response['value']['taskInfoList']:
                if '浏览组浏览任务' in task['taskName']:
                    target_tasks.append(task)
            # logger.info(json.dumps(target_tasks, indent=4, ensure_ascii=False))
            # logger.info(target_tasks)
            return target_tasks
        except Exception as e:
            logger.error(f'获取任务列表失败：{e}')
            return None

    # 获取当前完成的任务
    def get_task(self, task_code):
        if not self.options.get('task_item', False):
            return
        try:
            data = {
                'activityCode': self.activity_code,
                'taskCode': task_code,
                'jrairstar_ph': '98lj8puDf9Tu/WwcyMpVyQ==',
            }
            response = self.rr.post(
                'https://m.jr.airstarfinance.net/mp/api/generalActivity/getTask',
                data=data,
            )
            if response['code'] != 0:
                logger.error(f'获取任务信息失败：{response}')
                return None

            return response['value']['taskInfo']['userTaskId']
        except Exception as e:
            logger.error(f'获取任务信息失败：{e}')
            return None

    # 完成任务
    def complete_task(self, task_id, t_id, brows_click_urlId):
        if not self.options.get('complete_task', False):
            return
        try:
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/completeTask?activityCode={self.activity_code}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&taskId={task_id}&browsTaskId={t_id}&browsClickUrlId={brows_click_urlId}&clickEntryType=undefined&festivalStatus=0',
            )
            if response['code'] != 0:
                logger.error(f'完成任务失败：{response}')
                return None
            logger.success(f'完成任务成功：{response["error"]}')
            return response['value']
        except Exception as e:
            logger.error(f'完成任务失败：{e}')
            return None

    # 领取奖励
    def receive_award(self, user_task_id):
        if not self.options.get('receive_award', False):
            return
        try:
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/luckDraw?imei=&device=manet&appLimit=%7B%22com.qiyi.video%22:false,%22com.youku.phone%22:true,%22com.tencent.qqlive%22:true,%22com.hunantv.imgo.activity%22:true,%22com.cmcc.cmvideo%22:false,%22com.sankuai.meituan%22:true,%22com.anjuke.android.app%22:false,%22com.tal.abctimelibrary%22:false,%22com.lianjia.beike%22:false,%22com.kmxs.reader%22:true,%22com.jd.jrapp%22:false,%22com.smile.gifmaker%22:true,%22com.kuaishou.nebula%22:false%7D&activityCode={self.activity_code}&userTaskId={user_task_id}&app=com.mipay.wallet&isNfcPhone=true&channel=mipay_indexicon_TVcard&deviceType=2&system=1&visitEnvironment=2&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D'
            )
            if response['code'] != 0:
                logger.error(f'领取奖励务失败：{response}')
                return None
            logger.success(f'领取奖励成功：{response["error"]}')
        except Exception as e:
            logger.error(f'领取奖励务失败：{e}')

    # 任务完成记录
    def queryUserJoinListAndQueryUserGoldRichSum(self):
        try:
            total_res = self.rr.get('https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserGoldRichSum?app=com.mipay.wallet&deviceType=2&system=1&visitEnvironment=2&userExtra={"platformType":1,"com.miui.player":"4.27.0.4","com.miui.video":"v2024090290(MiVideo-UN)","com.mipay.wallet":"6.83.0.5175.2256"}&activityCode=2211-videoWelfare')
            if total_res['code'] != 0:
                logger.error(f'获取兑换视频天数失败：{total_res}')
                return False
            total = f"{int(total_res['value']) / 100:.2f}天"
            response = self.rr.get(
                f'https://m.jr.airstarfinance.net/mp/api/generalActivity/queryUserJoinList?&userExtra=%7B%22platformType%22:1,%22com.miui.player%22:%224.27.0.4%22,%22com.miui.video%22:%22v2024090290(MiVideo-UN)%22,%22com.mipay.wallet%22:%226.83.0.5175.2256%22%7D&activityCode={self.activity_code}&pageNum=1&pageSize=20',
            )
            if response['code'] != 0:
                logger.error(f'查询任务完成记录失败：{response}')
                return False
            history_list = response['value']['data']
            logger.success(f'当前用户兑换视频天数：{total}')
            logger.info('------------ 任务完成记录 ------------')
            for a in history_list:
                t = a['createTime']
                desc = a['desc']
                val = a['value']
                logger.success(f'{desc}，+{int(val) / 100:.2f}天,{t}')
            return True
        except Exception as e:
            logger.error(f'获取兑换视频天数和任务完成记录失败，可能cookie过期：{e}')
            return False

    def main(self):
        if not self.queryUserJoinListAndQueryUserGoldRichSum():
            return False
        for i in range(2):
            # 获取任务列表
            tasks = self.get_task_list()
            task = tasks[0]
            try:
                t_id = task['generalActivityUrlInfo']['id']
                self.t_id = t_id
            except:
                t_id = self.t_id
            task_id = task['taskId']
            task_code = task['taskCode']
            brows_click_url_id = task['generalActivityUrlInfo']['browsClickUrlId']

            time.sleep(13)

            # 完成任务
            user_task_id = self.complete_task(
                t_id=t_id,
                task_id=task_id,
                brows_click_urlId=brows_click_url_id,
            )

            time.sleep(2)

            # 获取任务数据
            if not user_task_id:
                user_task_id = self.get_task(task_code=task_code)
                time.sleep(2)

            # 领取奖励
            self.receive_award(
                user_task_id=user_task_id
            )

            time.sleep(2)
        # 记录
        self.queryUserJoinListAndQueryUserGoldRichSum()
        return True

if __name__ == "__main__":
    cookie = ''
    if not cookie:
        cookie = os.getenv('xmqb', '')
    cookie_list = cookie.split('&')
    if len(cookie_list) > 0:
        print(f"\n>>>>>>>>>>共获取到{len(cookie_list)}个账号<<<<<<<<<<")
        for index, c in enumerate(cookie_list):
            print(f"\n---------开始执行第{index+1}个账号>>>>>")
            run_result = RNL(c).main()
            if not run_result:
                continue

