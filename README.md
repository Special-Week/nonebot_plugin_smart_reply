# nonebot2智能(障)回复插件

    问问提前请务必看完readme, 这是一个融合了openai, newbing, 词库的智障回复插件
    
### 提醒, new bing与openai国内服务器需要科学上网才可调用, 希望你能熟练使用v2ray或clash或其他代理软件



## 功能

    艾特bot时回复一些基于词库的消息, 戳一戳回复特定的消息或者语音以及反戳
    接入了new bing的接口, 详情见下文
    接入了openai的接口, 详情见下文
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
| newbing_cd_time    | int     |600        |newbing_cd_time = 114             |    newbing创建会话的cd                       |
|bing_or_openai_proxy|str       |""         |bing_or_openai_proxy = "http://127.0.0.1:1081" |    openai或者newbing的代理, 配置详细请看下文|        
|newbing_style    |str             |creative   |newbing_style = "creative"             |newbing的风格, "creative", "balanced", "precise", 三选一, 乱填报错我不管|

.env完全不配置不影响插件运行, 但是部分功能会无法使用(openai, newbing)
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




## 关于new bing的配置:

    0. 也许需要科学上网, 代理配置详细请看下文
    1. 使用功能必须配置cookie, 否则无法使用, 这个cookie内容过多不适合在.env, 所以这个cookie将会与json文件的形式进行配置
    2. 首先你需要一个通过申请的账号, 使用edge浏览器安装"editthiscookie"浏览器插件, 或者使用相关的其他插件获取cookie. 进入"bing.com/chat"登录通过的账号
    3. 先随便交互点内容(不交互可能会出现User needs to solve CAPTCHA to continue)再右键界面选择"editthiscookie", 找到一个看上去像出门的样子的图标"导出cookie", cookie一般就能在你的剪贴板, 注意了, cookie导出来是一个list, 大概长这样[{},{},{}]
    4. 新建cookiexxx.json文件(xxx为任意合法字符), 把你剪贴板的cookie的字符串粘贴进去, 再次强调json大概长[{},{},{}]这样
    5. 打开你bot项目文件夹, 依次进入data/smart_reply, 没有就新建, 把json文件丢进去, 有几个账号可以放几个, 要求cookie开头, .json结尾, 载入插件时初始化会全部读取, 创建会话的时候会通过random来选择一个账号的cookie
    6. 注意观察加载插件的时候, log会提示你加载了几个cookie
    7. 调用时报错请检查cookie是否有效, 是否做到了科学上网

    用法:
        1. bing + 内容, 和bing发起会话, 如果没有会新建会话.
        2. 重置bing, 重置bing的会话

    使用了与Bing通讯的接口 [EdgeGPT](https://github.com/acheong08/EdgeGPT)        
    tips: 根据这条[issue](https://github.com/acheong08/EdgeGPT/issues/584)，中国大陆服务器你也许edgeGPT 0.10.16才能使用


## bing_or_openai_proxy的配置:

    1. 你需要使用v2ray或者clash等代理工具开启本地监听端口
    2. 根据http和socks5的不同, 配置不同, 
    3. 以v2rayN举例, 本地监听端口1080, 你应该配置成"socks5://127.0.0.1:1080"或者"http://127.0.0.1:1081"
    4. 以clash for windows举例, 本地监听端口7890, 你应该配置成"socks5://127.0.0.1:7890"或者"http://127.0.0.1:7890"





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
# 使用bing的响应器
on_command("bing", priority=55, block=True, handlers=[newbing.bing_handle])
on_command("重置bing", aliases={"重置会话", "bing重置", "会话重置"}, priority=10, block=True, handlers=[newbing.reserve_bing])
# 使用openai的响应器
on_command("openai",aliases={"求助"},block=True, priority=55, handlers=[openai.openai_handle])
on_command("重置openai", aliases={"重置会话", "openai重置", "会话重置"}, priority=10, block=True, handlers=[openai.reserve_openai])
on_command("apikey_status", aliases={"apikey用量", "apikey状态"}, priority=10, block=True, handlers=[openai.apikey_status])
```
