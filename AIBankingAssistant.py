import re
import os 
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

BankUssdAirtimeCode= {
    "gtbank": "*737*",
    "access": "*901*",
    "zenith": "*966*",
    "uba": "*919*",
    "firstbank": "*894*"
           }

BankUssdTransfercode = {
    "gtbank": {"same_bank": "*737*1*", "other_bank": "*737*2*"},  
    "access": {"same_bank": "*901*1*", "other_bank": "*901*2*"},
    "zenith": {"same_bank": "*966*1*", "other_bank": "*966*2*"},
    "uba": {"same_bank": "*919*3*", "other_bank": "*919*4*"},
    "firstbank": {"same_bank": "*894*1*", "other_bank": "*894*2*"} 
}

def AirtimePurchase(Bank,Amount,PhoneNumber = None):
    Bank = Bank.lower()
    if Bank not in BankUssdAirtimeCode:
        return "Your bank is not included in the database"
    if PhoneNumber is None:
        return f"{BankUssdAirtimeCode[Bank]}{Amount}#"
    else:
        return f"{BankUssdAirtimeCode[Bank]}{Amount}*{PhoneNumber}#"
    
def AirtimeRequest(user_input):
    if not re.search(r"\b(airtime|credit|data|top up|recharge|topup)\b", user_input.lower()):
        return None 
    print("Airtime purchase detected")
    BankName = input("The name of the bank you are using?:").lower().strip()
    PriceAmount = input("How much?:").strip()
    choice = input("For self (Put 1) or For others (Put 2): ").strip()
    
    if choice == "1":
        UssdCode = AirtimePurchase(BankName,PriceAmount)
        return f"Copy and paste this: {UssdCode}"
    else:
        DestinationNumber = input("Thr phone you would like to send the airtime to: ").strip()
        UssdCode = AirtimePurchase(BankName,PriceAmount,DestinationNumber)
        return f"Copy and paste this: {UssdCode}"
    
def MoneyTransfer(Bank,AccountNumber,Amount,DestinationBank):
    Bank = Bank.lower()
    if Bank not in BankUssdTransfercode:
        return "Your bank is not in the database"
    
    if DestinationBank == "3":
        return f"{BankUssdTransfercode[Bank]["same_bank"]}{AccountNumber}*{Amount}#"
    elif DestinationBank == "4":
        return f"{BankUssdTransfercode[Bank]["other_bank"]}{AccountNumber}*{Amount}#"
    else:
        return "Invalid transfer type"


def TransferRequest(user_input):
    if not re.search(r"\b(transfer|send.money|wire|send.funds)\b", user_input.lower()):
        return None
    
    print("Money transfer detected!")
    TheBankName = input("Put your bank name?: ").lower().strip()
    
    TheBankChoice = input("For the same bank (put 3), for the other bank(put 4)?: ").strip()
    
    AccountNumberRequest = input("The Account Number you want to transfer to?: ").strip()
    
    CashAmount = input("How much?: ").strip()
    
    TheUssdCode = MoneyTransfer(TheBankName,AccountNumberRequest,CashAmount,TheBankChoice)
    return f"Copy and paste this:{TheUssdCode}"
    

def TheChatBot():
    load_dotenv()
    llm = ChatOpenAI(base_url= "https://openrouter.ai/api/v1",
                 openai_api_key = os.getenv("DeepSeekApi"), 
                 model="deepseek/deepseek-chat-v3.1:free",
                 temperature= 0.7,
                 )
    
    memory = ConversationBufferMemory()

    prompt = PromptTemplate(
    input_variables=["history","input"],
    template=""" You are a banking assistant. Help with banking services and questions.
    
    chat history:
    {history}

    Human: {input}
    AI:\n"""
    )
    return LLMChain(
        llm = llm, 
        prompt=prompt, 
        memory=memory, 
        verbose=False)
   
def BankingChatBot():
    chain = TheChatBot()
    print("The Banking assistant Active") #Like chivita hehehe 😂 Will still clear this 
    print("I can help with airtime purchase,Money transfers and Banking questions ")
    print("Type 'exit' when you are done")

    while True:
        user_input = input("what will you have me do?: ").strip()

        if user_input.lower() == "exit":
            print("Thank you and Good Bye")
            break
        
        AirtimeResponse = AirtimeRequest(user_input)
        if AirtimeResponse:
            print(AirtimeResponse)
            continue

        TransferResponse = TransferRequest(user_input)
        if TransferResponse:
            print(TransferResponse)
            continue
        Response = chain.run(user_input)
        print(f"{Response}\n")

if __name__ == "__main__":
    BankingChatBot()
    