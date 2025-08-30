import os
from dotenv import load_dotenv
import requests


load_dotenv()

ChatKey = os.getenv("LLM_KEY")


url = "https://openrouter.ai/api/v1/chat/completions"

headers ={
    "Authorization":f"Bearer {ChatKey}",
    "Content-Type": "application/json"
}
 
data = {
    "model": "openai/gpt-4o",
    "messages": [
        {
            "role":"user",
            "content":"what is the best programming language to use now "
        }
    ],  
    "max_tokens": 500
}

response = requests.post(url,headers=headers,json=data)

if response.status_code == 200:
    print(response.json()["choices"][0]["message"]["content"])
else:
    print("Error",response.status_code,response.text)