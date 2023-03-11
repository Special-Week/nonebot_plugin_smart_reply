# nonebot2智能(障)回复插件

    问问提前请务必看完readme


## 功能

    艾特bot时回复一些基于词库, 或青云客api拿到的消息(优先词库, 这个词库有点色情)
    艾特bot时并且加上"求助", "请问"的命令头时, bot回复一些调用openai的ai回复(这个ai真的逆天), 具体效果请见下文
    接入了new bing的接口, 详情见下文

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
| xiaoai_apikey  | string         |寄         |xiaoai_apikey = "abc1145141919810"       |    小爱同学的apiKey, 详细请看下文        |
| Bot_NICKNAME   | string         |脑积水     |Bot_NICKNAME = "Hinata"                  |      你Bot的称呼                         |
| Bot_MASTER     | string         |脑积水     |Bot_MASTER = "星野日向_Official"          |      你Bot主人的称呼                     |
| ai_reply_private  | boolean |false     |ai_reply_private = true          |    私聊时是否启用AI聊天（不影响功能性指令）            |
| openai_api_key    | string  |寄        |openai_api_key = "aabb114514"    |    openai的api_key, 详细请看下文         |
| openai_max_tokens | int     |1000      |openai_max_tokens = 1500         |    openai的max_tokens, 详细请看下文     |
| openai_cd_time    | int     |60        |openai_cd_time = 114             |    openai调用的cd                       |

.env完全不配置不影响插件运行, 但是部分功能会无法使用



对戳一戳也有反应. 33%概率回复莲宝的藏话(发送语音需要配置好ffmpeg), 33%的概率回复poke__reply的内容, 剩下的概率戳回去, 如果想改概率的话, 找到@poke_.handle()下的函数, 根据注释改概率, 莲包的藏话放在了插件目录下的resource/audio, 想加可以任意

智障回复的优先级是99, 并且block = False, 也就是说基本上不用担心这个智障回复阻断其他消息

但由于优先级较低(数字越大越低), 可能被其他插件阻断, 如果没反应请查看控制台判断被哪个插件的on_message阻断了, 然后自行拉高或者降低相关响应器的优先级


​       
## 关于openai:

    0. 如果你出现了<module 'openai' has no attribute 'Completion'>的报错, 大概是和numpy相关, 解决方法是卸载numpy和openai然后再单独安装openai(numpy会被当作依赖再次下回来, 所以不需要再次下载numpy)
    1. openai_api_key请注册openai后在 https://beta.openai.com/account/api-keys 自己获取
    2. openai_max_tokens貌似是ai返回的文本最大多少(根据我自己用的经验)
    3. openai_api_key必须配置, openai_max_tokens随意, 有默认值
    4. bot通过openai模块最近貌似需要科学上网
    5. 目前env只提供了api_key和max_tokens的设置, 其他参数你可以自己动源码
    6. 据我个人使用的情况, 总是有群友提问一些引诱犯罪的问题, 如果你遇到这种情况, 你可以考虑自己处理prompt字符串做一些判断
    7. 这个模块貌似不是免费的, 注册的账号只有$18.00的免费额度, 我个人调用了大约1500回, 目前的额度 $7.05 / $18.00
    8. 一些具体的实例:
    
        Q: @bot求助 使用golang定义一个全局变量client, 并让其在init函数内与redis相连接
        A: @USER  
            package main
            import (
                "github.com/go-redis/redis"
            )
            var client *redis.Client
            func init() {
                client = redis.NewClient(&redis.Options{
                    Addr:     "localhost:6379",
                    Password: "", // no password set
                    DB:       0,  // use default DB
                })
            }
    
        Q: @bot求助 假如你是李华，今日中国三大运营商——中国联通，中国移动，中国电信，屏蔽了中国境内对 GitHub 的访问，请你使用英语向你的外国笔友
           Jane写一封信，简要讨论这件事。正文内容要点：（1）对GitHub被封感到震惊、（2）谈论此事对中国开源界的影响、（3）对中国开源界的未来进行探讨。
           要求：（1）正文要点必须全部包含、（2）词数不少于100词、（3）文中不得出现真实的姓名
        A: @USER 
            Dear Jane,
            I am writing to tell you about a shocking news that three major Chinese operators, China Unicom, 
            China Mobile and China Telecom, have blocked access to GitHub in China.
    
            This news has caused great concern among Chinese open source communities. On the one hand, the 
            number of people who use GitHub to store and share their codes has decreased dramatically. On the
            other hand, the development of open source technology in China is facing a great challenge.
    
            I'm really worried about the future of open source in China. The government should take measures
            to guarantee the development of open source projects and encourage more people to join in. Moreover,
            the operators should also consider the interests of users and provide better services.
    
            I hope the situation can be improved soon.
    
            Yours,
            Li Hua
    
    	Q: @bot求助 群聊的同性朋友总幻想和我发生性关系怎么办
        A: @USER 首先，你需要有耐心，坦诚地和朋友进行沟通，明确你的立场。如果朋友不能理解你的想法，你可以尝试改变聊天的话题，
            让谈话变得更加积极有趣。如果朋友仍然追求你，你可以向他/她明确表达你的立场，如果朋友仍然不能接受，你可以考虑暂时结束聊天，
            或者把他/她从群聊中移除。





