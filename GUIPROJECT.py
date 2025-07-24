import tkinter as tope
from tkinter import messagebox
class GUIPROJECT:
    def __init__(self):

       self.Page1= tope.Tk()
       self.Page1.geometry("250x450")
       self. Page1.title("GUI PROJECT")
       self.menu = tope.Menu(self.Page1)
       self.menubar = tope.Menu(self.menu,tearoff=0)
       self.menubar.add_command(label="close",command=exit)
       self.menubar.add_separator()
       self.menubar.add_command(label="close with comand ",command=self.show)
       self.menu.add_cascade(menu=self.menubar, label= "file")
       self.Page1.config(menu=self.menu)
       self.newmenu = tope.Menu(self.menu, tearoff=0)
       self.newmenu.add_command(label="show message ", command=self.MessageShowed)
       self.menu.add_cascade(menu=self.newmenu,label="Action ")

      
       self.Page1_Label1 = tope.Label(self.Page1, text=" To Do List", font=(50))
       self.Page1_Label1.pack(padx=10,pady=10)
       self.Textbox1= tope.Text(self.Page1, height=3, font=(12))
       self.Textbox1.bind("<KeyPress>",self.shortcut)
       self.Textbox1.pack(padx=10,pady=10)
       self.check = tope.IntVar()
       self.checkbox1 = tope.Checkbutton(self.Page1, text="Show message", variable=self.check,)
       self.checkbox1.pack(padx=30,pady=30)
       self.button1 = tope.Button(self.Page1,text="show message", command=self.MessageShowed, )  
       self.button1.pack(padx=20, pady=20)
       self.Page1.protocol("WM_DELETE_WINDOW", self.show)
       self.button2 = tope.Button(self.Page1, text="clear", font=(15), command= self.clearwords)
       self.button2.pack(padx=50, pady=50)
       self.Page1.mainloop()
    def MessageShowed(self):
        if self.check.get() == 0:
          print(self.Textbox1.get('1.0', tope.END))
        else:
           messagebox.showinfo(title="click the box", message=self.Textbox1.get("1.0", tope.END))
   
    def shortcut(self, event):
       if event.state == 4 and event.keysym == "Return":
          print("tried")
          self.MessageShowed()
    
    def show(self):
       if messagebox.askyesno(title="Quit?", message="Are you sure you want to quit"):
        self.Page1.destroy()
    
    def clearwords(self):
       self.Textbox1.delete("1.0", tope.END)

       
    #def shortcut(self, event):
      #print(event.state)
      #print(event.keysym)

       
       
        
GUIPROJECT() 