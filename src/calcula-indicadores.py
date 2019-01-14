import os
from datetime import datetime

# myFile = open('/home/franciclo/git/indicadores-portal-datos-abiertos/src/append.txt', 'a')
myFile = open('/usr/src/append.txt', 'a')
myFile.write('\nAccessed on ' + str(datetime.now()))

myFile.close()
