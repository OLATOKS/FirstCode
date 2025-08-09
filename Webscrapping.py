from selenium import webdriver #this line imports the webdriver module from selenium, which lets me control a real browser, allows for loading pages and clicking buttons. 
from selenium.webdriver.common.by import By #the By class is used to specify how i want to find an element on the web page, basically locating classnames etc.
from selenium.webdriver.chrome.service import Service #the service class helps to set up and manage the chromedriver service that selenium uses to control the chrome browser.
from selenium.webdriver.support.ui import WebDriverWait # this tells selenium to wait for a button in this case
from selenium.webdriver.support import expected_conditions as EC # this is a condition for, which is for the element to be clickable 
import time

driver = webdriver.Chrome()
driver.get("https://www.premierleague.com/tables")
def ClubName():
    try:
        AcceptButton= WebDriverWait(driver, 12).until( #this line is to tell selenium to wait 12 seconds until a button is clickable.
        EC.element_to_be_clickable((By.CLASS_NAME,"Btn-primary"))# EC is an alais for Selenium.Webdriver.support.expected_conditions, which is meant the first button 
        ) 
        AcceptButton.click() #if the button appears clcik it automatically 
    except:
        print("No cookie popup or it already disappeared.")

    try:
        FindTeam = WebDriverWait(driver, 15).until( # This line is for the driver to wait for 15 secs 
            EC.presence_of_all_elements_located((By.CLASS_NAME,"standings-row__team-name-short")) # waits for elements with the class name 
            )
        print("There are",len(FindTeam),"teams") # this line lets me know the number of teams 
        
        TeamList=[]
        Known= set() # make sure are not two teams in the list 
        for team in FindTeam: # print the teams name 
            name = team.get_attribute("textContent").strip() #extracts the visible text from the web element, cleans it and saves it into the variable name
            if name and name not in Known:# avoid printing empty names.
                TeamList.append(name)
                Known.add(name)
         
        print("The teams are:")
        for name in TeamList:
            print("-", name)    
       
    except Exception as e:
        print("Error:", e)# this is to print the exact error 
        print("Check your internet connection ")
    driver.quit()
    print("done")

PlTeamNames = ClubName()
print(PlTeamNames)
