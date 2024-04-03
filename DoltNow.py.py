import random
print("Good day welcome to pyprojects")
print("what is your name?")
name = input()
print("welcome", name )
password = 'olajidetokunboh'
print("Do you have an account, if not sign up ")
Accountanswer = input()
if Accountanswer == 'yes':
    print("welcome and please input your password below")
    passwordinput = input()
    if passwordinput != password:
        while passwordinput!= password:
            print("try again")
            passwordinput = input()
    if passwordinput == password:
        print("ok")
if Accountanswer == 'no':
    print("we will need you to sign in, input your email and password")
    email = input()
    first_sign_in_password = input()
    print("please input your password below")
    passwordinput = input()
    if passwordinput != first_sign_in_password:
        while passwordinput != first_sign_in_password:
            print("try again")
            passwordinput = input()
print("welcome, Mr", name)
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
print("when done with project type in next!, if not type in no")
nxtproject = input()
if nxtproject == 'no':
    print("complete the given project before moving onto the next")
    while nxtproject == 'no':
        print("are you done with the given project, yes or no \n if done type in next,\nif not type in no")
        nxtproject = input()
    if nxtproject == 'next':
        pyprojects.remove(randomprojects)
print(pyprojects)
