import tkinter  as tk 
practise = tk.Tk()
practise.title("Lists")
practise.geometry("400x400")
Entry1 = tk.Entry(practise, font=(10), borderwidth=6, )
Entry1.pack(fill="x", padx="5", pady="5")
Textbox1 = tk.Text(practise,font=(10),borderwidth=6,height=12 )
Textbox1.pack(fill="x",padx="5", pady="5")
def DELETE():
    Textbox1.delete("1.0", tk.END)


frame1 = tk.Frame(practise)
frame1.columnconfigure(0, weight=1)
frame1.columnconfigure(1, weight=1)
button1 = tk.Button(frame1,text="Save", font="12",)
button1.grid(row=0,column=0,pady=2,sticky="ew")
button2 = tk.Button(frame1,text="clear", font="12",command=DELETE)
button2.grid(row=0,column=1,pady=2,sticky="ew")
frame1.pack(fill="x")
practise.mainloop()