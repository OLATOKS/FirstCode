import re

Text = input("Type your word \n")
def strip(CorrectedWord):
   ImproveText = re.sub(r'^\s+|\s+$', '',CorrectedWord)
   print(ImproveText)
strip(Text)