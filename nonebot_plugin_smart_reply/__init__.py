from nonebot.plugin.on import on_message, on_notice, on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    PokeNotifyEvent,
    MessageSegment
)
from .utils import *
from loguru import logger
import asyncio

try:
    cd_time = nonebot.get_driver().config.openai_cd_time
except:
    cd_time = 60        # 默认cd时间为60秒

openai_cd_dir = {}  # 用于存放cd时间


# 这个值为False时, 使用的是小爱同学, True时使用的是青云客api
api_flag = True
# 优先级1, 向下阻断, 需要艾特bot, 智能回复api切换指令, 目前有俩api, 分别是qinyunke_api和小爱同学, 默认qinyun
api_switch = on_command("智障回复api切换", aliases={
                        "ai切换", "api_switch", "智能回复api切换"}, permission=SUPERUSER, rule=to_me(), block=True)
# 优先级99, 条件: 艾特bot就触发
ai = on_message(rule=to_me(), priority=99, block=False)
# 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
poke_ = on_notice(rule=to_me(), block=False)
# 使用openai的接口, 优先级5
openai_text = on_command(
    "求助", aliases={"请问", "帮忙"}, block=True, priority=5, rule=to_me())



@api_switch.handle()
async def _():
    global api_flag
    api_flag = not api_flag
    await api_switch.send(message=f"切换成功, 当前智能回复api为{'青云客' if api_flag else '小爱同学'}")


@ai.handle()
async def _(event: MessageEvent):
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
        if api_flag:
            qinyun_url = f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={msg}"
            message = await qinyun_reply(qinyun_url)
            logger.info("来自青云客的智能回复: " + message)
        else:
            xiaoai_url = f"https://apibug.cn/api/xiaoai/?msg={msg}&apiKey={apiKey}"
            if apiKey == "寄":
                await ai.finish("小爱同学apiKey未设置, 请联系SUPERUSERS在.env中设置")
            message = await xiaoice_reply(xiaoai_url)
            if message == "寄":
                await ai.finish("小爱同学apiKey错误, 请联系SUPERUSERS在.env中重新设置")
            logger.info("来自小爱同学的智能回复: " + message)
        await ai.finish(message=message)
    await ai.finish(Message(result))


@poke_.handle()
async def _poke_event(event: PokeNotifyEvent):
    if event.is_tome:
        # 50%概率回复莲宝的藏话
        if random.random() < 0.5:
            # 发送语音需要配置ffmpeg, 这里try一下, 不行就随机回复poke__reply的内容
            try:
                await poke_.send(MessageSegment.record(Path(aac_file_path)/random.choice(aac_file_list)))
            except:
                await poke_.send(message=f"{random.choice(poke__reply)}")
        # 随机回复poke__reply的内容
        else:
            await poke_.send(message=f"{random.choice(poke__reply)}")

@openai_text.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if api_key == "寄":                             
        await openai_text.finish("请先配置openai_api_key")          # 没有配置openai_api_key
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
        await openai_text.send(MessageSegment.text("让本喵想想吧..."))        # 发送消息
        loop = asyncio.get_event_loop()                                # 获取事件循环
        try:
            res = await loop.run_in_executor(None, get_openai_reply, prompt)        # 开一个不会阻塞asyncio的线程调用get_openai_reply函数
        except Exception as e:                                        # 如果出错
            await openai_text.finish(str(e))                       # 发送错误信息
        await openai_text.finish(MessageSegment.text(res),at_sender=True)   # 发送结果
    else:
        await openai_text.finish(
            MessageSegment.text(f"让本喵的脑子休息一下好不好喵, {cd_time - cd:.0f}秒后才能再次使用"),   # 发送cd时间
            at_sender=True
        )
