import asyncio
from .utils import *
from typing import Tuple
from loguru import logger
from nonebot.rule import to_me
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.message import event_preprocessor
from nonebot.exception import IgnoredException
from nonebot.params import CommandArg, RegexGroup, ArgPlainText
from nonebot.plugin.on import on_message, on_notice, on_command, on_regex
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    NotifyEvent,
    MessageEvent,
    MessageSegment,
    PokeNotifyEvent,
    GroupMessageEvent,
    PrivateMessageEvent
)


openai_cd_dir = {}  # 用于存放cd时间

# 添加和删除关键词
add_new = on_regex(
    r"^添加关键词\s*(\S+.*?)\s*答\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=11,
    rule=to_me(),
    permission=SUPERUSER,
)
check_new = on_command(
    "查看关键词",
    aliases={"查询关键词"},
    block=True,
    priority=11,
    rule=to_me(),
    permission=SUPERUSER,
)
check_all = on_command(
    "查看所有关键词",
    aliases={"查询所有关键词"},
    block=True,
    priority=11,
    rule=to_me(),
    permission=SUPERUSER,
)
del_new = on_command(
    "删除关键词",
    block=True,
    priority=11,
    rule=to_me(),
    permission=SUPERUSER,
)
del_new_list = on_regex(
    r"^删除关键词\s*(\S+.*?)\s*删\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=10,
    rule=to_me(),
    permission=SUPERUSER,
)
bingchat = on_command("bing", priority=10, block=True)      # bing主要的响应器
reserve = on_command("重置会话", priority=10, block=True)       # 重置会话
su_help = on_command("su_help", priority=10, block=True)        # 消息转发给su
release_count = on_command("释放违规",aliases={"解禁bing"}, permission=SUPERUSER, priority=1, block=True)      # 释放用户违规次数
add_blacklist = on_command("添加黑名单", permission=SUPERUSER, priority=1, block=True)      # 添加黑名单(全局)
del_blacklist = on_command("删除黑名单", permission=SUPERUSER, priority=1, block=True)      # 删除黑名单(全局)
# 优先级99, 条件: 艾特bot就触发
ai = on_message(rule=to_me(), priority=99, block=False)
# 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
poke_ = on_notice(rule=to_me(), block=False)
# 使用openai的接口, 优先级5
openai_text = on_command(
    "求助", aliases={"请问", "帮忙"}, block=True, priority=5, rule=to_me())


@add_new.handle()
async def _(
    matched: Tuple[str, ...] = RegexGroup(),
):
    word1, word2 = matched
    if add_(word1, word2) == "寄":
        await add_new.finish("这个关键词已经记住辣")
    else:
        await add_new.finish("我记住了\n关键词："+word1+"\n回复："+word2)


@check_new.handle()
async def _(
    matcher: Matcher,
    args: Message = CommandArg()
):
    word1 = args.extract_plain_text()
    if word1:
        matcher.set_arg("word", args)


@check_new.got("word", prompt="你要查看哪个关键词（查看所有关键词指令：查看所有关键词）")
async def _(tag: str = ArgPlainText("word")):
    mes = check_(tag)
    if mes == "寄":
        await add_new.finish("抱歉没有记过这个关键词捏，请输入[查询所有关键词]来获取全部关键词")
    else:
        output = text_to_png(mes) # 将文字转换为图片
        await add_new.finish(MessageSegment.image(output))


@check_all.handle()
async def _():
    mes = check_al()
    output = text_to_png(mes)
    await add_new.finish(MessageSegment.image(output))

@del_new.handle()
async def _(args: Message = CommandArg()):
    key = args.extract_plain_text()
    if key=="" or key.isspace():
        await del_new.finish("没有关键词，del失败")
    else:
        try:
            del AnimeThesaurus[key]
            with open(Path(__file__).parent.joinpath('resource/json/data.json'), "w", encoding="utf8") as f_new:
                json.dump(AnimeThesaurus, f_new, ensure_ascii=False, indent=4)
            await del_new.send("已删除该关键词下所有回复~")
        except:
            await del_new.finish("del失败, 貌似没有这个关键词呢")

