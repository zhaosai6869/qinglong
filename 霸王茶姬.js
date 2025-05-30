/**
* 霸王茶姬 
* export BW_TEA_TOKEN = 'token#id' 
* 多账号用 & 或换行 
* const $ = new Env('霸王茶姬') 
* cron: 22 11 * * * 
*/
const init = require('init')
const {$, notify, sudojia, checkUpdate} = init('霸王茶姬');
const moment = require('moment');
const bwTeaToken = process.env.BW_TEA_TOKEN ? process.env.BW_TEA_TOKEN.split(/[\n&]/) : [];
let message = '';
// 接口地址
const baseUrl = 'https://webapi2.qmai.cn'
// AppId
const appId = 'wxafec6f8422cb357b';
// 新版活动IDconst 
newActivityId = '1080523113114726401';
// 请求头
const headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a1b)XWEB/11097',
    'content-type': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'qm-from': 'wechat'}
!(async () => {
    await checkUpdate($.name, bwTeaToken);
    for (let i = 0; i < bwTeaToken.length; i++) {
        const index = i + 1;
        const [token, uid] = bwTeaToken[i].split('#');
        headers['qm-user-token'] = token;
        $.userId = uid;
        console.log(`\n*****第[${index}]个${$.name}账号*****`);
        const isLogin = await checkLogin();
        if (!isLogin) {
            console.error(`Token 已失效`);
            await notify.sendNotify(`「Token失效通知」`, `${$.name}账号[${index}] Token 已失效，请重新登录获取 Token\n\n`);
            continue;
        }
        message += `📣====${$.name}账号[${index}]====📣\n`;
        await $.wait(sudojia.getRandomWait(800, 1200));
        await main();
        await $.wait(sudojia.getRandomWait(2000, 2500));
    }    
    if (message) {
        await notify.sendNotify(`「${$.name}」`, `${message}`);
    }
})().catch((e) => $.logErr(e)).finally(() => $.done());
async function main() {
    await $.wait(sudojia.getRandomWait(500, 800));
    await getUserInfo();
    await $.wait(sudojia.getRandomWait(1000, 2000));
    // await queryOldSign();
    // await $.wait(sudojia.getRandomWait(2e3, 3e3));
    await queryNewSign();
    await $.wait(sudojia.getRandomWait(1000, 1500));
    await pointsInfo();}
/**
* 检测 Token 
* 
* @returns {Promise<*>} 
*/
async function checkLogin() {
    try {
         const data = await sudojia.sendRequest(`${baseUrl}/web/catering2-apiserver/crm/customer-center?appid=${appId}`, 'get', headers);
         return data.status;
        } catch (e) {
            console.error(`检测 Token 时发生异常：${e}`);
        }}
