# :sparkles: Lab automation with python :sparkles:
This is to develop YACOS - yet another chemistry orchestration software. This tries to solve the problem of having multiple devices in an instrument that work at the same time with dangerous racing conditions by using asyncio and dedicated servers for all instruments. 
## Task servers
Independent services, synchronization handled by client
- XYZ Motion & IO
  - Report position :green_heart:
  - Move to position :green_heart:
  - Abort motion :green_heart:
  - Check status (ready, moving, locked) :green_heart:
  - Signal input / output :green_heart:
- Electrochemistry
  - Data aquisition :green_heart:
  - Potentiostat control :yellow_heart:
  - Broadcast live data :red_heart:
  - Check status (idle, measuring) :yellow_heart:
- Display
  - Dashboard :heart:
  - Live measurement view :heart:
  - Saved data inspection :heart:
 

## Automation setup (client)
- Handles motion calibration
- Generates ordered sample / position list for measurement
- Generates technique list and parameters
- Defines pre/post/maintenance actions
- Writes automation parameters to disk

## Automation scheduler (client)
- Executes experiment techniques in order
- Control (start, stop now, stop after sample)
- Writes scheduler state to disk
- Packages data (rcp, exp, ana)


Install gclib (provides python module)
http://www.galil.com/sw/pub/all/rn/gclib.html
http://www.galil.com/sw/pub/win/gclib/galil_gclib_449.exe

GalilTools (controller initialization)
http://www.galil.com/sw/pub/win/galiltools/GalilTools-1.6.4.580-Win-x64.exe

If no IP address is set:
    connect via USB with GalilTools
    issue commands:
        IA ? # show current ip address
        DH 0 # disable DHCP mode
        IA 192,168,1,10 # set ip address to 192.168.1.10
        SM 255,255,255,0 # set subnet mask
        BN # burn parameters
        IA ? # show current ip address
        

gclib python module tested with python 3.7.4
    copy "C:\Program Files (x86)\Galil\gclib\source" to writable directory
    cd to source\wrappers\python and execute: 
        python setup.py build
        python setup.py install
