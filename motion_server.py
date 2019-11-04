#shell: uvicorn motion_server:app --reload

from fastapi import FastAPI
import gclib
import numpy as np

setupd = {'count_to_mm':154.1133/985482.0,
          'galil_ip_str' : '192.168.200.23',
          'def_speed_count_sec':20000,
          'max_speed_count_sec':25000,
          'ipstr':'192.168.200.23',
          'axis_id':{'x':'D','y':'A','z':'B','s':'C','t':'E','u':'F'},
          'axlett':'ABCD'}


if __main__:
    #if this is the main instance let us make a galil connection
    g = gclib.py()
    print('gclib version:', g.GVersion())
    g.GOpen('%s --direct -s ALL' %(setupd['galil_ip_str']))
    print(g.GInfo())
    c = g.GCommand #alias the command callable
    app = FastAPI()


@app.put("/motor/move/{x}")
def motor_move(x_mm: float,axis: str,speed=None,mode='relative'):
    #this function moves the motor by a set amount of milimeters
    #you have to specify the axis, 
    #if no axis is specified this function throws an error
    #if no speed is specified we use the default slow speed 
    #as specified in the setupdict
    
    #example: move the motor 5mm to the positive direction:
    #motor_move(5,'x')
    
    #first we check if we have the right axis specified
    if axis in setupd['axis_id'].keys():
        ax = setupd['axis_id'][axis]
    else:
        return {'moved_axis':None,
                'speed':None,
                'accepted_rel_dist':None,
                'supplied_rel_dist':x_mm,
                'err_dist':None,
                'err_code':'setup'}
    
    #recalculate the distance in mm into distance in counts
    try:
        float_counts = x_mm/setupd['count_to_mm']#calculate float dist from steupd
        counts = int(np.floor(float_counts))#we can only mode full counts
        #save and report the error distance
        error_distance = setupd['count_to_mm']*(float_counts-counts)
        
        #check if a speed was upplied otherwise set it to standart
        if speed == None:
            speed = setupd['def_speed_count_sec']
        else:
            speed = int(np.floor(speed))
    
        if speed>setupd['max_speed_count_sec']:
            speed = steupd['max_speed_count_sec']
    
    except:
        #something went wrong in the numerical part so we give that as feedback
        return {'moved_axis':None,
                'speed':None,
                'accepted_rel_dist':None,
                'supplied_rel_dist':x_mm,
                'err_dist':None,
                'err_code':'numerical'}
    try:
        #the logic here is that we assemble a command sequence 
        #here we decide if we move relative, home, or move absolute
        if mode not in ['relative','absolute','homing']:
            raise cmd_exception
            
        cmd_seq = ['AB',
                   'MO',
                   'SH',
                   'SP{}={}'.format(ax,speed)]
        if mode=='relative':
            cmd_seq.append('PR{}={}'.format(ax,counts))
        if mode == 'homing':
            cmd_seq.append('HM{}'.format(ax))
        if mode == 'absolute':
            #now we want an abolute position
            #identify which axis we are talking about
            axlett = {l:i for i,l in enumerate(setupd['axlett'])}
            cmd_str = 'PA '+','.join(str(0) if ax!=lett 
                                     else str(counts)
                                     for lett in setupd['axlett'])
            cmd_seq.append(cmd_str)
        cmd_seq.append('BG{}'.format(ax))
            
        ret = ''
        for cmd in cmd_seq:
            _ = c(cmd)
            ret.join(_)

        return {'moved_axis':ax,
                'speed':speed, 
                'accepted_rel_dist':None,
                'supplied_rel_dist':x_mm,
                'err_dist':error_distance,
                'err_code':0}
    except:
        return {'moved_axis':None,
                'speed':None,
                'accepted_rel_dist':None,
                'supplied_rel_dist':x_mm,
                'err_dist':None,
                'err_code':'motor'}

def disconnect():
    try:
      None
    except gclib.GclibError as e:
      print('Unexpected GclibError:', e)
    finally:
      g.GClose() #don't forget to close connections!
    return {'connection': 'motor_offline'}


def query_all_axis_positions():
    #first query the actual position
    ret = c('TP') # query position of all axis
    #now we need to map these outputs to the ABCDEFG... channels
    #and then map that to xyz so it is humanly readable
    inv_axis_id = {d:v for v,d in setupd['axis_id'].items()}
    ax_abc_to_xyz = {l:inv_axis_id[l] for i,l in enumerate(setupd['axlett'])}
    pos = {axl:int(r) for axl,r in zip(setupd['axlett'],ret.split(', '))}
    #return the results through calculating things into mm
    return {ax_abc_to_xyz[k]:p*setupd['count_to_mm'] for k,p in pos.items()}


def query_axis(ax):
    q = query_all_axis_positions()
    if ax in q.keys():
        return {'ax':ax,'position':q[ax]}
    else:
        return {'ax':None,'position':None}
    
    
def query_moving():
    #this function queries the galil motor controller if any of 
    #it's motors are moving if so it returns moving as a 
    #motor_status otherwise stopped. Stopping codes can mean different things
    #here we just want to know if is is moving or not
    ret = c('SC')
    inv_axis_id = {d:v for v,d in setupd['axis_id'].items()}
    ax_abc_to_xyz = {l:inv_axis_id[l] for i,l in enumerate(setupd['axlett'])}
    for axl,r in zip(setupd['axlett'],ret.split(', ')):
        if int(r)==0:
            return {'motor_status':'moving'}
    return {'motor_status':'stopped'}

def motor_off():
        #sometimes it is useful to turn the motors off for manual alignment
        #this function does exactly that
        #It then returns the status
        #and the current position of all motors
        cmd_seq = ['AB','MO']
        for cmd in cmd_seq:
            _ = c(cmd)
        ret = query_moving()
        ret.update(query_all_axis_positions())
        return ret

def motor_on():
        #sometimes it is useful to turn the motors back on for manual alignment
        #this function does exactly that
        #It then returns the status
        #and the current position of all motors
        cmd_seq = ['AB','SH']
        for cmd in cmd_seq:
            _ = c(cmd)
        ret = query_moving()
        ret.update(query_all_axis_positions())
        return ret

def motor_stop():
        #this immediately stopps all motions turns off themotors for a short
        #time and then turns them back on. It then returns the status
        #and the current position of all motors
        cmd_seq = ['AB','MO','SH']
        for cmd in cmd_seq:
            _ = c(cmd)
        ret = query_moving()
        ret.update(query_all_axis_positions())
        return ret
