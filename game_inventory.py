import pprint
inventory = {"keys":10, "rope":2,"health potion": 30, "mp potion":50, "teleport spells":11,
             "fire spells":30,"maze unique":1,"magic wand(unique)":2,"sword(legendary)":1}

NewItems = ["keys","keys","rope","maze unique","magic wand(unique)","sword(legendary)","teleport spells","sword(legendary)"]


def Output(TheDic: dict):
    print("things in the inventory are :")
    for i, j in TheDic.items():
        print(j , i)
        Adding = 0 
    for i in inventory.values():
        Adding += i
    print("Total items is : " , Adding)


def addingNewItems(Inventory: dict, AddingItems):
    for k, j in Inventory.items():
        for t in AddingItems:
            if k == t:
                j += 1
                Inventory[k]=j
                
    for k in AddingItems:
        item_exists = Inventory.get(k, False)
        if  item_exists == False:
            Inventory[k] = 1

    return Inventory

Output(inventory)
inventory = addingNewItems(inventory,NewItems)
Output(inventory)       

