from dotenv import load_dotenv
import os
import requests
import re
import pprint
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate



def Weather(CityName):
    
    load_dotenv()
    TheWeatherApi = os.getenv("WeatherApi")
    
    if not TheWeatherApi:
        return "Weather Api not found go check the envfile"

    Url = f"https://api.openweathermap.org/data/2.5/weather?q={CityName}&appid={TheWeatherApi}&units=metric"
   
    try:
        Response = requests.get(Url)
        Data = Response.json()
        if Response.status_code == 200:
            value = {
                "Name of city":Data["name"],
                "Description":Data["weather"][0]["description"],
                "Temperature":Data["main"]["temp"],
                "Max Temperature":Data["main"]["temp_max"],
                "Min Temperature":Data["main"]["temp_min"],
                "Humidity":Data["main"]["humidity"],
                "Wind Speed":Data["wind"]["speed"]
                }
            return pprint.pprint(value)
        else:
            return f"Error:{Response.status_code} - {Data.get('message', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    
    
def ForeCast(CityName, days=None):
    load_dotenv()
    TheApi = os.getenv("WeatherApi")

    Url = f"https://api.openweathermap.org/data/2.5/forecast?q={CityName}&appid={TheApi}&units=metric"

    try:
        Response = requests.get(Url)
        Data = Response.json()
        if Response.status_code == 200:
            daily_data = {}
            
            for item in Data['list']:
                forecast_time = datetime.fromtimestamp(item['dt'])
                date = forecast_time.strftime("%Y-%m-%d")
                day_name = forecast_time.strftime("%A")
                
                if date not in daily_data:
                    daily_data[date] = {
                        'date': date,
                        'day_name': day_name,
                        'city': Data['city']['name'],
                        'temperatures': [],
                        'descriptions': [],
                        'humidities': [],
                        'wind_speeds': []
                    }
                
                
                daily_data[date]['temperatures'].append(item['main']['temp'])
                daily_data[date]['descriptions'].append(item['weather'][0]['description'])
                daily_data[date]['humidities'].append(item['main']['humidity'])
                daily_data[date]['wind_speeds'].append(item['wind']['speed'])
            
          
            daily_summaries = []
            for date, data in list(daily_data.items()) [:days]:  
                
                most_common_desc = max(set(data['descriptions']), key=data['descriptions'].count)
                
                daily_summaries.append({
                    'date': data['date'],
                    'day': data['day_name'],
                    'city': data['city'],
                    'weather': most_common_desc,
                    'min_temp': min(data['temperatures']),
                    'max_temp': max(data['temperatures']),
                    'avg_temp': round(sum(data['temperatures']) / len(data['temperatures']), 1),
                    'avg_humidity': f"{round(sum(data['humidities']) / len(data['humidities']))}%",
                    'avg_wind_speed': f"{round(sum(data['wind_speeds']) / len(data['wind_speeds']), 1)} m/s"
                })
            
            return pprint.pprint(daily_summaries)
        else:
            return f"Error: {Response.status_code} - {Data.get('message', 'Unknown error')}"
            
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
        

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
    template=""" You are a weather report assistant. Help with weather forecasting.
    
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
   
def WeathherBot():
    chain = TheChatBot()
    print("🌤️ The weather assistant is Active!")
    print("I can help with weather forecasts and other questions")
    print("Type 'exit' when you are done\n")

    while True:
        user_input = input("user: ").strip()

        if user_input.lower() == "exit":
            print("👋 Thank you and Goodbye!")
            break 

        
        if re.search(r"\b(weather|today's weather|temperature|forecast)\b", user_input.lower()):
            city_match = re.search(r'in (\w+)', user_input.lower())
            city = city_match.group(1) if city_match else input("What city? ").strip()
            
          
            if re.search(r'\b(forecast|week|days|ahead)\b', user_input.lower()):
                days_match = re.search(r'(\d+) days?', user_input.lower())
                days = int(days_match.group(1)) if days_match else 5
                result = ForeCast(city, days)
            else:
                result = Weather(city)
            
            print(f"🌤️ {result}")
            continue  
        
        
        response = chain.run(user_input)
        print(f"🤖 {response}\n")
        
        
if __name__ == "__main__":
    WeathherBot()
