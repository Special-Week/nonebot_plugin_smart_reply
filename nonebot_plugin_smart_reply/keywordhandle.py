import re
import json
import random
from typing import Tuple
from pathlib import Path
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup

from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    PokeNotifyEvent,
    GroupMessageEvent,
    PrivateMessageEvent,
)

from .utils import(
    del_,
    add_,
    hello,
    check_,
    check_al,
    text_to_png,
    get_chat_result,
    
    poke__reply,
    Bot_NICKNAME,
    aac_file_path,
    reply_private,
    aac_file_list,
    AnimeThesaurus,
)


async def check_keyword_handle(matcher:Matcher,args: Message = CommandArg()):
    """查看关键词"""
    key = args.extract_plain_text()
    if key=="" or key.isspace():
        await matcher.finish("check失败, 你要输入关键词哦")
    mes = check_(key)
    if mes == "寄":
        await matcher.finish("抱歉没有记过这个关键词捏，请输入[查询所有关键词]来获取全部关键词")
    else:
        output = text_to_png(mes) # 将文字转换为图片
        await matcher.finish(MessageSegment.image(output))





async def del_akeyword_handle(
    matcher:Matcher,
    matched: Tuple[str, int] = RegexGroup(),
):
    """删除关键词, 通过序号删除或者通过关键词删除"""
    word1, word2 = matched
    if del_(word1, word2) == "寄":
        await matcher.finish("找不到关键词或回复序号，请用查看命令核对")
    else:
        await matcher.finish("删除成功~")



async def del_keyword_handle(matcher:Matcher,args: Message = CommandArg()):
    """删除关键词, 通过关键词删除"""
    key = args.extract_plain_text()
    if key=="" or key.isspace():
        await matcher.finish("没有关键词，del失败")
    else:
        try:
            del AnimeThesaurus[key]
            with open(Path(__file__).parent.joinpath('resource/json/data.json'), "w", encoding="utf8") as f_new:
                json.dump(AnimeThesaurus, f_new, ensure_ascii=False, indent=4)
            await matcher.send("已删除该关键词下所有回复~")
        except:
            await matcher.finish("del失败, 貌似没有这个关键词呢")


async def check_all_keyword(matcher:Matcher):
    """查看全部关键词"""
    mes = check_al()
    output = text_to_png(mes)
    await matcher.finish(MessageSegment.image(output))



async def add_new_keyword(
    matcher:Matcher,
    matched: Tuple[str, ...] = RegexGroup(),
):
    """添加新的关键词"""
    word1, word2 = matched
    if add_(word1, word2) == "寄":
        await matcher.finish("这个关键词已经记住辣")
    else:
        await matcher.finish("我记住了\n关键词："+word1+"\n回复："+word2)



async def poke(matcher:Matcher, event: PokeNotifyEvent):
    """戳一戳回复"""
    if event.is_tome:
        probability = random.random() # 生成0-1之间的随机数
        # 33%概率回复莲宝的藏话
        if probability < 0.33:
            # 发送语音需要配置ffmpeg, 这里try一下, 不行就随机回复poke__reply的内容
            try:
                await matcher.send(MessageSegment.record(Path(aac_file_path)/random.choice(aac_file_list)))
            except:
                await matcher.send(message=f"{random.choice(poke__reply)}")
        elif probability > 0.66:
            # 33% 概率戳回去
            await matcher.send(Message(f"[CQ:poke,qq={event.user_id}]"))
        # probability在0.33和0.66之间的概率回复poke__reply的内容
        else:
            await matcher.send(message=f"{random.choice(poke__reply)}")



async def regular_reply(matcher:Matcher, event: MessageEvent):
    """普通回复"""
    # 配置私聊不启用后，私聊信息直接结束处理
    if not reply_private and isinstance(event, PrivateMessageEvent):
        return
    # 获取消息文本
    msg = str(event.get_message())
    # 去掉带中括号的内容(去除cq码)
    msg = re.sub(r"\[.*?\]", "", msg)
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    if (not msg) or msg.isspace() or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "你好",
        "在",
    ]:
        await matcher.finish(Message(hello()))
    # 获取用户nickname
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 从字典里获取结果
    result = await get_chat_result(msg,  nickname)
    # 如果词库没有结果，则调用api获取智能回复
    if result == None:
        await matcher.finish(Message(f"抱歉，{Bot_NICKNAME}暂时不知道怎么回答你呢, 试试使用openai或者bing吧~"))
    await matcher.finish(Message(result))