/** 
* 获取用户信息 
* 
* @returns {Promise<void>} 
*/
async function getUserInfo() {
    try {
        const data = await sudojia.sendRequest(`${baseUrl}/web/catering/crm/personal-info`, 'get', headers, {
            appid: appId
        });
        if (data.status) {
            $.phone = data.data.mobilePhone;
            $.nickName = data.data.name;
            message += `${$.nickName}(${$.phone})\n`;
            console.log(`${$.nickName}登录成功~`);
        } else {
            console.error(data.message);
        }
    } catch (e) {
        console.error(`获取用户信息时发生异常：${e}`);
    }
}
/** 
* 查询旧版签到 
* 
* @return {Promise<void>} 
*/
async function queryOldSign() {
    try {
        const data = await sudojia.sendRequest(`${baseUrl}/web/catering/integral/sign/detail`, 'post', headers, {
                appid: appId
        });
        if (data.status) {
            const {
                continuityTotal,
                signInDateList,
                activityId,
            } = data.data;
            if (signInDateList.includes(moment().format('YYYY-MM-DD'))) {
                console.log(`旧版-今天已经签到过了, 已连续签到${continuityTotal}天`);
                message += `旧版-今天已经签到过了, 已连续签到${continuityTotal}天\n`;
            } else {
                await $.wait(sudojia.getRandomWait(1000, 1500));
                await oldSign(activityId);
            }
        }
    } catch (e) {
        console.error('查询旧版接口请求失败：', e);
    }
}
/** 
* 旧版签到 
* 
* @param activityId * @returns {Promise<void>} 
*/
async function oldSign(activityId) {
    try {
        const data = await sudojia.sendRequest(`${baseUrl}/web/catering/integral/sign/signIn`, 'post', headers, {
            activityId: activityId,
            appid: appId,
            mobilePhone: $.phone,
            userName: $.nickName,
        });
        if (data.status && data.message === 'ok') {
            message += `旧版-签到成功\n`;
            console.log('旧版-签到成功');
        } else {
            console.error(`旧版-签到失败：${data.message}`);
        }
    } catch (e) {
        console.error('旧版签到接口请求失败：', e);
    }
}
/** 
* 查询新版签到 
* 
* @return {Promise<void>} 
*/
async function queryNewSign() {
    try {
        const data = await sudojia.sendRequest(`${baseUrl}/web/cmk-center/sign/userSignStatistics`, 'post', headers, {
            activityId: newActivityId,
            appid: appId,
        });
        if (data.status) {
            const {signDays, signStatus} = data.data;
            if (1 === signStatus) {
                console.log(`新版-今天已经签到过了, 已连续签到${signDays}天`);
                message += `新版-今天已经签到过了, 已连续签到${signDays}天\n`;
            } else {
                await $.wait(sudojia.getRandomWait(3e3, 5e3));
                await newSign();
            }
        }
    } catch (e) {
        console.error('查询新版接口请求失败：', e);
    }
}
/** 
* 签到 
* 
* @return {Promise<void>} 
*/
async function newSign() {
    try {
        const times = new Date().getTime();
        const data = await sudojia.sendRequest(`${baseUrl}/web/cmk-center/sign/takePartInSign`, 'post', headers, {
            activityId: newActivityId,
            storeId: 49006,
            timestamp: times,
            signature: getSign(times, $.userId),
            appid: appId,
            store_id: 49006
        });
        if (data.status) {
            message += `新版-签到成功\n`;
            console.log(`新版-签到成功`);
        } else {
            console.error('新版-签到失败：', data.message);
        }
    } catch (e) {
        console.error('新版签到接口请求失败：', e);
    }
}
/** 
* 积分查询 
* 
* @return {Promise<void>} 
*/
async function pointsInfo() {
    try {
        const data = await sudojia.sendRequest(`${baseUrl}/web/catering/crm/points-info`, 'post', headers, {
            appid: appId
        });
        if (data.status) {
            const {soonExpiredPoints, totalPoints, expiredTime} = data.data;
            message += `当前积分：${totalPoints}\n`;
            console.log(`当前积分：${totalPoints}`);
            soonExpiredPoints > 0 ? message += `${soonExpiredPoints}积分将在${expiredTime}失效\n\n`
                : message += `暂无过期积分\n\n`;
        }
    } catch (e) {
        console.error('积分查询接口请求失败：', e);
    }
}
function getSign(timestamp, userId) {
    const sellerId = 49006;
    const sellerIdStr = sellerId ? sellerId.toString() : undefined;
    const dataObject = {
        activityId: newActivityId,
        sellerId: sellerIdStr,
        timestamp: timestamp,
        userId: userId
    };
    const sortedKeys = Object.keys(dataObject).sort();
    const sortedDataObject = sortedKeys.reduce(function (acc, key) {
        acc[key] = dataObject[key];
        return acc;
    }, {});
    const queryString = Object.entries(sortedDataObject).map(function ([key, value]) {
        return key + "=" + value;
    }).join("&") + "&key=" + newActivityId.split("").reverse().join("");
    return sudojia.md5(queryString);
}