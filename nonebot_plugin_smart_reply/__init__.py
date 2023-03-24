import re

from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command, on_message, on_notice, on_regex
from nonebot.rule import to_me

from .getnewbing import newbing
from .getopenai import openai
from .keywordhandle import key_word_module

# 戳一戳响应器 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
poke_ = on_notice(rule=to_me(), block=False, handlers=[key_word_module.poke_handle])

# 添加关键词响应器, 优先级11, 条件: 正则表达式
add_new = on_regex(
    r"^添加关键词\s*(\S+.*?)\s*答\s*(\S+.*?)\s*$",
    flags=re.S,
    block=True,
    priority=11,
    permission=SUPERUSER,
    handlers=[key_word_module.add_new_keyword],
)

# 查看所有关键词响应器, 优先级11, 条件: 命令头
check_all = on_command(
    "查看所有关键词",
    aliases={"查询所有关键词"},
    block=True,
    priority=11,
    permission=SUPERUSER,
    handlers=[key_word_module.check_all_keyword],
)

# 删除关键词响应器, 优先级11, 条件: 命令头
del_keyword = on_command(
    "删除关键词", priority=11,block=True, permission=SUPERUSER, handlers=[key_word_module.del_keyword_handle]
)

# 删除关键词的一个回复响应器, 优先级10, 条件: 正则表达式
del_akeyword = on_regex(
    r"^删除关键词\s*(\S+.*?)\s*删\s*(\S+.*?)\s*$",
    flags=re.S,
    priority=10,
    permission=SUPERUSER,
    handlers=[key_word_module.del_akeyword_handle],
)

# 普通回复响应器, 优先级999, 条件: 艾特bot就触发
regular = on_message(rule=to_me(), priority=999, block=False, handlers=[key_word_module.regular_reply])

# 查看关键词响应器
check_new = on_command(
    "查看关键词",
    aliases={"查询关键词"},
    priority=11,
    block=True,
    permission=SUPERUSER,
    handlers=[key_word_module.check_keyword_handle],
)

# 使用bing的响应器
bingchat = on_command(
    "bing",
    priority=55,
    block=True,
    handlers=[newbing.bing_handle],
)
reserveBing = on_command(
    "重置bing",
    aliases={"重置会话", "bing重置", "会话重置"},
    priority=10,
    block=True,
    handlers=[newbing.reserve_bing],
)

# 使用openai的响应器
openai_text = on_command(
    "openai",
    aliases={"求助"},
    block=True,
    priority=55,
    handlers=[openai.openai_handle],
)
reserveOp = on_command(
    "重置openai",
    aliases={"重置会话", "openai重置", "会话重置"},
    priority=10,
    block=True,
    handlers=[openai.reserve_openai],
)