@del_new_list.handle()
async def _(
    matched: Tuple[str, int] = RegexGroup(),
):
    word1, word2 = matched
    if del_(word1, word2) == "寄":
        await del_new_list.finish("找不到关键词或回复序号，请用查看命令核对")
    else:
        await del_new_list.finish("删除成功~")




@ai.handle()
async def _(event: MessageEvent):
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
        await ai.finish(Message(random.choice(hello__reply)))
    # 获取用户nickname
    if isinstance(event, GroupMessageEvent):
        nickname = event.sender.card or event.sender.nickname
    else:
        nickname = event.sender.nickname
    # 从字典里获取结果
    result = await get_chat_result(msg,  nickname)
    # 如果词库没有结果，则调用api获取智能回复
    if result == None:
        qinyun_url = f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}"
        message = await qinyun_reply(qinyun_url)
        logger.info("来自青云客的智能回复: " + message)
        await ai.finish(message=message)
    await ai.finish(Message(result))


@poke_.handle()
async def _(event: PokeNotifyEvent):
    if event.is_tome:
        probability = random.random() # 生成0-1之间的随机数
        # 33%概率回复莲宝的藏话
        if probability < 0.33:
            # 发送语音需要配置ffmpeg, 这里try一下, 不行就随机回复poke__reply的内容
            try:
                await poke_.send(MessageSegment.record(Path(aac_file_path)/random.choice(aac_file_list)))
            except:
                await poke_.send(message=f"{random.choice(poke__reply)}")
        elif probability > 0.66:
            # 33% 概率戳回去
            await poke_.send(Message(f"[CQ:poke,qq={event.user_id}]"))
        # probability在0.33和0.66之间的概率回复poke__reply的内容
        else:
            await poke_.send(message=f"{random.choice(poke__reply)}")


@openai_text.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if openai_api_key == "寄":
        # 没有配置openai_api_key
        await openai_text.finish("请先配置openai_api_key")
    prompt = msg.extract_plain_text()                               # 获取文本
    if prompt == "" or prompt == None or prompt.isspace():
        await openai_text.finish("需要提供文本prompt")                  # 没有提供文本

    qid = event.get_user_id()                                       # 获取用户id
    try:
        cd = event.time - openai_cd_dir[qid]
    except KeyError:
        cd = cd_time + 1
    if (
        cd > cd_time
        or event.get_user_id() in nonebot.get_driver().config.superusers
    ):                                                                          # 超过cd时间或者是超级用户
        # 记录cd
        openai_cd_dir.update({qid: event.time})
        await openai_text.send(MessageSegment.text(f"让{Bot_NICKNAME}想想吧..."))        # 发送消息
        loop = asyncio.get_event_loop()                                # 获取事件循环
        try:
            # 开一个不会阻塞asyncio的线程调用get_openai_reply函数
            res = await loop.run_in_executor(None, get_openai_reply, prompt)
        except Exception as e:                                        # 如果出错
            await openai_text.finish("Error: " + str(e))                       # 发送错误信息
        # 发送结果, 长消息根据账号可能会报错风控, 这里try一下, 不行就发送图片
        try:
            await openai_text.send(MessageSegment.text(res), at_sender=True)
        except:
            await openai_text.send("文本消息被风控了, 这里咱尝试把文字写在图片上发送了"+MessageSegment.image(text_to_png(res)))
        # 图片都发不出去那没办法了
    else:
        await openai_text.finish(
            MessageSegment.text(
                f"让{Bot_NICKNAME}的脑子休息一下好不好喵, {cd_time - cd:.0f}秒后才能再次使用"),   # 发送cd时间
            at_sender=True
        )


