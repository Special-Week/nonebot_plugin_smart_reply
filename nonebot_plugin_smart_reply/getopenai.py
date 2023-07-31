import asyncio
from datetime import datetime, timedelta
from typing import Dict

from httpx import AsyncClient
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
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
        # 查询openai的使用情况
        self.usage_url = "/v1/dashboard/billing/usage"
        self.subscription_url = "/v1/dashboard/billing/subscription"
        self.expire_time_url = "dashboard/billing/credit_grants"
        self.host = "https://api.openai.com"

    @staticmethod
    async def reserve_openai(matcher: Matcher, event: MessageEvent) -> None:
        """重置openai会话"""
        await utils.openai_new_chat(event=event, matcher=matcher)
        await matcher.send("openai会话已重置", at_sender=True)

    async def openai_handle(
        self, matcher: Matcher, event: MessageEvent, args: Message = CommandArg()
    ) -> None:
        """openai聊天的handle函数"""
        if not self.reply_private and isinstance(event, PrivateMessageEvent):
            return  # 配置私聊不启用后，私聊信息直接结束处理
        uid: str = event.get_user_id()  # 获取用户id
        msg: str = args.extract_plain_text()  # 获取消息

        if not self.apikey_allow:
            await matcher.finish("openai_api_key未设置, 无法访问")

        if msg.isspace() or not msg:
            return  # 如果消息为空, 则不处理
        if msg in utils.nonsense:
            # 如果消息为空或者是一些无意义的问候, 则返回一些问候语
            await matcher.finish(
                MessageSegment.text(await utils.rand_hello()), reply_message=True
            )
        if uid not in utils.openai_chat_dict:  # 如果用户id不在会话字典中, 则新建一个会话
            await utils.openai_new_chat(event=event, matcher=matcher)
            await matcher.send(MessageSegment.text("openai新会话已创建"), reply_message=True)
        if utils.openai_chat_dict[uid]["isRunning"]:  # 如果当前会话正在运行, 则返回正在运行
            await matcher.finish(
                MessageSegment.text("当前会话正在运行中, 请稍后再发起请求"), reply_message=True
            )
        if utils.openai_chat_dict[uid]["sessions_number"] >= self.max_sessions_number:
            # 如果会话数超过最大会话数, 则返回会话数已达上限
            await matcher.send(
                MessageSegment.text("会话数已达上限, 正在帮您请重置会话"), reply_message=True
            )
            await self.reserve_openai(matcher=matcher, event=event)
            return
        utils.openai_chat_dict[uid]["isRunning"] = True  # 将当前会话状态设置为运行中
        bot: Chatbot = utils.openai_chat_dict[uid]["chatbot"]  # 获取当前会话的Chatbot对象
        try:
            loop = asyncio.get_event_loop()  # 调用ask会阻塞asyncio
            data: str = await loop.run_in_executor(None, bot.ask, msg)
            utils.openai_chat_dict[uid]["sessions_number"] += 1  # 会话数+1
        except Exception as e:  # 如果出现异常, 则返回异常信息, 并且将当前会话状态设置为未运行
            utils.openai_chat_dict[uid]["isRunning"] = False
            await matcher.finish(
                MessageSegment.text(f'askError: {repr(e)}多次askError请尝试发送"重置openai"'),
                reply_message=True,
            )
        utils.openai_chat_dict[uid]["isRunning"] = False  # 将当前会话状态设置为未运行
        sessions_number: int = utils.openai_chat_dict[uid][
            "sessions_number"
        ]  # 获取当前会话的会话数
        data += f'\n\n当前: {sessions_number} 共{self.max_sessions_number}  \n字数异常请发送"重置openai"'
        try:
            await matcher.send(MessageSegment.text(data), reply_message=True)
        except Exception as e:
            try:
                await matcher.send(
                    MessageSegment.text(f"文本消息被风控了,错误信息:{repr(e)}, 这里咱尝试把文字写在图片上发送了")
                    + MessageSegment.image(await utils.text_to_img(data)),
                    reply_message=True,
                )
            except Exception as eeee:
                await matcher.send(
                    MessageSegment.text(f"消息全被风控了, 这是捕获的异常: \n{repr(eeee)}"),
                    reply_message=True,
                )

    async def get_usage(self, params: dict, apikey: str) -> str:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {apikey}",
        }
        try:
            async with AsyncClient(proxies=utils.proxy) as client:
                usage_result = (
                    await client.get(
                        self.host + self.usage_url, headers=headers, params=params
                    )
                ).json()
                subscription_result = (
                    await client.get(self.host + self.subscription_url, headers=headers)
                ).json()
            # 获取总额
            total_usd = subscription_result["hard_limit_usd"]
            # 获取过期时间
            expire_seconds = subscription_result["access_until"]
            date = datetime.fromtimestamp(int(expire_seconds))
            # 获取使用量
            total_usage = usage_result["total_usage"] / 100
            return f"apikey:{f'{apikey[:7]}*******{apikey[-4:]}'}\n实际已使用金额:{round(total_usage, 3)}\n总共金额:{round(total_usd, 3)}\n过期日期:{date.isoformat()}\n\n"
        except Exception as e:
            return f"apikey:{f'{apikey[:7]}*******{apikey[-4:]}'}\n获取使用量失败, 错误信息:{repr(e)}\n\n"

    async def apikey_status(
        self,
        matcher: Matcher,
    ) -> None:
        """获取apikey状态"""
        if not self.apikey_allow:
            await matcher.finish("apikey未设置, 无法访问")
        else:
            params: Dict[str, str] = {
                "start_date": (datetime.now() - timedelta(days=90)).strftime(
                    "%Y-%m-%d"
                ),
                "end_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            }
            tasks = [
                self.get_usage(params=params, apikey=apikey)
                for apikey in utils.openai_api_key
            ]
            result = await asyncio.gather(*tasks)
            await matcher.finish("".join(result))


# 创建实例
openai = Openai()
