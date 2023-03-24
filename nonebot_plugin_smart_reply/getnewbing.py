from EdgeGPT import Chatbot
from nonebot.adapters.onebot.v11 import (Message, MessageEvent, MessageSegment,
                                         PrivateMessageEvent)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .utils import utils


class NewBing:
    def __init__(self) -> None:
        """初始化newbing, 标记cookie是否有效, 以及是否私聊启用"""
        self.cookie_allow = bool(utils.bing_cookies)
        self.reply_private: bool = utils.reply_private


    async def reserve_bing(
        self,
        matcher: Matcher, 
        event: MessageEvent
    ) -> None:
        await utils.newbing_new_chat(event=event, matcher=matcher)
        await matcher.send("newbing会话已重置", at_sender=True)


    async def pretreatment(
        self, 
        event: MessageEvent,
        matcher: Matcher, 
        msg: str
    ):  
        """稍微预处理一下"""
        uid = event.get_user_id()  # 获取用户id
        if not self.reply_private and isinstance(event, PrivateMessageEvent):
            await matcher.finish()          # 配置私聊不启用后，私聊信息直接结束处理
        if msg.isspace() or not msg:        # 如果消息为空或者全为空格, 则结束处理
            await matcher.finish()
        if not self.cookie_allow:
            await matcher.finish("cookie未设置, 无法访问")
        if msg in utils.nonsense:
            await matcher.finish(await utils.rand_hello())
        if uid not in utils.bing_chat_dict:
            await utils.newbing_new_chat(event=event, matcher=matcher)
            await matcher.send("newbing新会话已创建", at_sender=True)
        if utils.bing_chat_dict[uid]["isRunning"]:
            await matcher.finish("当前会话正在运行中, 请稍后再发起请求", at_sender=True)
        utils.bing_chat_dict[uid]["isRunning"] = True

        
    async def bing_handle(
        self,
        matcher: Matcher, 
        event: MessageEvent, 
        args: Message = CommandArg()
    ): 
        """newbing聊天的handle函数"""
        uid = event.get_user_id()  # 获取用户id
        msg = args.extract_plain_text()  # 获取消息
        
        await self.pretreatment(event=event, matcher=matcher, msg=msg)      # 预处理

        bot: Chatbot = utils.bing_chat_dict[uid]["chatbot"]  # 获取当前会话的Chatbot对象
        style: str = utils.bing_chat_dict[uid]["model"]  # 获取当前会话的对话样式
        try:  # 尝试获取bing的回复
            data = await bot.ask(prompt=msg, conversation_style=style)
        except Exception as e:  # 如果出现异常, 则返回异常信息, 并且将当前会话状态设置为未运行
            utils.bing_chat_dict[uid]["isRunning"] = False
            await matcher.finish(f'askError: {str(e)}多次askError请尝试"重置bing"', at_sender=True)
        utils.bing_chat_dict[uid]["isRunning"] = False  # 将当前会话状态设置为未运行
        if (
            data["item"]["result"]["value"] != "Success"
        ):  # 如果返回的结果不是Success, 则返回错误信息, 并且删除当前会话
            await matcher.send(
                "返回Error: " + data["item"]["result"]["value"] + "请重试", at_sender=True
            )
            del utils.bing_chat_dict[uid]
            return

        throttling = data["item"]["throttling"]  # 获取当前会话的限制信息
        # 获取当前会话的最大对话数
        max_conversation = throttling["maxNumUserMessagesInConversation"]
        # 获取当前会话的当前对话数
        current_conversation = throttling["numUserMessagesInConversation"]
        if len(data["item"]["messages"]) < 2:  # 如果返回的消息数量小于2, 则说明会话已经中断, 则删除当前会话
            await matcher.send("该对话已中断, 可能是被bing掐了, 正帮你重新创建会话", at_sender=True)
            await utils.newbing_new_chat(event=event, matcher=matcher)
            return
        # 如果返回的消息中没有text, 则说明提问了敏感问题, 则删除当前会话
        if "text" not in data["item"]["messages"][1]:
            await matcher.send(
                data["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"],
                at_sender=True,
            )
            return
        rep_message = await utils.bing_string_handle(
            data["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
        )  # 获取bing的回复, 并且稍微处理一下
        try:  # 尝试发送回复
            await matcher.send(
                f"{rep_message}\n\n当前{current_conversation} 共 {max_conversation}",
                at_sender=True,
            )
            if max_conversation <= current_conversation:
                await matcher.send("达到对话上限, 正帮你重置会话", at_sender=True)
                try:
                    await utils.newbing_new_chat(event=event, matcher=matcher)
                except Exception:
                    return
        except Exception as e:  # 如果发送失败, 则尝试把文字写在图片上发送
            try:
                await matcher.send(
                    f"文本消息可能被风控了\n错误信息:{str(e)}\n这里咱尝试把文字写在图片上发送了{MessageSegment.image(await utils.text_to_img(rep_message))}",
                    at_sender=True,
                )
            except Exception as eeee:  # 如果还是失败, 我也没辙了, 只能返回异常信息了
                await matcher.send(f"消息全被风控了, 这是捕获的异常: \n{str(eeee)}", at_sender=True)


# 实例化一个NewBing对象
newbing = NewBing()