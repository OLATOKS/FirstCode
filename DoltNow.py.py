import random
print("what is your name?")
name = input()
print("welcome" ,  name)
print("please input the project you want to work on below", name)
pyprojects = []
newprojects = input()
pyprojects.append(newprojects)
print("do you want \to add another?, yes or no, answer below")
answer = input()
if answer == 'yes':
    while answer != 'no':
        newprojects = input()
        pyprojects.append(newprojects)
        print("do you want to add another?,yes or no, answer below")
        answer = input()
    if answer == 'no':
        print(" ok thank you, Mr" , name)
print("do you wish do to see your projects?")
answer2 = input()
if answer2 == 'yes':
    print(pyprojects)
print("are you ready to work, yes or no ? answer below")
workans = input()
if workans == 'yes':
    print("you will be given a random project to start with below!")
randomprojects = random.choice(pyprojects)
print("you are too work on", randomprojects,"now")   

print(pyprojects)
