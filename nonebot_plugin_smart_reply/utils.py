from pathlib import Path
import os
import random
import nonebot
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from httpx import AsyncClient
import re
import openai


try:
    apiKey: str = nonebot.get_driver().config.xiaoai_apikey
except:
    apiKey: str = "寄"

try:
    Bot_NICKNAME: str = nonebot.get_driver(
    ).config.bot_nickname     # bot的nickname,可以换成你自己的
    Bot_MASTER: str = nonebot.get_driver().config.bot_master      # bot的主人名称,也可以换成你自己的
except:
    Bot_NICKNAME: str = "脑积水"
    Bot_MASTER: str = "脑积水"
# NICKNAME: str = "Hinata"
# MASTER: str = "星野日向_Official"

try:
    api_key = nonebot.get_driver().config.openai_api_key
except:
    api_key = '寄'

try:
    max_tokens = nonebot.get_driver().config.openai_max_tokens
except:
    max_tokens = 1000


# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(os.path.join(os.path.dirname(
    __file__), "resource/json")) / "data.json", "r", encoding="utf8"))


# 获取resource/audio下面的全部文件
aac_file_path = os.path.join(os.path.dirname(__file__), "resource/audio")
aac_file_list = os.listdir(aac_file_path)

# hello之类的回复
hello__reply = [
    "你好！",
    "哦豁？！",
    "你好！Ov<",
    f"库库库，呼唤{Bot_NICKNAME}做什么呢",
    "我在呢！",
    "呼呼，叫俺干嘛",
]


# 戳一戳消息
poke__reply = [
    "lsp你再戳？",
    "连个可爱美少女都要戳的肥宅真恶心啊。",
    "你再戳！",
    "？再戳试试？",
    "别戳了别戳了再戳就坏了555",
    "我爪巴爪巴，球球别再戳了",
    "你戳你🐎呢？！",
    f"请不要戳{Bot_NICKNAME} >_<",
    "放手啦，不给戳QAQ",
    f"喂(#`O′) 戳{Bot_NICKNAME}干嘛！",
    "戳坏了，赔钱！",
    "戳坏了",
    "嗯……不可以……啦……不要乱戳",
    "那...那里...那里不能戳...绝对...",
    "(。´・ω・)ん?",
    "有事恁叫我，别天天一个劲戳戳戳！",
    "欸很烦欸！你戳🔨呢",
    "再戳一下试试？",
    "正在关闭对您的所有服务...关闭成功",
    "啊呜，太舒服刚刚竟然睡着了。什么事？",
    "正在定位您的真实地址...定位成功。轰炸机已起飞",
]

# 从字典里返还消息, 抄(借鉴)的zhenxun-bot


async def get_chat_result(text: str, nickname: str) -> str:
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname)

# 从qinyunke_api拿到消息


async def qinyun_reply(url):
    async with AsyncClient() as client:
        response = await client.get(url)
        # 这个api好像问道主人或者他叫什么名字会返回私活,这里replace掉部分
        res = response.json()["content"].replace("林欣", Bot_MASTER).replace("{br}", "\n").replace("贾彦娟", Bot_MASTER).replace("周超辉", Bot_MASTER).replace(
            "鑫总", Bot_MASTER).replace("张鑫", Bot_MASTER).replace("菲菲", Bot_NICKNAME).replace("dn", Bot_MASTER).replace("1938877131", "2749903559").replace("小燕", Bot_NICKNAME)
        res = re.sub(u"\\{.*?\\}", "", res)
        # 检查广告, 这个api广告太多了
        if have_url(res):
            res = Bot_NICKNAME + "暂时听不懂主人说的话呢"
        return res

# 从小爱同学api拿到消息, 这个api私货比较少


async def xiaoice_reply(url):
    async with AsyncClient() as client:
        res = (await client.get(url)).json()
        if res["code"] == 200:
            return (res["text"]).replace("小爱", Bot_NICKNAME)
        else:
            return "寄"


# 判断传入的字符串中是否有url存在(我他娘的就不信这样还能输出广告?)
def have_url(s: str) -> bool:
    index = s.find('.')     # 找到.的下标
    if index == -1:         # 如果没有.则返回False
        return False

    flag1 = (u'\u0041' <= s[index-1] <= u'\u005a') or (u'\u0061' <=
                                                       s[index-1] <= u'\u007a')        # 判断.前面的字符是否为字母
    flag2 = (u'\u0041' <= s[index+1] <= u'\u005a') or (u'\u0061' <=
                                                       s[index+1] <= u'\u007a')        # 判断.后面的字符是否为字母
    if flag1 and flag2:     # 如果.前后都是字母则返回True
        return True
    else:               # 如果.前后不是字母则返回False
        return False


def get_openai_reply(prompt:str)->str:
    openai.api_key = api_key
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    res = response.choices[0].text
    # 移除所有开头的\n
    while res.startswith("\n"):
        res = res[1:]
    return res
