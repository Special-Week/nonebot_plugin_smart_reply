# nonebot2智能(障)回复插件


安装方式:

    nb plugin install nonebot-plugin-smart-reply
    
    pip install nonebot-plugin-smart-reply
    
    Download Zip
    

艾特bot时回复一些基于词库, 或青云客api或者小爱同学(好像这个api寄了)拿到的消息(优先词库, 这个词库有点色情)

api切换的命令为:

    智障回复api切换 | ai切换 | api_switch | 智能回复api切换
    ps.默认用的青云客api

对戳一戳也有反应(50%概率回复莲宝的藏话, 剩下50%概率回复poke__reply的内容, 需要配置好ffmpeg, 没配置好应该会随机回复poke__reply的内容)

智障回复的优先级是99, 并且block = False, 也就是说基本上不用担心这个智障回复阻断其他消息

但由于优先级较低(数字越大越低), 可能被其他插件阻断

建议看看源码改改utils部分的NICKNAME和MASTER
