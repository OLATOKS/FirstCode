import os
from dotenv import load_dotenv
import requests


load_dotenv()

ChatKey = os.getenv("LLM_KEY")


url = "https://openrouter.ai/api/v1/chat/completions"

BankCode= {
    "gtbank": "*737*",
    "access": "*901*",
    "zenith": "*966*",
    "uba": "*919*",
    "firstbank": "*894*"
           }


def LLM(Question):
    headers ={
    "Authorization":f"Bearer {ChatKey}",
    "Content-Type": "application/json"
    }
    data = {
    "model": "openai/gpt-4o",
    "messages": [
        {
            "role":"user",
            "content": Question
        }
    ],  
    "max_tokens": 500
    }
    response = requests.post(url,headers=headers,json=data)
    if response.status_code == 200:
        print(response.json()["choices"][0]["message"]["content"])
    else:
        print("Error",response.status_code,response.text)

def Airtimepurchase(Bank,Amount,PhoneNumber=None):
    Bank = Bank.lower()
    if Bank not in BankCode:
        return "Sorry your bank is not in the avaible options"
    if PhoneNumber is None:
        return f"{BankCode[Bank]}{Amount}#"
    else:
        return f"{BankCode[Bank]}{Amount}*{PhoneNumber}#"
        
print("Welcome what would like to do")
Answer = input()

if any(keyword in Answer.lower() for keyword in ["question", "check", "what"]):
    Question = input()
    LLM(Question)
Pattern = r"\b(data|airtime|credit)\b"

if  re.search(Pattern.lower(),Answer, re.IGNORECASE):
    
    BankName = input("What bank are you using?:").strip().lower()
    PriceAmount = input("How much?:").strip()
    Choice = input("For self(Put 1) For others(put 2):")
    if Choice == "1":
        print(f"Copy and paste this {Airtimepurchase(BankName,PriceAmount)}")
    else:
        AirtimeDestination = input("Please type the phone Number of the receipt below").strip()
        print(f"Copy and paste this {Airtimepurchase(BankName,PriceAmount,AirtimeDestination)}")