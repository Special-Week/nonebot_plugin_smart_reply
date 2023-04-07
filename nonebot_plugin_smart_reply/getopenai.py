import asyncio

from nonebot.adapters.onebot.v11 import (Message, MessageEvent, MessageSegment,
                                         PrivateMessageEvent)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from revChatGPT.V3 import Chatbot

from .utils import utils


class Openai:
    def __init__(self) -> None:
        """初始化, 获取openai的apikey是否存在, 获取是否私聊启用"""
        self.apikey_allow = bool(utils.openai_api_key)
        self.reply_private: bool = utils.reply_private
        self.max_sessions_number: int = utils.max_sessions_number


    async def reserve_openai(
        self,
        matcher: Matcher, 
        event: MessageEvent
    ) -> None:
        """重置openai会话"""
        await utils.openai_new_chat(event=event, matcher=matcher)
        await matcher.send("openai会话已重置", at_sender=True)


    async def openai_handle(
        self,
        matcher: Matcher, 
        event: MessageEvent, 
        args: Message = CommandArg()
    ):
        """openai聊天的handle函数"""
        if not self.reply_private and isinstance(event, PrivateMessageEvent):
            return          # 配置私聊不启用后，私聊信息直接结束处理
        uid = event.get_user_id()  # 获取用户id
        msg = args.extract_plain_text()  # 获取消息

        if not self.apikey_allow:
            await matcher.finish("openai_api_key未设置, 无法访问")

        if msg.isspace() or msg == "":
            return      # 如果消息为空, 则不处理
        if msg in utils.nonsense:
            # 如果消息为空或者是一些无意义的问候, 则返回一些问候语
            await matcher.finish(await utils.rand_hello())

        if uid not in utils.openai_chat_dict:  # 如果用户id不在会话字典中, 则新建一个会话
            await utils.openai_new_chat(event=event, matcher=matcher)
            await matcher.send("openai新会话已创建", at_sender=True)
        if utils.openai_chat_dict[uid]["isRunning"]:  # 如果当前会话正在运行, 则返回正在运行
            await matcher.finish("当前会话正在运行中, 请稍后再发起请求", at_sender=True)
        if utils.openai_chat_dict[uid]["sessions_number"] >= self.max_sessions_number:
            # 如果会话数超过最大会话数, 则返回会话数已达上限
            await matcher.send("会话数已达上限, 正在帮您请重置会话", at_sender=True)
            await self.reserve_openai(matcher=matcher, event=event)
            return
        utils.openai_chat_dict[uid]["isRunning"] = True  # 将当前会话状态设置为运行中
        bot: Chatbot = utils.openai_chat_dict[uid]["chatbot"]  # 获取当前会话的Chatbot对象
        try:
            loop = asyncio.get_event_loop()     # 调用ask会阻塞asyncio
            data = await loop.run_in_executor(None, bot.ask, msg)
            utils.openai_chat_dict[uid]["sessions_number"]+=1  # 会话数+1
        except Exception as e:  # 如果出现异常, 则返回异常信息, 并且将当前会话状态设置为未运行
            utils.openai_chat_dict[uid]["isRunning"] = False
            await matcher.finish(
                f'askError: {str(e)}多次askError请尝试发送"重置openai"', at_sender=True
            )
        utils.openai_chat_dict[uid]["isRunning"] = False  # 将当前会话状态设置为未运行
        sessions_number = utils.openai_chat_dict[uid]["sessions_number"]  # 获取当前会话的会话数
        data += f"\n\n当前: {sessions_number} 共{self.max_sessions_number}  \n字数异常请发送\"重置openai\"" 
        try:
            await matcher.send(data, at_sender=True)
        except Exception as e:
            try:
                await matcher.send(
                    f"文本消息被风控了,错误信息:{str(e)}, 这里咱尝试把文字写在图片上发送了{MessageSegment.image(await utils.text_to_img(data))}",
                    at_sender=True,
                )
            except Exception as eeee:
                await matcher.send(f"消息全被风控了, 这是捕获的异常: \n{str(eeee)}", at_sender=True)


# 创建实例
openai = Openai()
