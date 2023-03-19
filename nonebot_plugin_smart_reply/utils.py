import os
import re
import json
import random
import nonebot
from pathlib import Path
from loguru import logger
from .txtToImg import txt_to_img
from EdgeGPT import Chatbot as bingChatbot
from revChatGPT.V3 import Chatbot as openaiChatbot

from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher



# 获取env配置: 
config = nonebot.get_driver().config
Bot_NICKNAME: str = getattr(config, "bot_nickname", "脑积水")
reply_private: bool = getattr(config, "ai_reply_private", False)
openai_api_key: list = getattr(config, "openai_api_key", [])
openai_max_tokens: int = getattr(config, "openai_max_tokens", 1000)
openai_cd_time: int = getattr(config, "openai_cd_time", 10*60)
newbing_cd_time: int = getattr(config, "newbing_cd_time", 10*60)
# ===================================================================================================
logger.info(f"openai_api_key读取, 初始化成功, 共{len(openai_api_key)}个api_key")   # 打印日志






# newbing相关工具:
if not os.path.exists("data/smart_reply"):
    os.makedirs("data/smart_reply")             # 不存在创建文件夹

bing_chat_dict: dict = {}           # 会话字典，用于存储会话   {"user_id": {"Chatbot": bot, "last_time": time}}
bing_cookies = []               # 初始化bing_cookies, 注意这个cookies是一个长这样的列表[ [{},{},{}], [{},{},{}] ...]

try:
    # 获取data/smart_reply/所有以cookie文件
    cookie_files = [file for file in os.listdir(
        "data/smart_reply") if file.startswith("cookie")]
    for file in cookie_files:
        if file.endswith(".json"):  # 如果是json文件
            with open(f"data/smart_reply/{file}", "r", encoding="utf-8") as f:
                bing_cookies.append(json.load(f))    # 加载json文件到列表里面
    logger.success(f"bing_cookies读取, 初始化成功, 共{len(bing_cookies)}个cookies")   # 打印日志
except Exception as e:
    logger.info(f"bing_cookies读取, 初始化失败, 错误信息{str(e)}")  # 初始化失败


async def newbing_new_chat(event: MessageEvent, matcher: Matcher, user_id: str):
    """重置会话"""
    currentTime = event.time    # 获取当前时间
    if user_id in bing_chat_dict:    # 如果用户id在会话字典里面
        last_time = bing_chat_dict[user_id]["last_time"] # 获取上一次的时间
        if (currentTime - last_time < newbing_cd_time) and (event.get_user_id() not in config.superusers):    # 如果当前时间减去上一次时间小于CD时间, 直接返回
            await matcher.finish(f"非报错情况下每个会话需要{newbing_cd_time}秒才能新建哦, 当前还需要{newbing_cd_time - (currentTime - last_time)}秒")
    # 如果用户id不在会话字典里面, 或者当前时间减去上一次时间大于CD时间, 重置会话
    bot = bingChatbot(cookies=random.choice(bing_cookies))       # 随机选择一个cookies创建一个Chatbot
    bing_chat_dict.update({user_id: {"Chatbot": bot, "model": "balanced",
                     "last_time": currentTime, "isRunning": False}})    # 更新会话字典
    

def bing_string_handle(input_string: str) -> str:
    """处理一下bing返回的字符串"""
    input_string = re.sub(r'\[\^(\d+)\^\]', '', input_string)
    regex = r"\[\d+\]:"
    matches = re.findall(regex, input_string)
    if not matches:
        return input_string
    positions = [(match.start(), match.end()) for match in re.finditer(regex, input_string)]
    end = input_string.find("\n", positions[len(positions)-1][1])
    target = input_string[end:] +"\n\n"+ input_string[:end]
    while target[0] == "\n":
        target = target[1:]
    return target
# ===================================================================================================






# openai相关工具:
openai_chat_dict: dict = {}           # openai会话字典，用于存储会话   {"user_id": {"Chatbot": bot, "last_time": time}}

async def openai_new_chat(event: MessageEvent, matcher: Matcher, user_id: str):
    """重置会话"""
    currentTime = event.time    # 获取当前时间
    if user_id in openai_chat_dict:    # 如果用户id在会话字典里面
        last_time = openai_chat_dict[user_id]["last_time"] # 获取上一次的时间
        if (currentTime - last_time < openai_cd_time) and (event.get_user_id() not in config.superusers):    # 如果当前时间减去上一次时间小于CD时间, 直接返回
            await matcher.finish(f"非报错情况下每个会话需要{openai_cd_time}秒才能新建哦, 当前还需要{openai_cd_time - (currentTime - last_time)}秒")
    # 如果用户id不在会话字典里面, 或者当前时间减去上一次时间大于CD时间, 重置会话
    bot = openaiChatbot(api_key=random.choice(openai_api_key), max_tokens=openai_max_tokens)       # 随机选择一个cookies创建一个Chatbot
    openai_chat_dict.update({user_id: {"Chatbot": bot, "last_time": currentTime, "isRunning": False}})    # 更新会话字典












# key_word相关工具: 
AnimeThesaurus = json.load(open(Path(__file__).parent.joinpath(
    'resource/json/data.json'), "r", encoding="utf8"))          # 载入词库(这个词库有点涩)

# 获取resource/audio下面的全部文件
aac_file_path = os.path.join(os.path.dirname(__file__), "resource/audio")
aac_file_list = os.listdir(aac_file_path)



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

def hello() -> str:
    """随机问候语"""
    result = random.choice(
        (
            "你好！",
            "哦豁？！",
            "你好！Ov<",
            f"库库库，呼唤{Bot_NICKNAME}做什么呢",
            "我在呢！",
            "呼呼，叫俺干嘛",
        )
    )
    return result

async def get_chat_result(text: str, nickname: str) -> str:
    """从字典里返还消息, 抄(借鉴)的zhenxun-bot"""
    if len(text) < 7:
        keys = AnimeThesaurus.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(AnimeThesaurus[key]).replace("你", nickname)
            

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
# ===================================================================================================





def text_to_png(msg: str) -> bytes:
    """文字转png"""
    return txt_to_img(msg)