@bingchat.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    uid = event.get_user_id()     # 获取用户id
    if uid in ban_list:         # 如果用户在黑名单中, 则直接返回
        await bingchat.finish(f"阈值大于{THRESHOLD}, 你已被ban, 请通过bot联系SUPERUSER, su会根据数据库记录的信息自行决定是否清空count, 命令头“su_help”, 后接内容\n别重复发, 要是不断通过bot转发给su, 该用户所有事件将永久禁用, 群聊也会退出", at_sender=True)
    msg: str = msg.extract_plain_text()     # 获取消息
    if cookies == {}:       # 如果cookies为空, 则直接返回
        await bingchat.finish("cookie未设置, 无法访问")
    if (msg.isspace() or msg == ""):        # 如果消息为空, 则直接返回
        await bingchat.finish("请告诉我你要交流什么", at_sender=True)
    if uid not in chat_dict:                # 如果用户不在会话字典中, 则创建会话
        _ = await new_chat_(uid)            # 创建会话
        await bingchat.send("新会话已创建, 请稍等, 当前模式creative, 如要切换对话样式请发送“重置会话”， 并附带参数 balanced 或者 creative 或 precise",at_sender=True)
    bot: Chatbot = chat_dict[uid]["Chatbot"]        # 获取用户的Chatbot
    style: str = chat_dict[uid]["model"]            # 获取用户的对话模式

    try:                                            # 从头try到尾
        data = await bot.ask(prompt=msg, conversation_style=style)      # 获取响应, 这一部分是最耗时的
        if data["item"]["result"]["value"]!="Success":                  # 如果返回的结果不是Success, 则直接返回
            await bingchat.send("返回Error: " + data["item"]["result"]["value"], at_sender=True)
            return
        throttling = data["item"]["throttling"]             # 获取限制信息
        maxConversation = throttling["maxNumUserMessagesInConversation"]            # 获取最大对话数
        currentConversation = throttling["numUserMessagesInConversation"]           # 获取当前对话数
        if len(data["item"]["messages"]) < 2:                                       # 如果返回的消息长度小于2, 那么他没回答你消息, 很可能是被掐断了
            await bingchat.send("Error, 该对话已中断, 可能已被bing切断, 已帮你重置会话", at_sender=True)
            _ = await new_chat_(user_id = uid)             # 重置会话并且return
            return
        if "text" not in data["item"]["messages"][1]:                          # 如果返回的消息中没有text, 那么他没回答你消息, 很可能是你问了敏感问题
            if uid in user_info:                                    # 如果用户在用户信息中, 则将用户的违规次数+1
                user_info[uid]["violation"] += 1
            else:                                        # 如果用户不在用户信息中, 则创建用户信息, 并且将用户的违规次数设置为1
                user_info[uid] = {"violation": 1} 
            save_user_info()                                # 持久存储用户信息
            count = user_info[uid]["violation"]         # 获取用户的违规次数
            if count > THRESHOLD:                       # 如果用户的违规次数大于阈值, 则将用户加入黑名单
                ban_list.append(uid)            
            await bingchat.send(data["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"], at_sender=True)     # 发送一条text, 一般是违规内容固定的回答
            await bingchat.send(f"bot好像检测到你问了敏感问题, 已被记录次数, 超过阈值({THRESHOLD})会被禁用该功能请注意当前count = {count}\n如被ban想解封请通过bot转发给SUPERUSER, su会根据数据库记录的信息自行决定是否清空count, 命令头“su_help”, 后接内容\n要是不断通过bot转发给su, 该用户将永久禁用, 群聊也会退出",at_sender=True) # 提示消息
            await push_sql(user_id = uid, user_name = event.sender.nickname, content=msg, isrational=False)   # 将用户的违规信息存入数据库, 并且return
            return
        await push_sql(user_id = uid, user_name = event.sender.nickname, content=msg, isrational=True)      # 将用户的正常信息存入数据库
        if maxConversation > currentConversation:       # 没超过最大上限, 直接发送
            await bingchat.send(data["item"]["messages"][1]["text"] + f"\n\n当前{currentConversation} 共 {maxConversation}", at_sender=True)
        else:                                    # 超过最大上限, 发送并且重置会话
            await bingchat.send(data["item"]["messages"][1]["text"]+ f"\n\n当前{currentConversation} 共 {maxConversation}", at_sender=True) 
            _ = await new_chat_(event.get_user_id())
            await bingchat.send("达到对话上限, 已自动重置会话", at_sender=True)
    except Exception as e:      # 如果出现异常, 则直接发送报错信息, 防止bot无反应
        await bingchat.send("Error: " + str(e), at_sender=True)


