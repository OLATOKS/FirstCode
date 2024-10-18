MagicBall = ['go read', 
             'rest',
             'sleep',
             'your project',
             'Assignment',
             'chapel',
             'design']
print("pick a number from 0-7")
number = int(input())
while number != "":
    print(MagicBall[number])
    number = int(input())
