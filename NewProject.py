TableData = [['apples', 'oranges', 'cherries', 'banana'], 
             ['Alice', 'Bob', 'Carol', 'David'], 
             ['dogs', 'cats', 'moose', 'goose']]
            
def AdjustRight(anything : list): 
  ColumnWidth = [0] * len(anything)
  for t in range(len(anything)):
    for item in anything:
      ColumnWidth[t] = max(ColumnWidth[t], len(item[t]))
  for row  in zip(*anything):
    for j in range(len(row)):
      print(row[j].rjust(ColumnWidth[j]), end=" ")
    print()

AdjustRight(TableData)
