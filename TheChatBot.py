from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os 


load_dotenv()

llm = ChatOpenAI(base_url= "https://openrouter.ai/api/v1",
                 openai_api_key = os.getenv("DeepSeekApi"), 
                 model="deepseek/deepseek-chat-v3.1:free",
                 temperature= 0.7,
                 )

memory = ConversationBufferMemory()

prompt = PromptTemplate(
    input_variables=["history","input"],
    template=""" You are a helpful AI assistant.
    
    chat history:
    {history}

    Human: {input}
    AI:\n"""
)

chain = LLMChain( 
    llm = llm,
    prompt=prompt,
    memory=memory,
    verbose=False
) 

print("this is a simple Q&A chat bot")

while True:
    print("Type when you want to stop the chatbot")
    UserInput = input("How may i be of help??\n")
    if UserInput.lower() == "exit":
        print("Thank you and GoodBye")
        break
    
    Response = chain.run(UserInput)
    print(f"AI :\n{Response}")
