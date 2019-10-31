import time

class Instrument():
    def __init__(self,device_setups,action_setups):
        self.device_blockages = {}
        self.devices = {}
        self.actions = {}

        for setup in device_setups:
            self.devices[setup['name']] = Device(setup)

        for setup in action_setups:
            self.actions[setup['name']] = Action(setup)

    def pass_time(self):
        for name,device in self.devices.items():
            self.set_device_blockages(name,-1)
        time.sleep(0.001)

    def set_device_blockages(self,name,time):
        self.devices[name].blockage += time
        if self.devices[name].blockage <0:
            self.release_device(name)

    def release_device(name):
        self.devices[name].blockage = 0

    def show_blockages(self):
        for name,device in self.devices.items():
            if device.blockage == 0:
                print(name + ' is available')
            else:
                print(name + ' is blocked for ' + str(device.blockage))


class Device():
    def __init__(self,setup):
        self.name = setup['name']
        self.blockage = setup['blockage']

    def interface():
        import numpy as np
        return {'measurement':np.random.rand()}

class Action(Instrument):
    def __init__(self,setup):
        self.req_avail_devices = setup['req_avail_devices'] #a list of device identifiers
        self.blocking_devices = setup['blocking_devices'] #a dict of device identifiers and times

        self.hook_in = setup['hook_in'] #a value to be evaluated by the to be overloaded hook function True=it breaks something
        self.hook_while = setup['hook_while'] #same just checked while experiment is performed

        self.name = setup['name']

    def call(self,exp_json):
        self.hook()
        self.check_availability()
        self.set_blocks()
        self.exp(exp_json)
        self.release_blocks()

    def hook(self):
        #override this function with a lambda
        if self.hook_in:
            pass
        else:
            pass

    def check_availability(self):
        availability = 2

        while availability != 1:
            for requisite_str in self.req_avail_devices:
                if super().device_blockages[requisite_str] > 0: #list stores blocking in miliseconds
                    availability *= 0
                else:
                    if availability == 2:
                        availability = 1
                    availability *= 1
            super().pass_time(1)

    def set_blocks(self):
        for device,time in self.blocking_devices.items():
            super().set_device_blockages(device,time)

    def hook_while_exp(self):
        print('No hok excecuted!!')
        pass

    def exp(self,exp_json):
        print(exp_json)
        for i in range(3):
            self.hook_while_exp()

    def release_blocks(self):
        #only nessesary if experiment finshed early i.e. if hook_exp weas called
        for device,time in self.blocking_devices.items():
            super().release_device(device)



device_setups = [{'name':'pump','blockage':0},
           {'name':'motor','blockage':0},
           {'name':'switch','blockage':0},
           {'name':'potentiostat','blockage':0}]

action_setups = [{'name':'move','req_avail_devices':['motor'],'blocking_devices':{'potentiostat':100},'hook_in':False,'hook_while':False},
                {'name':'measure_cv','req_avail_devices':['potentiostat','motor'],'blocking_devices':{'potentiostat':3000,'motor':3000,'switch':3000},'hook_in':False,'hook_while':False},
                {'name':'flush_reference','req_avail_devices':['potentiostat'],'blocking_devices':{'motor':1000},'hook_in':False,'hook_while':False},
                {'name':'switch_on_light_30ms','req_avail_devices':[],'blocking_devices':{'switch':30},'hook_in':False,'hook_while':False},
                {'name':'switch_off_light_20ms','req_avail_devices':[],'blocking_devices':{'switch':30},'hook_in':False,'hook_while':False}]

Action()

myRobot = Instrument(device_setups,action_setups)
myRobot.show_blockages()
