import json
import random
import re
from pathlib import Path
from typing import Tuple

from nonebot.adapters.onebot.v11 import (GroupMessageEvent, Message,
                                         MessageEvent, MessageSegment,
                                         PokeNotifyEvent, PrivateMessageEvent)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup

from .utils import utils


class KeyWordModule:
    def __init__(self) -> None:
        self.reply_private: bool = utils.reply_private


    async def check_keyword_handle(self, 
        matcher: Matcher, 
        args: Message = CommandArg()
    ):
        """查看关键词"""
        key = args.extract_plain_text()
        if key == "" or key.isspace():
            await matcher.finish("check失败, 你要输入关键词哦")
        mes = await utils.check_word(key)
        if mes == "寄":
            await matcher.finish("抱歉没有记过这个关键词捏，请输入[查询所有关键词]来获取全部关键词")
        else:
            output = await utils.text_to_img(text=mes)  # 将文字转换为图片
            await matcher.finish(MessageSegment.image(output))


    async def del_akeyword_handle(
        self,
        matcher: Matcher,
        matched: Tuple[str, int] = RegexGroup(),
    ):
        """删除关键词, 通过序号删除或者通过关键词删除"""
        word1, word2 = matched
        if await utils.del_word(word1, word2) == "寄":
            await matcher.finish("找不到关键词或回复序号，请用查看命令核对")
        else:
            await matcher.finish("删除成功~")


    async def del_keyword_handle(
        self,
        matcher: Matcher, 
        args: Message = CommandArg()
    ):
        """删除关键词, 通过关键词删除"""
        key = args.extract_plain_text()
        if key == "" or key.isspace():
            await matcher.finish("没有关键词，del失败")
        else:
            try:
                del utils.anime_thesaurus[key]
                with open(utils.keyword_path, "w", encoding="utf8") as f:
                    json.dump(utils.anime_thesaurus, f, ensure_ascii=False, indent=4)
                await matcher.send("已删除该关键词下所有回复~")
            except Exception:
                await matcher.finish("del失败, 貌似没有这个关键词呢")


    async def check_all_keyword(self, matcher: Matcher):
        """查看全部关键词"""
        mes = await utils.check_all()
        output = await utils.text_to_img(mes)
        await matcher.finish(MessageSegment.image(output))


    async def add_new_keyword(
        self,
        matcher: Matcher,
        matched: Tuple[str, ...] = RegexGroup(),
    ):
        """添加新的关键词"""
        word1, word2 = matched
        if await utils.add_word(word1, word2) == "寄":
            await matcher.finish("这个关键词已经记住辣")
        else:
            await matcher.finish("我记住了\n关键词：" + word1 + "\n回复：" + word2)


    async def poke_handle(
        self, 
        matcher: Matcher, 
        event: PokeNotifyEvent
    ):
        """戳一戳回复, 私聊会报错, 暂时摸不着头脑"""
        if event.is_tome():
            probability = random.random()
            # 33%概率回复莲宝的藏话
            if probability > 11:
                # 发送语音需要配置ffmpeg, 这里try一下, 不行就随机回复poke__reply的内容
                try:
                    await matcher.send(
                        MessageSegment.record(
                            Path(utils.audio_path) / random.choice(utils.audio_list)
                        )
                    )
                except Exception:
                    await matcher.send(await utils.rand_poke())
            elif probability > 0.66:
                # 33% 概率戳回去
                await matcher.send(Message(f"[CQ:poke,qq={event.user_id}]"))
            # probability在0.33和0.66之间的概率回复poke__reply的内容
            else:
                await matcher.send(await utils.rand_poke())


    async def regular_reply(
        self,
        matcher: Matcher, 
        event: MessageEvent
    ):
        """普通回复"""
        # 配置私聊不启用后，私聊信息直接结束处理
        if not self.reply_private and isinstance(event, PrivateMessageEvent):
            return
        # 获取消息文本
        msg = str(event.get_message())
        # 去掉带中括号的内容(去除cq码)
        msg = re.sub(r"\[.*?\]", "", msg)
        # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
        if (
            (not msg)
            or msg.isspace()
            or msg in utils.nonsense
        ):
            await matcher.finish(Message(await utils.rand_hello()))
        # 获取用户nickname
        if isinstance(event, GroupMessageEvent):
            nickname = event.sender.card or event.sender.nickname
        else:
            nickname = event.sender.nickname
        # 从字典里获取结果
        result = await utils.get_chat_result(msg, nickname)
        # 如果词库没有结果，则调用api获取智能回复
        if result is None:
            await matcher.finish(
                Message(f"抱歉，{utils.bot_nickname}暂时不知道怎么回答你呢, 试试使用openai或者bing吧~")
            )
        await matcher.finish(Message(result))


# 创建实例
key_word_module = KeyWordModule()