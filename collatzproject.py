def collatz(number):
    if number % 2 == 0:
       return  (  number // 2)
    
    else:
       return (3 * number + 1)
print("type in a number ")
Number = int(input())
while Number != 1:
   Number = collatz(Number)
   print(Number)
