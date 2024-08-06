class Project :
    def __init__(self,Name,Tasks):
        self.Name = Name
        self.Tasks = list(Tasks.split(", "))

    def DisplayTasks(self):
        print(self.Tasks)
    
    def AddMoreTasks(self,NewTasks):
        self.Tasks.append(NewTasks)
        
<<<<<<< HEAD

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

=======
    def RemoveTask(self,Tasks):
        self.TasksLists.remove(Tasks)
print("enter the name of the new obeject")
ProjectName = str(input())  
ProjectName = Project("Tokunboh")
ProjectName.AddMoreTask("go and eat , go and sleep , cleaning ")
ProjectName.listTasks()
>>>>>>> 027305e62ac204b985d4b0a4254060e469c5c4a8
