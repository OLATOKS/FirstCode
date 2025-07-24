import re


def PasswordDetect(TestPassword):
    PasswordCheck = re.compile(r'^(?=.*[a-z])and(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$')
    Check = PasswordCheck.search(TestPassword)
    
    while not Check:
        TestPassword = input("incorrect password,Does not match guildlines, input your password again \n")
        PasswordCheck = re.compile(r'^(?=.*[a-z])and(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$')
        Check = PasswordCheck.search(TestPassword)
    if Check:
            print("password saved")


ThePassword = input("input your password \n")
PasswordDetect(ThePassword)