## 关于new bing的配置:

    0. 你也许需要科学上网
    1. 使用new bing必须配置cookie, 这个cookie内容过多不适合在.env, 所以这个cookie将会与json文件的形式进行配置
    2. 首先你需要一个通过申请的账号, 使用edge浏览器安装"editthiscookie"浏览器插件或者相关其他获取cookie的插件. 然后进入"bing.com/chat"登录通过的账号
    3. 右键界面选择"editthiscookie", 找到一个看上去像出门的样子的图标"导出cookie", cookie一般就能在你的剪贴板
    4. 打开你bot项目文件夹, 依次进入data/smart_reply, 没有就新建, 在bot/data/smart_reply目录下新建文件"cookie.json", 打开把你的cookie内容复制进去
    5. 当cookie失效后, cookie.json文件更新后, 发送update_bing | cookie_bing即可热更新


    用法:
        1. bing + 内容, 和bing发起会话, 如果没有会新建会话.
        2. 重置会话, 重置bing的会话
        3. su_help + 内容, 通过bot转发消息给superusers
        4. 所有会话会被记录在data/smart_reply/req_data.db这个sqlite3数据库内, superuser可以根据这个ban人, 预防有人故意找bing进行诱导犯罪的会话
        5. new bing遇到不合理的问题不会直接给出回复, 所以我根据这个设计了一个用户违规数记录, 大于阈值(5, 在utlis.py内, 变量名为THRESHOLD)会被禁用该功能, 留了一个su_help响应器可以让被ban的用户把解封的请求转发给superuser, superuser可以根据数据库的内容来执行判断该不该解禁, 违规的记录将保存在data/smart_reply/user_info.json
        6. 解禁的指令 释放违规 | 解禁bing xxx, 后跟qq账号
        7. 防止又弔人用su_help功能烦superuser, 增加了一个响应器"添加黑名单", 后跟参数qq号, 使用后该用户的消息事件与通知事件均无视, 包括其他插件的响应器
        8. 相对应的, 当然准备了"删除黑名单" 这个响应器用来接触, 黑名单数据存储在插件目录下的resource/json/blacklist.json下, 请注意与上面讲的用户违规记录是不一样的
        
    项目使用了与Bing通讯的接口 [EdgeGPT](https://github.com/acheong08/EdgeGPT)        


## 会有人需要教命令行如何科学上网吗?:

    1. 利用v2rayN等工具开启本地监听端口(一般高位端口任意设置, 下面用port代替你说设置的)
    2. 环境变量增加all_proxy变量, 协议是socks那值就是socks5://127.0.0.1:port, 是http那么值就是http://127.0.0.1:port


