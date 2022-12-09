# nonebot2智能(障)回复插件

## 功能

    艾特bot时回复一些基于词库, 或青云客api或者小爱同学拿到的消息(优先词库, 这个词库有点色情)
    艾特bot时并且加上"求助", "请问"的命令头时, bot回复一些调用openai的ai回复(这个ai真他娘的逆天), 具体效果请见下文

### 安装方式:

    nb plugin install nonebot-plugin-smart-reply
    
    pip install nonebot-plugin-smart-reply
    
    Download Zip
 
### env配置项:

|config          |type            |default    |example                                  |usage                                   |
|----------------|----------------|-----------|-----------------------------------------|----------------------------------------|
| xiaoai_apikey  | string         |寄         |xiaoai_apikey = "abc1145141919810"       |    小爱同学的apiKey, 详细请看下文        |
| Bot_NICKNAME   | string         |脑积水     |Bot_NICKNAME = "Hinata"                  |      你Bot的称呼                         |
| Bot_MASTER     | string         |脑积水     |Bot_MASTER = "星野日向_Official"          |      你Bot主人的称呼                     |
| openai_api_key    | string  |寄        |openai_api_key = "aabb114514"    |    openai的api_key, 详细请看下文         |
| openai_max_tokens | int     |1000      |openai_max_tokens = 1500         |    openai的max_tokens, 详细请看下文     |
| openai_cd_time    | int     |60        |openai_cd_time = 114             |    openai调用的cd                       |

.env完全不配置不影响插件运行, 但是部分功能会无法使用


### 小爱同学apiKey的申请步骤:

    1. 进入网页 https://apibug.cn/doc/xiaoai.html
    2. 右上角注册登录
    3. 左边接口列表
    4. 找到"小爱同学AI"零元购买
    5. 请求接口中 "&apiKey="后面的值就是你的apiKey, 填在.env内, 假设返回你的请求接口是 "https://apibug.cn/api/xiaoai/?msg=你是谁？&apiKey=abc1145141919810" 
       那么你应该在.env内填入:  xiaoai_apikey = "abc1145141919810"
       
api切换的命令为:

    智障回复api切换 | ai切换 | api_switch | 智能回复api切换
    ps.默认用的青云客api

对戳一戳也有反应(50%概率回复莲宝的藏话, 剩下50%概率回复poke__reply的内容, 需要配置好ffmpeg, 没配置好应该会随机回复poke__reply的内容)

智障回复的优先级是99, 并且block = False, 也就是说基本上不用担心这个智障回复阻断其他消息

但由于优先级较低(数字越大越低), 可能被其他插件阻断


       
## 关于openai:

    1. openai_api_key请注册openai后在 https://beta.openai.com/account/api-keys 自己获取

    2. openai_max_tokens貌似是ai返回的文本最大多少(根据我自己用的经验)

    3. openai_api_key必须配置, openai_max_tokens随意, 有默认值

    4. bot通过openai模块调用应该不需要科学上网
    
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
            (这逼甚至手撕二叉树, 手撸STL容器, 已经吊打我这个废物了....)

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
            (真nm正宗, 薄纱我这个在四六级考试把中国皇帝写成Chinese boss的废物)
            
            
            
        Q: @bot求助 群聊的同性朋友总幻想和我发生性关系怎么办
        A: @USER 首先，你需要有耐心，坦诚地和朋友进行沟通，明确你的立场。如果朋友不能理解你的想法，你可以尝试改变聊天的话题，
           让谈话变得更加积极有趣。如果朋友仍然追求你，你可以向他/她明确表达你的立场，如果朋友仍然不能接受，你可以考虑暂时结束聊天，
           或者把他/她从群聊中移除。
