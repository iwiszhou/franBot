import os
import requests

class HKBU_ChatGPT():
    def __init__(self,config_='./config.ini'):
        if type(config_) == str:
            self.config = "config"
        elif type(config_) != str:
            self.config = "config"

    def submit(self,message):   
        conversation = [{"role": "user", "content": message}]
        url = (os.environ['CHATGPT_BASICURL']) + "/deployments/" + (os.environ['CHATGPT_MODELNAME']) + "/chat/completions/?api-version=" + (os.environ['CHATGPT_APIVERSION'])
        headers = { 'Content-Type': 'application/json', 'api-key': (os.environ['CHATGPT_ACCESS_TOKEN']) }
        payload = { 'messages': conversation }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response