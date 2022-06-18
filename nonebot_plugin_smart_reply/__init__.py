from nonebot.plugin.on import on_message, on_notice
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    PokeNotifyEvent,
    Bot
)
from .utils import *

# 优先级99, 条件: 艾特bot就触发
ai = on_message(rule=to_me(), priority=99,block=False)
# 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
poke_ = on_notice(block=False)


@ai.handle()
async def _(event: MessageEvent):
    # 获取消息文本
    msg = get_message_text(event.json())
    if "CQ:xml" in str(event.get_message()):
        return
    # 如果是光艾特bot(没消息返回)或者打招呼的话,就回复以下内容
    if (not msg) or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "你好",
        "在",
    ]:
        await ai.finish(Message(random.choice(hello__reply)))
    # 获取用户nickname
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 从字典里获取结果
    result = await get_chat_result(msg,  nickname)
    # 如果词库没有结果，则调用qingyunke获取智能回复
    if result == None:
        url = f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}"
        message = await get_reply(url)
        await ai.finish(message=message)
    await ai.finish(Message(result))


@poke_.handle()
async def _poke_event(bot: Bot, event: PokeNotifyEvent) -> bool:
    # 如果戳一戳对象是自己
    if event.is_tome():
        # 随机回复poke__reply中的一条
        await poke_.send(message=f"{random.choice(poke__reply)}")
