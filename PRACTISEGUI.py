import tkinter as tk 
page1 = tk.Tk()
page1.title("Calculator")
page1.geometry("500x500")
Text1 = tk.Entry(page1,font=(40), borderwidth= 3,justify="right")
Text1.pack(fill="x", padx="10", pady="15")
buttonframe = tk.Frame(page1)
buttonframe.columnconfigure(0, weight=1)
buttonframe.columnconfigure(1, weight=1)
buttonframe.columnconfigure(2, weight=1)
buttonframe.columnconfigure(3, weight=1)
ButtonCheck = tk.BooleanVar()
def Number(number):
    currentNumber = Text1.get()
    Text1.delete(0, tk.END)
    Text1.insert(0,str(currentNumber) + str(number))
    
def clear():
    Text1.delete(0,tk.END)

def Add():
    first_number = Text1.get()
    global NO1 
    global math
    math = "Addition"
    NO1 = float(first_number)
    Text1.delete(0,tk.END)
def equal():
    if math == "Addition":
        second_number = Text1.get()
        Text1.delete(0,tk.END)
        Text1.insert(0,NO1 + float(second_number))
    
    if math == "substraction":
        second_number = Text1.get()
        Text1.delete(0,tk.END)
        Text1.insert(0, NO1 - float(second_number))
    
    if math == "multiplication":
        second_number = Text1.get()
        Text1.delete(0,tk.END)
        Text1.insert(0,NO1 * float(second_number))
    
    if math == "division":
        second_number = Text1.get()
        Text1.delete(0,tk.END)
        Text1.insert(0,NO1 / float(second_number))
    
def substract():
    first_number = Text1.get()
    global NO1 
    global math
    math = "substraction"
    NO1 = float(first_number)
    Text1.delete(0,tk.END)

def multiplication():
    first_number = Text1.get()
    global NO1 
    global math
    math = "multiplication"
    NO1 = float(first_number)
    Text1.delete(0,tk.END)

def division():
    first_number = Text1.get()
    global NO1 
    global math
    math = "division"
    NO1 = float(first_number)
    Text1.delete(0,tk.END)

def power():
    first_number = Text1.get()
    global NO1 
    NO1 = float(first_number)
    Text1.delete(0, tk.END)
    Text1.insert(0, NO1*NO1)

       
Button1 = tk.Button(buttonframe, text="1",font=(20),command=lambda:Number(1), )
Button1.grid(row=1,column=0,sticky="ew", )
Button2 = tk.Button(buttonframe, text="2",font=(20),command=lambda:Number(2))
Button2.grid(row=1,column=1,sticky="ew")
Button3 = tk.Button(buttonframe, text="3",font=(20),command=lambda:Number(3))
Button3.grid(row=1,column=2,sticky="ew")
Button4 = tk.Button(buttonframe, text="4",font=(20),command=lambda:Number(4))
Button4.grid(row=2,column=0,sticky="ew")
Button5 = tk.Button(buttonframe, text="5",font=(20),command=lambda:Number(5))
Button5.grid(row=2,column=1,sticky="ew")
Button6 = tk.Button(buttonframe, text="6",font=(20),command=lambda:Number(6))
Button6.grid(row=2,column=2,sticky="ew")
Button7 = tk.Button(buttonframe, text="7",font=(20),command=lambda:Number(7))
Button7.grid(row=3,column=0,sticky="ew")
Button8 = tk.Button(buttonframe, text="8",font=(20),command=lambda:Number(8))
Button8.grid(row=3,column=1,sticky="ew")
Button9 = tk.Button(buttonframe, text="9",font=(20),command=lambda:Number(9))
Button9.grid(row=3,column=2,sticky="ew")
Button0 = tk.Button(buttonframe, text="0",font=(20),command=lambda:Number(0))
Button0.grid(row=4,sticky="ew",column=1)
AddButton = tk.Button(buttonframe,text="+",font=(20),command=Add)
AddButton.grid(row=4, column=0, sticky="ew")
MinusButton = tk.Button(buttonframe, text="-", font=(20),command= substract)
MinusButton.grid(row=4, column=2, sticky="ew")
EqualButton = tk.Button(buttonframe, text="=", font=(20),command=equal)
EqualButton.grid(row=5, columnspan=3, sticky="ew")
DivieButton = tk.Button(buttonframe, text="/", font=(20),command=division)
DivieButton.grid(row=1, column=3, sticky="ew")
MultiplicationButton = tk.Button(buttonframe, text="x", font=(20),command=multiplication)
MultiplicationButton.grid(row=2,column=3, sticky="ew")
PointButton = tk.Button(buttonframe, text=".", font=(20),command=lambda:Number("."))
PointButton.grid(row=3, column=3, sticky="ew")
PowerButton = tk.Button(buttonframe, text="^2", font=(20),command=power)
PowerButton.grid(row=4, column= 3, sticky="ew")
ClearButton = tk.Button(buttonframe, text="CLEAR", font=(20),command=clear)
ClearButton.grid(row=5,column=3,sticky="ew")
child =  buttonframe.winfo_children()
buttonframe.pack(fill="x")
page1.mainloop()