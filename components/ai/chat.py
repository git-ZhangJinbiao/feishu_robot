import json
import requests
import logging

logging.basicConfig(level=logging.INFO)


class GptChat:
    url = "https://api.openai.com/v1/completions"
    token = "sk-"

    def get_open_ai_reply(self, content):
        prompt = content.strip()

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token
        }
        req_body = {
            "model": "text-davinci-003",
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "top_p": 1,
            "stop": ["#"]
        }
        answer = ''
        try:
            response = requests.request("POST", self.url, headers=headers, data=json.dumps(req_body))
            json_response = response.json()
            choices = json_response.get('choices')
            for i in range(len(choices)):
                answer = answer + choices[i].get('text')
            logging.info(answer.strip().replace('\n\n', ''))
        except Exception as e:
            logging.error(e)
            return "ERROR：未知错误"

        return answer


if __name__ == '__main__':
    xxx = GptChat()
    xxx.get_open_ai_reply('你好，请介绍一下自己')
