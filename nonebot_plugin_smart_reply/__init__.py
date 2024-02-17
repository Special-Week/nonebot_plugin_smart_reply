import contextlib
import re

from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command, on_message, on_notice, on_regex
from nonebot.rule import to_me

from .getopenai import openai
from .keywordhandle import key_word_module

with contextlib.suppress(Exception):
    from nonebot.plugin import PluginMetadata

    __plugin_meta__ = PluginMetadata(
        name="smart_reply",
        description="nonebot2的融合了openai, newbing, 词库的智障回复插件",
        usage="""
openai [文本]  # 使用openai的api进行交互
@bot [文本]  # 使用词库进行交互
添加关键词 [关键词] 答 [回复]  # 添加自带词库的关键词
删除关键词 [关键词]  # 删除自带词库的关键词
删除关键词 [关键词] 删 [回复]  # 删除自带词库的关键词的一个回复
查看所有关键词  # 查看自带词库的所有关键词
查看关键词 [关键词]  # 查看自带词库的关键词的所有回复
重置openai  # 重置openai的会话
群内戳一戳bot  # 戳一戳bot触发
    """,
        type="application",
        homepage="https://github.com/Special-Week/nonebot_plugin_smart_reply",
        supported_adapters={"~onebot.v11"},
        extra={
            "author": "Special-Week",
            "link": "https://github.com/Special-Week/nonebot_plugin_smart_reply",
            "version": "0.13.114514",
            "priority": [1, 10, 11, 55, 999],
        },
    )


# 戳一戳响应器 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
on_notice(rule=to_me(), block=False, handlers=[key_word_module.poke_handle])

# 添加关键词响应器, 优先级11, 条件: 正则表达式
on_regex(
    r"^添加关键词\s*(\S+.*?)\s*答\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=11,
    permission=SUPERUSER,
    handlers=[key_word_module.add_new_keyword],
)

# 查看所有关键词响应器, 优先级11, 条件: 命令头
on_command(
    "查看所有关键词",
    aliases={"查询所有关键词"},
    block=True,
    priority=11,
    permission=SUPERUSER,
    handlers=[key_word_module.check_all_keyword],
)

# 删除关键词响应器, 优先级11, 条件: 命令头
on_command(
    "删除关键词",
    priority=11,
    block=True,
    permission=SUPERUSER,
    handlers=[key_word_module.del_keyword_handle],
)

# 删除关键词的一个回复响应器, 优先级10, 条件: 正则表达式
on_regex(
    r"^删除关键词\s*(\S+.*?)\s*删\s*(\S+.*?)\s*$",
    flags=re.S,
    priority=10,
    permission=SUPERUSER,
    handlers=[key_word_module.del_akeyword_handle],
)

# 普通回复响应器, 优先级999, 条件: 艾特bot就触发
on_message(
    rule=to_me(), priority=999, block=False, handlers=[key_word_module.regular_reply]
)

# 查看关键词响应器
on_command(
    "查看关键词",
    aliases={"查询关键词"},
    priority=11,
    block=True,
    permission=SUPERUSER,
    handlers=[key_word_module.check_keyword_handle],
)


# 使用openai的响应器
on_command(
    "openai",
    aliases={"求助"},
    block=True,
    priority=55,
    handlers=[openai.openai_handle],
)
on_command(
    "重置openai",
    aliases={"重置会话", "openai重置", "会话重置"},
    priority=10,
    block=True,
    handlers=[openai.reserve_openai],
)
