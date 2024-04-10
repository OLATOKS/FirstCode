import re 
class Project:
    def __init__(self,Name):
        self.Name = Name
        self.TasksLists = []
    def WhatAreTheTasks(self,Tasks):
        return Tasks

    def AddMoreTask(self,Tasks):
        self.TasksLists.append(Tasks)
        self.TasksLists = Tasks.split(", ")
        
    def RemoveTask(self,Tasks):
        self.TasksLists.remove(Tasks)
print("enter the name of the new obeject")
ProjectName = str(input())  
ProjectName = Project("Tokunboh")
ProjectName.AddMoreTask("go and eat , go and sleep , cleaning ")
print(ProjectName.Name,"your projects are",ProjectName.WhatAreTheTasks(ProjectName.TasksLists))