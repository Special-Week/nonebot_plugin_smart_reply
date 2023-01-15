import os
import re
import base64
import random
import openai
import nonebot
from pathlib import Path
from httpx import AsyncClient
from loguru import logger
from re import findall
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
poke_reply = [
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


async def xiaoice_reply(url: str) -> str:
    """从小爱同学api拿到消息, 这个api私货比较少"""
    async with AsyncClient() as client:
        res = (await client.get(url)).json()
        if res["code"] == 200:
            return (res["text"]).replace("小爱", Bot_NICKNAME)
        else:
            return "寄"


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


"""获取 setu 部分"""
async def get_setu() -> list:
    async with AsyncClient() as client:
        req_url = "https://api.lolicon.app/setu/v2"
        params = {
            "r18": 0,
            "size": "regular",
            "proxy": "i.pixiv.re",
        }
        res = await client.get(req_url, params=params, timeout=120)
        logger.info(res.json())
        setu_title = res.json()["data"][0]["title"]
        setu_url = res.json()["data"][0]["urls"]["regular"]
        content = await down_pic(setu_url)
        setu_pid = res.json()["data"][0]["pid"]
        setu_author = res.json()["data"][0]["author"]
        base64 = convert_b64(content)
        if type(base64) == str:
            pic = "[CQ:image,file=base64://" + base64 + "]"
            data = (
                "标题:"
                + setu_title
                + "\npid:"
                + str(setu_pid)
                + "\n画师:"
                + setu_author
            )
        return [pic, data, setu_url]
async def down_pic(url):
    async with AsyncClient() as client:
        headers = {
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        re = await client.get(url=url, headers=headers, timeout=120)
        if re.status_code == 200:
            logger.success("成功获取图片")
            return re.content
        else:
            logger.error(f"获取图片失败: {re.status_code}")
            return re.status_code
def convert_b64(content) -> str:
    ba = str(base64.b64encode(content))
    pic = findall(r"\'([^\"]*)\'", ba)[0].replace("'", "")
    return pic