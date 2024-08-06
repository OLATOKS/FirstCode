class Project :
    def __init__(self,Name,Tasks):
        self.Name = Name
        self.Tasks = list(Tasks.split(", "))

    def DisplayTasks(self):
        print(self.Tasks)
    
    def AddMoreTasks(self,NewTasks):
        self.Tasks.append(NewTasks

    def RemoveTasks(self,NewTasks):
        self.Tasks.remove(NewTasks)

Tk = Project("olajide olatokunboh", "cooking, coding, playing fifa")
print(Tk.Name)
Tk.DisplayTasks()
print("Want To Add New Tasks")
AdditionalTasks = input().split(", ")
TheTasks = " "
for char in AdditionalTasks:
    if char != ",":
        TheTasks = char
        Tk.AddMoreTasks(TheTasks)
Tk.DisplayTasks()
print(" Add a new project name ")
NewNameOfTask = input()
print("add a name for the task category")
NameOfTasklist = input()
print("name of the object you want to instiate?")
NewObject = input("")
NewObject = Project(NewNameOfTask,NameOfTasklist)
if isinstance(NewObject, Project):
    print(True)
else:
    print(False)
print(NewObject.Name)
NewObject.DisplayTasks()

