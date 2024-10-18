import random,gc
class Project :
    def __init__(self,Name,Tasks):
        self.Name = Name
        self.Tasks = list(Tasks.split(", "))

    def DisplayTasks(self):
        print(self.Tasks)
    
    def AddMoreTasks(self,NewTasks):
        self.Tasks.append(NewTasks)
        
    def RemoveTasks(self,NewTasks):
        self.Tasks.remove(NewTasks)

obj_1 = Project("leisure", "cooking, coding, playing fifa")
obj_2 = Project("finace","saving, less spending, budgeting")
print(obj_1.Name)
obj_1.DisplayTasks()
print(obj_1.Tasks)
GetInstances = gc.get_objects()
Listsofinstances = [items for items in GetInstances if isinstance(items,Project)]
for index,items in enumerate(Listsofinstances):
    print(index,Listsofinstances[index].Name )
print("Want To Add New Tasks, choose the number you want add task to and right below add the task ") #turns a string into a number 
WhichTask = int(input())
AdditionalTasks = input().split(", ")
TheTasks = " "
for char in AdditionalTasks:
    if char != ",":
        TheTasks = char
        Listsofinstances[WhichTask].AddMoreTasks(TheTasks)
Listsofinstances[WhichTask].DisplayTasks()
print(" Add a new project name ")
NewNameOfTask = input()
print("add a name for the task category")
NameOfTasklist = input()
print("name of the object you want to instiate?")
NewObject = input("")
NewObject = Project(NewNameOfTask,NameOfTasklist)
Listsofinstances.append(NewObject)
if isinstance(NewObject, Project):
    print(True)
else:
    print(False)
print(NewObject.Name)
NewObject.DisplayTasks()
for index,items in enumerate(Listsofinstances):
    print(index,Listsofinstances[index].Name )
print("from the list shown above choose the task assign name you want to start!")
WhichTask = int(input())
def DecideTask():
    RandomChoice = random.choice(Listsofinstances[WhichTask].Tasks)
    print("do this task -->" + RandomChoice)
DecideTask()
print(Listsofinstances[0].Name,)
print(Listsofinstances[1].Name)
print(Listsofinstances[2].Name)
print(Listsofinstances[0].Tasks)
print(Listsofinstances[1].Tasks)
print(Listsofinstances[2].Tasks)