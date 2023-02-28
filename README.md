# 使用python3
```此项目为飞书机器人后端代码
目前仅支持与chatGPT私聊(p2p)事件，暂不支持群里@机器人
代码写的比较粗糙，大家将就者用 ^_^
```

## 准备工作
1. 修改：feishu_robot/components/http/handler.py 里的
    APP_ID = ""
    APP_SECRET = ""
    APP_VERIFICATION_TOKEN = ""
    
2. 修改：feishu_robot/components/ai/chat.py 里的
  token = "sk-xxxxxxxxx"
  
3. 视情况修改 feishu_robot/main.py 中的启动端口
  默认 port = 8008

4. 安装 requests 模块
pip3 install requests 

5. 安装 logging 模块
pip3 install logging


## 启动
`nouhp python3 main.py > /tmp/chat.log 2>&1 &`
