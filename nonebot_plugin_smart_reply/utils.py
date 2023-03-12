import os
import re
import time
import random
import openai
import nonebot
import sqlite3
from pathlib import Path
from loguru import logger
from EdgeGPT import Chatbot
from httpx import AsyncClient
from .txtToImg import txt_to_img

try:
    import ujson as json
except ModuleNotFoundError:
    import json

config = nonebot.get_driver().config
xiaoai_api_key: str = getattr(config, "xiaoai_apikey", "寄")
Bot_NICKNAME: str = getattr(config, "bot_nickname", "脑积水")
Bot_MASTER: str = getattr(config, "Bot_MASTER", "脑积水")
reply_private: bool = getattr(config, "ai_reply_private", False)
openai_api_key: str = getattr(config, "openai_api_key", "寄")
max_tokens: int = getattr(config, "openai_max_tokens", 1000)
cd_time: int = getattr(config, "openai_cd_time", 60)

# 数据库路径
SQLITT_PATH: str = 'data/smart_reply/req_data.db'
# 会话字典，用于存储会话   {"user_id": {"Chatbot": bot,"model":  balanced or creative or precise}}
chat_dict: dict = {}
# 初始化cookies, 注意这个cookies是一个长这样的列表[{},{},{}]
try:
    cookies: list = json.load(open("data/smart_reply/cookie.json", "r", encoding="utf8"))
except:
    logger.info("cookies.json不存在, 初始化失败")
    cookies: list = []
# 获取超级用户
SU_LIST: list = list(nonebot.get_driver().config.superusers)



def initSomething() -> None:
    """初始化一些东西"""
    if not os.path.exists("data/smart_reply"):
        os.makedirs("data/smart_reply")            # 创建文件夹
    conn = sqlite3.connect(SQLITT_PATH)         # 数据库初始化
    c = conn.cursor()
    try:
        c.execute(
            "CREATE TABLE main (user_id text, user_name text, content text, time text, isrational bool)")
        conn.commit()
    except:
        logger.info("数据库已存在")
    conn.close()
initSomething()


# 获取挑战敏感问题的次数, 超过阈值会被禁用该功能
THRESHOLD = 5       # 阈值
if os.path.exists("./data/smart_reply/user_info.json"):  # 读取用户数据
    with open("data/smart_reply/user_info.json", "r", encoding="utf-8") as f:
        user_info: dict = json.load(f)
else: 
    user_info: dict = {}
    with open("data/smart_reply/user_info.json", "w", encoding="utf-8") as f:
        json.dump(user_info, f, indent=4)
# json结构  {"user_id": {"violation": 0}}


# 初始化获取violation大于阈值的用户
ban_list: list = []
for user_id, user_data in user_info.items():
    if user_data["violation"] > THRESHOLD:
        ban_list.append(user_id)

# 获取黑名单
blackdata: dict = json.load(open(Path(__file__).parent.joinpath(
    'resource/json/blacklist.json'), "r", encoding="utf8"))


def save_user_info() -> None:
    """保存用户数据"""
    with open("data/smart_reply/user_info.json", "w", encoding="utf-8") as f:
        json.dump(user_info, f, indent=4)

async def new_chat_(user_id: str, style: str = "creative") -> str:
    """重置会话"""
    bot = Chatbot(cookies=cookies)
    chat_dict.update({user_id: {"Chatbot": bot, "model": style}})
    return f"重置会话成功, bot: {str(bot)}, model: {style}"

async def push_sql(user_id: str, user_name, content: str, isrational: bool) -> None:
    """sql插入, 记录用户请求"""
    user_name = user_name.replace("'", "")
    content = content.replace("'", "")
    conn = sqlite3.connect(SQLITT_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO main VALUES (?,?,?,?,?)", (user_id, user_name, content,
              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), isrational))
    conn.commit()
    conn.close()


# 载入词库(这个词库有点涩)
AnimeThesaurus = json.load(open(Path(__file__).parent.joinpath(
    'resource/json/data.json'), "r", encoding="utf8"))

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


async def get_chat_result(text: str, nickname: str) -> str:
    """从字典里返还消息, 抄(借鉴)的zhenxun-bot"""
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname)


async def qinyun_reply(url: str) -> str:
    """从qinyunke_api拿到消息"""
    async with AsyncClient() as client:
        response = await client.get(url)
        # 这个api好像问道主人或者他叫什么名字会返回私活,这里replace掉部分(这里好丑，不想改了)
        res = response.json()["content"].replace("林欣", Bot_MASTER).replace("{br}", "\n").replace("贾彦娟", Bot_MASTER).replace("周超辉", Bot_MASTER).replace(
            "鑫总", Bot_MASTER).replace("张鑫", Bot_MASTER).replace("菲菲", Bot_NICKNAME).replace("dn", Bot_MASTER).replace("1938877131", "2749903559").replace("小燕", Bot_NICKNAME)
        res = re.sub(u"\\{.*?\\}", "", res)
        # 检查广告, 这个api广告太多了
        if have_url(res):
            res = Bot_NICKNAME + "暂时听不懂主人说的话呢"
        return res


def have_url(s: str) -> bool:
    """判断传入的字符串中是否有url存在(我他娘的就不信这样还能输出广告?)"""
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


def text_to_png(msg: str) -> bytes:
    """文字转png"""
    return txt_to_img(msg)


def get_openai_reply(prompt: str) -> str:
    """从openai api拿到消息"""
    openai.api_key = openai_api_key
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
    # 去除开头的换行符
    while res.startswith("\n"):
        res = res[1:]
    return "\n" + res



def add_(word1: str, word2: str):
    """添加词条"""
    lis = []
    for key in AnimeThesaurus:
        if key == word1:
            # 获取字典内容
            lis = AnimeThesaurus[key]
            # 判断是否已存在问答
            for word in lis:
                if word == word2:
                    return "寄"
    # 判断是否存在关键词
    if lis == []:
        axis = {word1: [word2]}
    else:
        lis.append(word2)
        axis = {word1: lis}
    AnimeThesaurus.update(axis)
    with open(Path(__file__).parent.joinpath('resource/json/data.json'), "w", encoding="utf8") as f_new:
        json.dump(AnimeThesaurus, f_new, ensure_ascii=False, indent=4)


def check_(target: str) -> str:
    """查询关键词下词条"""
    for item in AnimeThesaurus:
        if target == item:
            mes = "下面是关键词" + target + "的全部响应\n\n"
            # 获取关键词
            lis = AnimeThesaurus[item]
            n = 0
            for word in lis:
                n = n + 1
                mes = mes + str(n) + '、'+word + '\n'
            return mes
    return "寄"


def check_al() -> str:
    """查询全部关键词"""
    mes = "下面是全部关键词\n\n"
    for c in AnimeThesaurus:
        mes = mes + c + '\n'
    return mes

def del_(word1: str, word2: int):
    """删除关键词下具体回答"""
    axis = {}
    for key in AnimeThesaurus:
        if key == word1:
            lis = AnimeThesaurus[key]
            word2 = int(word2) - 1
            try:
                lis.pop(word2)
                axis = {word1: lis}
            except:
                return "寄"
    if axis == {}:
        return "寄"
    AnimeThesaurus.update(axis)
    with open(Path(__file__).parent.joinpath('resource/json/data.json'), "w", encoding="utf8") as f_new:
        json.dump(AnimeThesaurus, f_new, ensure_ascii=False, indent=4)