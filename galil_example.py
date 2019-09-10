import sys
import string
import gclib

g = gclib.py()

print('gclib version:', g.GVersion())
g.GOpen('192.168.1.10 --direct -s ALL')
print(g.GInfo())


c = g.GCommand #alias the command callable
c('AB') #abort motion and program
c('MO') #turn off all motors
c('SHD') #servo A
c('SPD=32000') #speead, 1000 cts/sec
c('PRD=3000') #relative move, 3000 cts

c('BGD') #begin motion

c('PR ?')
c('TP')

c('HM')
c('BGD')

c('PA 0, 0, 0, 0')
c('BGD')

del c #delete the alias

try:
  None
except gclib.GclibError as e:
  print('Unexpected GclibError:', e)
finally:
  g.GClose() #don't forget to close connections!


#%%