@reserve.handle()
async def _(event: MessageEvent,msg: Message = CommandArg()):
    """重置会话"""
    user_id = event.get_user_id()       # 获取用户id
    msg: str = msg.extract_plain_text()     # 获取参数
    if msg not in ["balanced", "creative", "precise"]:      # 如果参数不在这三个中, 则直接重置会话
        _ = await new_chat_(user_id=user_id)    # 重置会话
        await reserve.finish("缺少参数或参数错误, 请使用 balanced 或者 creative 或 precise, 这里只能默认给你重置成creative")
    else:
        await reserve.finish(await new_chat_(user_id, msg))  # 重置会话并且返回结果


@su_help.handle()
async def _(bot:Bot,event: MessageEvent, msg: Message = CommandArg()):
    """转发给su"""
    uid = event.get_user_id()
    msg = msg.extract_plain_text()
    reply = f"来自{uid}的消息: {msg}"
    if isinstance(event,GroupMessageEvent): # 如果是群聊, 则获取群号加到后面
        gid = str(event.group_id)
        reply+=f"\n来自群{gid}"
    su = SU_LIST[0]
    await bot.send_private_msg(user_id=su, message=reply)
    await su_help.finish("已转发给su, 请耐心等待回复, 请勿重复发送, 重复发送直接ban")
    

@release_count.handle()
async def _(msg: Message = CommandArg()):
    """清空用户的违规次数"""
    msg = msg.extract_plain_text()
    if msg not in ban_list:
        await release_count.finish("该用户不存在")
    user_info[msg]["violation"] = 0
    ban_list.remove(msg)
    save_user_info()
    await release_count.finish("已清空该用户的违规次数")


@event_preprocessor
async def event_preblock(event: Event, bot: Bot):
    """事件预处理器，阻断黑名单用户的事件"""
    if isinstance(event, MessageEvent) or isinstance(event, NotifyEvent):
        """阻断黑名单用户的消息事件和通知事件"""
        if not event.get_user_id() in bot.config.superusers:        # 超级用户不受限制
            if event.get_user_id() in blackdata["user"]:            # 如果用户在黑名单中, 则阻断
                blockreason = "user in blacklist"                   # 阻断原因
                logger.info(f'当前事件已阻断，原因：{blockreason}')   # 记录日志
                raise IgnoredException(blockreason)                 # 抛出异常(阻断事件)


@add_blacklist.handle()
async def _(msg: Message = CommandArg()):
    """添加黑名单"""
    msg: str = msg.extract_plain_text()     # 获取参数
    if msg.isspace() or msg == "":      # 如果参数为空, 则返回错误
        await add_blacklist.finish("参数错误")
    if msg.isdigit():               # 如果参数是数字, 则添加到黑名单
        blackdata["user"].append(msg)
    else:                        # 如果参数不是数字, 则返回错误
        await add_blacklist.finish("参数错误")
    await add_blacklist.send(f"id{msg}添加成功")
    with open(Path(__file__).parent.joinpath('blacklist.json'), "w", encoding="utf8") as f_new:
        json.dump(blackdata, f_new, ensure_ascii=False, indent=4)   # 将黑名单数据写入文件




@del_blacklist.handle()
async def _(msg: Message = CommandArg()):
    """删除黑名单"""
    msg: str = msg.extract_plain_text()   # 获取参数
    if msg.isspace() or msg == "":  # 如果参数为空, 则返回错误
        await del_blacklist.finish("参数错误")
    if msg.isdigit():   # 如果参数是数字, 则尝试删除黑名单
        try:    
            blackdata["user"].remove(msg)
        except ValueError:
            value = str(blackdata["user"])
            await del_blacklist.finish("参数错误, 列表中只存在:" + value)
    else:
        await del_blacklist.finish("参数错误")
    await del_blacklist.send("删除成功")
    with open(Path(__file__).parent.joinpath('blacklist.json'), "w", encoding="utf8") as f_new:
        json.dump(blackdata, f_new, ensure_ascii=False, indent=4)

                  