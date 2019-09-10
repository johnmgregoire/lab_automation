import sys
import string
import gclib
from private_vars import galil_ip_str

g = gclib.py()

print('gclib version:', g.GVersion())
g.GOpen('%s --direct -s ALL' %(galil_ip_str))
print(g.GInfo())


c = g.GCommand #alias the command callable
c('AB') #abort motion and program
c('MO') #turn off all motors
c('SHD') #axis D
c('SPD=32000') # Set speed, axis D, 32,000 cts/sec

c('PRD=3000') # Position Relative axis D, 3000 cts
c('BGD') # begin motion axis D

c('PR ?') # query position
c('TP')


c('HM') # set homing mode
c('BGD') # home axis D

c('PA 0, 0, 0, 0') # Position Absolute
c('BGD') # begin motion axis D

del c #delete the alias

try:
  None
except gclib.GclibError as e:
  print('Unexpected GclibError:', e)
finally:
  g.GClose() #don't forget to close connections!


#%%
