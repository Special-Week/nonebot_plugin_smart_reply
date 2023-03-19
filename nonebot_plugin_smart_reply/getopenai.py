from revChatGPT.V3 import Chatbot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent
)


from .txtToImg import txt_to_img
from .utils import (
    hello,
    openai_new_chat,

    reply_private,
    openai_api_key,
    openai_chat_dict,
)

async def openai_handle(matcher:Matcher,event:MessageEvent,args: Message = CommandArg()):
    # 配置私聊不启用后，私聊信息直接结束处理
    if not reply_private and isinstance(event, PrivateMessageEvent):
        return
    uid = event.get_user_id()               # 获取用户id
    msg = args.extract_plain_text()         # 获取消息
    if openai_api_key == []:
        await matcher.finish("openai_api_key未设置, 无法访问")
    if (msg.isspace() or msg == "" or msg in [
        "你好啊",
        "你好",
        "在吗",
        "在不在",
        "您好",
        "您好啊",
        "你好",
        "在",
    ]):                                     # 如果消息为空或者是一些无意义的问候, 则返回一些问候语
        await matcher.finish(hello())

    if uid not in openai_chat_dict:                # 如果用户id不在会话字典中, 则新建一个会话
        _ = await openai_new_chat(event=event, matcher=matcher, user_id=uid)
        await matcher.send("openai新会话已创建", at_sender=True)
    if openai_chat_dict[uid]["isRunning"]:             # 如果当前会话正在运行, 则返回正在运行
        await matcher.finish("当前会话正在运行中, 请稍等", at_sender=True)
    openai_chat_dict[uid]["isRunning"] = True          # 将当前会话状态设置为运行中
    bot: Chatbot = openai_chat_dict[uid]["Chatbot"]     # 获取当前会话的Chatbot对象
    try:
        data = bot.ask(msg)
    except Exception as e:                # 如果出现异常, 则返回异常信息, 并且将当前会话状态设置为未运行
        openai_chat_dict[uid]["isRunning"] = False
        await matcher.finish("askError: " + str(e) + "多次askError请尝试\"重置会话\"", at_sender=True)
    try:
        await matcher.send(data, at_sender=True)
    except Exception as e:
        try:
            await matcher.send(f"文本消息被风控了,错误信息:{str(e)}, 这里咱尝试把文字写在图片上发送了"+MessageSegment.image(txt_to_img(data)), at_sender=True)
        except Exception as eeee:
            await matcher.send(f"消息全被风控了, 这是捕获的异常: {str(eeee)}", at_sender=True)
    




async def reserve_OP(matcher:Matcher,event:MessageEvent):
    uid = event.get_user_id()               # 获取用户id
    await openai_new_chat(event=event, matcher=matcher, user_id=uid)
    await matcher.send("openai会话已重置", at_sender=True)

