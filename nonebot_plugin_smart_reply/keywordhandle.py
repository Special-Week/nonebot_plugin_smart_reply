import json
import random
import re
from pathlib import Path
from typing import Tuple, Union

from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PokeNotifyEvent,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup
from httpx import AsyncClient
from .utils import utils


class KeyWordModule:
    def __init__(self) -> None:
        self.reply_private: bool = utils.reply_private

    @staticmethod
    async def check_keyword_handle(
        matcher: Matcher, args: Message = CommandArg()
    ) -> None:
        """查看关键词"""
        key: str = args.extract_plain_text()
        if not key or key.isspace():
            await matcher.finish("check失败, 你要输入关键词哦")
        mes: str = await utils.check_word(key)
        if mes == "寄":
            await matcher.finish("抱歉没有记过这个关键词捏，请输入[查询所有关键词]来获取全部关键词")
        else:
            output: bytes = await utils.text_to_img(text=mes)  # 将文字转换为图片
            await matcher.finish(MessageSegment.image(output))

    @staticmethod
    def have_url(s: str) -> bool:
        """判断传入的字符串中是否有url存在(我他娘的就不信这样还能输出广告?)"""
        index = s.find(".")  # 找到.的下标
        if index == -1:  # 如果没有.则返回False
            return False
        flag1 = ("\u0041" <= s[index - 1] <= "\u005a") or (
            "\u0061" <= s[index - 1] <= "\u007a"
        )  # 判断.前面的字符是否为字母
        flag2 = ("\u0041" <= s[index + 1] <= "\u005a") or (
            "\u0061" <= s[index + 1] <= "\u007a"
        )  # 判断.后面的字符是否为字母
        return flag1 and flag2

    async def get_qinyunkeapi(self, ques: str) -> str:
        async with AsyncClient() as client:
            try:
                resp = (
                    await client.get(
                        f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={ques}"
                    )
                ).json()
                if self.have_url(resp["content"]):
                    if bool(utils.bing_cookies) and bool(utils.openai_api_key):
                        return f'这个问题{utils.bot_nickname}暂时不知道怎么回答你呢, 试试使用"openai"/"bing"命令头调用openai或new bing吧吧'
                    if bool(utils.openai_api_key):
                        return f'这个问题{utils.bot_nickname}暂时不知道怎么回答你呢, 试试使用"openai"命令头调用openai吧'
                    if bool(utils.bing_cookies):
                        return f'这个问题{utils.bot_nickname}暂时不知道怎么回答你呢, 试试使用"bing"命令头调用new bing吧'
                    return f"这个问题{utils.bot_nickname}暂时不知道怎么回答你呢, 换个话题吧"
                content: str = (resp["content"]).replace("{br}", "\n")
                maybe_master = ["dn", "林欣", "贾彦娟", "周超辉", "鑫总", "张鑫", "1938877131"]
                maybe_nickname = ["菲菲", "小燕"]
                su = random.choice(list(utils.superuser))
                for i in maybe_master:
                    content = content.replace(i, su)
                for i in maybe_nickname:
                    content = content.replace(i, utils.bot_nickname)
                return content
            except Exception as e:
                return f"调用api失败, 错误信息: {repr(e)}"

    @staticmethod
    async def del_akeyword_handle(
        matcher: Matcher,
        matched: Tuple[str, int] = RegexGroup(),
    ) -> None:
        """删除关键词, 通过序号删除或者通过关键词删除"""
        word1, word2 = matched
        if await utils.del_word(word1, word2) == "寄":
            await matcher.finish("找不到关键词或回复序号，请用查看命令核对")
        else:
            await matcher.finish("删除成功~")

    @staticmethod
    async def del_keyword_handle(
        matcher: Matcher, args: Message = CommandArg()
    ) -> None:
        """删除关键词, 通过关键词删除"""
        key: str = args.extract_plain_text()
        if not key or key.isspace():
            await matcher.finish("没有关键词，del失败")
        else:
            try:
                del utils.anime_thesaurus[key]
                with open(utils.keyword_path, "w", encoding="utf8") as f:
                    json.dump(utils.anime_thesaurus, f, ensure_ascii=False, indent=4)
                await matcher.send("已删除该关键词下所有回复~")
            except Exception:
                await matcher.finish("del失败, 貌似没有这个关键词呢")

    @staticmethod
    async def check_all_keyword(matcher: Matcher) -> None:
        """查看全部关键词"""
        mes: str = await utils.check_all()
        output: bytes = await utils.text_to_img(mes)
        await matcher.finish(MessageSegment.image(output))

    @staticmethod
    async def add_new_keyword(
        matcher: Matcher,
        matched: Tuple[str, ...] = RegexGroup(),
    ) -> None:
        """添加新的关键词"""
        word1, word2 = matched
        if await utils.add_word(word1, word2) == "寄":
            await matcher.finish("这个关键词已经记住辣")
        else:
            await matcher.finish("我记住了\n关键词：" + word1 + "\n回复：" + word2)

    @staticmethod
    async def poke_handle(matcher: Matcher, event: PokeNotifyEvent) -> None:
        """戳一戳回复, 私聊会报错, 暂时摸不着头脑"""
        if event.is_tome():
            probability: float = random.random()
            # 33%概率回复莲宝的藏话
            if probability < 0.33:
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

    async def regular_reply(self, matcher: Matcher, event: MessageEvent) -> None:
        """普通回复"""
        # 配置私聊不启用后，私聊信息直接结束处理
        if not self.reply_private and isinstance(event, PrivateMessageEvent):
            return
        # 获取消息文本
        msg = event.get_message().extract_plain_text()
        # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
        if (not msg) or msg.isspace() or msg in utils.nonsense:
            await matcher.finish(MessageSegment.text(await utils.rand_hello()))
        # 获取用户nickname
        if isinstance(event, GroupMessageEvent):
            nickname: Union[str, None] = event.sender.card or event.sender.nickname
        else:
            nickname = event.sender.nickname
        # 从字典里获取结果
        if nickname is None:
            nickname = "你"
        result: Union[str, None] = await utils.get_chat_result(msg, nickname)
        # 如果词库没有结果，则调用api获取智能回复
        if result is None:
            result = await self.get_qinyunkeapi(msg)
            await matcher.finish(MessageSegment.text(result), reply_message=True)
        await matcher.finish(MessageSegment.text(result), reply_message=True)


# 创建实例
key_word_module = KeyWordModule()
