# nonebot2智能(障)回复插件

    问问提前请务必看完readme, 这是一个融合了openai, 词库的智障回复插件
    
### 提醒, openai国内服务器需要科学上网才可调用, 希望你能熟练使用v2ray或clash或其他代理软件



## 功能

    艾特bot时回复一些基于词库的消息, 戳一戳回复特定的消息或者语音以及反戳
    接入了openai apikey的接口, 详情见下文
    接入了青云客的接口

## 词库添加关键词:
	1、添加关键词 [text1] 答 [text2]		 
	2、查看关键词 [text1]
	3、查看所有关键词
	4、删除关键词 [text1]
	5、删除关键词 [text1] 删 [number]
	注: 其中1，5相应器用的是on_regex, 其余全是on_command, 请注意是否需要带上.env响应头command_start
	    删除关键词的[number]可以用指令第二个查询查询
	    查看关键词,查看所有关键词采取的是输出图片的形式发送的, 如果这两个功能用的时候报错, 那么我猜测你的Linux没有simsun.ttc(宋体)这个字体
	    解决方案: 源码内txtToImg.py中函数txt_to_img第三个参数font_path的值, 换成你系统有的字体, 或者安装simsun.ttc这个字体

### 安装方式:

    nb plugin install nonebot-plugin-smart-reply
    pip install nonebot-plugin-smart-reply
    git clone https://github.com/Special-Week/nonebot_plugin_smart_reply.git
    Download Zip

### env配置项:

|config          |type            |default    |example                                  |usage                                   |
|----------------|----------------|-----------|-----------------------------------------|----------------------------------------|
| bot_nickname   | string         |我     |Bot_NICKNAME = "Hinata"                  |      你Bot的称呼                         |
| ai_reply_private  | boolean |false     |ai_reply_private = true          |    私聊时是否启用AI聊天            |
| openai_api_key    | list  |寄        |openai_api_key = ["aabb114514"]    |    openai的api_key, 详细请看下文         |
| openai_max_tokens | int     |1000      |openai_max_tokens = 1500         |    openai的max_tokens, 详细请看下文     |
| openai_cd_time    | int     |600        |openai_cd_time = 114             |    openai创建会话的cd                       |
| openai_max_conversation|int|10|openai_max_conversation = 10|openai的单个会话点最大交互数量|
|openai_proxy|str       |""         |openai_proxy = "http://127.0.0.1:1081" |    openai或者newbing的代理, 配置详细请看下文|        


.env完全不配置不影响插件运行, 但是部分功能会无法使用(openai)
config这里会有一个读取superusers, 如果你env没有配置在su = random.choice(utils.superuser)这里应该会报错, 但我觉得你创建项目时应该就至少配置了一个的



对戳一戳的反应. 33%概率回复莲宝的藏话(发送语音需要配置好ffmpeg), 33%的概率回复poke__reply的内容, 剩下的概率戳回去, 如果想改概率的话, 找到@poke_.handle()下的函数, 根据注释改概率, 莲包的藏话放在了插件目录下的resource/audio, 想加可以任意


但由于优先级较低(数字越大越低), 可能被其他插件阻断, 如果没反应请查看控制台判断被哪个插件的on_message阻断了, 然后自行拉高或者降低相关响应器的优先级, 响应器见结尾


​       
## 关于openai:

    1. openai_api_key请注册openai后在 https://beta.openai.com/account/api-keys 自己获取
    2. openai_max_tokens貌似是ai返回的文本最大多少(根据我自己用的经验)
    3. openai_api_key必须配置, openai_max_tokens随意, 有默认值(1000)
    4. 需要配置代理, 否则无法使用, 代理配置详细请看下文
    5. 这个模块貌似不是免费的, 注册的账号只有$18.00的免费额度(现在缩成了5刀??), 请注意使用
    6. openai_api_key要求你填的是list, 创建会话的时候会随机从list选一个, 你可以填多个, 注意观察加载插件的时候, log会提示你加载了几个apikey
    7. 尽量保证revChatGPT模块是最新(pip install revChatGPT --upgrade)


    用法:
        1. openai + 内容, 和openai发起会话, 如果没有会新建会话
        2. 重置openai, 重置openai的会话
    
    使用了与openai通讯的接口 [ChatGPT](https://github.com/acheong08/ChatGPT)        






## bopenai_proxy的配置:

    1. 你需要使用v2ray或者clash等代理工具开启本地监听端口
    2. 由于httpx的陈年老bug, socks5代理应该用不了, 请使用http代理 
    3. 以v2rayN举例, 本地监听端口1080, 你应该配置成"http://127.0.0.1:1081"(http = socks5 + 1)
    4. 以clash for windows举例, 本地监听端口7890, 你应该配置成"http://127.0.0.1:7890"





响应器:
```python
# 戳一戳响应器 优先级1, 不会向下阻断, 条件: 戳一戳bot触发
on_notice(rule=to_me(), block=False, handlers=[key_word_module.poke_handle])
# 添加关键词响应器, 优先级11, 条件: 正则表达式
on_regex(r"^添加关键词\s*(\S+.*?)\s*答\s*(\S+.*?)\s*$", flags=re.S, block=True, priority=11, permission=SUPERUSER, handlers=[key_word_module.add_new_keyword])
# 查看所有关键词响应器, 优先级11, 条件: 命令头
on_command("查看所有关键词", aliases={"查询所有关键词"}, block=True, priority=11, permission=SUPERUSER, handlers=[key_word_module.check_all_keyword])
# 删除关键词响应器, 优先级11, 条件: 命令头
on_regex(r"^删除关键词\s*(\S+.*?)\s*删\s*(\S+.*?)\s*$", flags=re.S, priority=10, permission=SUPERUSER, handlers=[key_word_module.del_akeyword_handle])
# 删除关键词的一个回复响应器, 优先级10, 条件: 正则表达式
on_regex(r"^删除关键词\s*(\S+.*?)\s*删\s*(\S+.*?)\s*$", flags=re.S, priority=10, permission=SUPERUSER, handlers=[key_word_module.del_akeyword_handle])
# 普通回复响应器, 优先级999, 条件: 艾特bot就触发
on_message(rule=to_me(), priority=999, block=False, handlers=[key_word_module.regular_reply])
# 查看关键词响应器
on_command("查看关键词", aliases={"查询关键词"}, priority=11, block=True, permission=SUPERUSER, handlers=[key_word_module.check_keyword_handle])
# 使用openai的响应器
on_command("openai",aliases={"求助"},block=True, priority=55, handlers=[openai.openai_handle])
on_command("重置openai", aliases={"重置会话", "openai重置", "会话重置"}, priority=10, block=True, handlers=[openai.reserve_openai])
```
