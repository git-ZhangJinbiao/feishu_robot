import json
import logging
import uuid
import requests
from http.server import BaseHTTPRequestHandler
from components.ai.chat import GptChat


class RequestHandler(BaseHTTPRequestHandler):
    APP_ID = ""
    APP_SECRET = ""
    APP_VERIFICATION_TOKEN = ""
    messages_url = 'https://open.feishu.cn/open-apis/im/v1/messages'
    access_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"

    def do_POST(self):
        # 解析请求 body
        req_body = self.rfile.read(int(self.headers['content-length']))
        req_json = json.loads(req_body.decode("utf-8"))
        logging.info(req_json)

        # 校验 verification token 是否匹配，token 不匹配说明该回调并非来自开发平台
        token = req_json.get("header", "").get("token", "")
        if token != self.APP_VERIFICATION_TOKEN:
            print("verification token not match, token =", token)
            self.response("")
            return

        # 根据 type 处理不同类型事件
        request_type = req_json.get("type", "")
        event_type = req_json.get("header", "").get("event_type", "")
        if "url_verification" == request_type:  # 验证请求 URL 是否有效
            self.handle_request_url_verify(req_json)
        elif "im.message.receive_v1" == event_type:  # 处理事件回调
            # 获取事件内容和类型，并进行相应处理，此处只关注给机器人推送的消息事件
            event = req_json.get("event")
            self.handle_message(event)
        return

    def do_Get(self):
        self.do_POST()

    def handle_request_url_verify(self, post_obj):
        # 原样返回 challenge 字段内容
        challenge = post_obj.get("challenge", "")
        rsp = {'challenge': challenge}
        self.response(json.dumps(rsp))
        return

    def handle_message(self, event):
        # 此处只处理 text 类型消息，其他类型消息忽略
        msg_type = event.get("message").get("message_type", "")
        if msg_type != "text":
            print("unknown msg_type =", msg_type)
            self.response("")
            return

        # 调用发消息 API 之前，先要获取 API 调用凭证：tenant_access_token
        access_token = self.get_tenant_access_token()
        if access_token == "":
            self.response("")
            return

        chat_type = event.get("message").get("chat_type", "")
        if chat_type == "p2p":
            message = GptChat().get_open_ai_reply(f'你是 ChatGPT, 一个由 OpenAI 训练的大型语言模型, 你旨在回答并解决人们的任何问题，并且可以使用多种语言与人交流。\n请回答我下面的问题\nQ: {event.get("message", "").get("content", "")}\nA: ')
            if message == "":
                self.response("")
                return
            # 机器人 echo 收到的消息
            message_id = event.get("message", "").get("message_id","")

            self.reply(message_id,message,str(uuid.uuid5(uuid.NAMESPACE_URL,message_id)))
            self.response("")
            return
        elif chat_type == "group":
            pass
        else:
            pass

    def response(self, body):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body.encode())

    def get_tenant_access_token(self):

        headers = {
            "Content-Type": "application/json"
        }
        req_body = {
            "app_id": self.APP_ID,
            "app_secret": self.APP_SECRET
        }
        try:
            rsp_dict = requests.request("POST", self.access_url, headers=headers, data=json.dumps(req_body)).json()
        except Exception as e:
            logging.error(e)
            return ""

        code = rsp_dict.get("code", -1)
        if code != 0:
            logging.warning("get tenant_access_token error, code =", code)
            return ""
        return rsp_dict.get("tenant_access_token", "")

    def reply(self, message_id, msg, uuid):
        msgContent = {
            "text": msg,
        }
        req = {
            "msg_type": "text",
            "content": json.dumps(msgContent),
            "uuid": json.dumps(uuid)
        }
        payload = json.dumps(req)
        headers = {
            'Authorization': f'Bearer {self.get_tenant_access_token()}',  # your access token
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", f'{self.messages_url}/{message_id}/reply', headers=headers, data=payload)
        logging.info(response.json())
        return response.json()