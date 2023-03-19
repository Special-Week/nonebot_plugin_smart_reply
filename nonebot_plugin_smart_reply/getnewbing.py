from EdgeGPT import Chatbot
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent
)


from .txtToImg import txt_to_img
from .utils import(
    hello,
    newbing_new_chat,
    bing_string_handle,
    bing_cookies,
    reply_private,
    bing_chat_dict,
)





async def bing_handle(matcher:Matcher,event:MessageEvent,args: Message = CommandArg()):
    # 配置私聊不启用后，私聊信息直接结束处理
    if not reply_private and isinstance(event, PrivateMessageEvent):
        return
    uid = event.get_user_id()               # 获取用户id
    msg = args.extract_plain_text()         # 获取消息
    if bing_cookies == []:                       # 如果cookies为空, 则无法访问bing
        await matcher.finish("cookie未设置, 无法访问")
    if msg.isspace() or msg == "" :
        return
    if (msg in ["你好啊", "你好", "在吗", "在不在", "您好", "您好啊", "你好", "在"]):  
        # 如果消息为空或者是一些无意义的问候, 则返回一些问候语
        await matcher.finish(hello())


    if uid not in bing_chat_dict:                # 如果用户id不在会话字典中, 则新建一个会话
        await newbing_new_chat(event=event, matcher=matcher, user_id=uid)
        await matcher.send("newbing新会话已创建", at_sender=True)
    if bing_chat_dict[uid]["isRunning"]:             # 如果当前会话正在运行, 则返回正在运行
        await matcher.finish("当前会话正在运行中, 请稍等", at_sender=True)
    bing_chat_dict[uid]["isRunning"] = True          # 将当前会话状态设置为运行中
    bot: Chatbot = bing_chat_dict[uid]["Chatbot"]     # 获取当前会话的Chatbot对象
    style: str = bing_chat_dict[uid]["model"]         # 获取当前会话的对话样式
    try:                                    # 尝试获取bing的回复
        data = await bot.ask(prompt=msg, conversation_style=style)
    except Exception as e:                # 如果出现异常, 则返回异常信息, 并且将当前会话状态设置为未运行
        bing_chat_dict[uid]["isRunning"] = False
        await matcher.finish("askError: " + str(e) + "多次askError请尝试\"重置bing\"", at_sender=True)
    bing_chat_dict[uid]["isRunning"] = False     # 将当前会话状态设置为未运行
    if data["item"]["result"]["value"] != "Success":  # 如果返回的结果不是Success, 则返回错误信息, 并且删除当前会话
        await matcher.send("返回Error: " + data["item"]["result"]["value"] + "请重试", at_sender=True)
        del bing_chat_dict[uid]
        return

    throttling = data["item"]["throttling"]     # 获取当前会话的限制信息
    # 获取当前会话的最大对话数
    maxConversation = throttling["maxNumUserMessagesInConversation"]
    # 获取当前会话的当前对话数
    currentConversation = throttling["numUserMessagesInConversation"]
    if len(data["item"]["messages"]) < 2:       # 如果返回的消息数量小于2, 则说明会话已经中断, 则删除当前会话
        await matcher.send("该对话已中断, 可能是被bing掐了, 正帮你重新创建会话", at_sender=True)
        await newbing_new_chat(event=event, matcher=matcher, user_id=uid)
        return
    # 如果返回的消息中没有text, 则说明提问了敏感问题, 则删除当前会话
    if "text" not in data["item"]["messages"][1]:
        await matcher.send(data["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"], at_sender=True)
        return
    repMessage = bing_string_handle(
        data["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"])  # 获取bing的回复, 并且稍微处理一下
    try:                                # 尝试发送回复
        if maxConversation > currentConversation:   # 如果当前对话数小于最大对话数, 则正常发送
            await matcher.send(repMessage + f"\n\n当前{currentConversation} 共 {maxConversation}", at_sender=True)
        else:                                # 如果当前对话数大于等于最大对话数, 先发送, 然后说不定帮你重置会话
            await matcher.send(repMessage + f"\n\n当前{currentConversation} 共 {maxConversation}", at_sender=True)
            await matcher.send("达到对话上限, 正帮你重置会话", at_sender=True)
            try:                # 因为重置会话可能遇到matcher.finish()的情况, 而finish()是通过抛出异常实现的, 我怕跑到下面的except里面去, 所以这里用try包一下, 然后直接return
                await newbing_new_chat(event=event, matcher=matcher, user_id=uid)
            except:
                return
    except Exception as e:            # 如果发送失败, 则尝试把文字写在图片上发送
        try:
            await matcher.send("文本消息被风控了, 这里咱尝试把文字写在图片上发送了"+MessageSegment.image(txt_to_img(repMessage)), at_sender=True)
        except Exception as eeee:   # 如果还是失败, 我也没辙了, 只能返回异常信息了
            await matcher.send(f"消息全被风控了, 这是捕获的异常: {str(eeee)}", at_sender=True)



async def reserve_Bing(matcher:Matcher,event:MessageEvent):
    uid = event.get_user_id()               # 获取用户id
    await newbing_new_chat(event=event, matcher=matcher, user_id=uid)
    await matcher.send("newbing会话已重置", at_sender=True)


