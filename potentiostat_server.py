# shell: uvicorn motion_server:app --reload

from fastapi import FastAPI
import comtypes
import comtypes.client as client
import uvicorn
import pickle
import os
import collections
from pydantic import BaseModel
setupd = {'path_to_gamrycom': r'C:\Program Files (x86)\Gamry Instruments\Framework\GamryCOM.exe',
          'temp_dump': r'C:\Users\hte\Documents\lab_automation\temp'}
app = FastAPI()


# definition of error handling things from gamry
class GamryCOMError(Exception):
    pass


def gamry_error_decoder(e):
    if isinstance(e, comtypes.COMError):
        hresult = 2 ** 32 + e.args[0]
        if hresult & 0x20000000:
            return GamryCOMError('0x{0:08x}: {1}'.format(2 ** 32 + e.args[0], e.args[1]))
    return e


class GamryDtaqEvents(object):
    def __init__(self, dtaq):
        self.dtaq = dtaq
        self.acquired_points = []
        self.status = "idle"

    def cook(self):
        count = 1
        while count > 0:
            count, points = self.dtaq.Cook(1000)
            # The columns exposed by GamryDtaq.Cook vary by dtaq and are
            # documented in the Toolkit Reference Manual.
            self.acquired_points.extend(zip(*points))

    def _IGamryDtaqEvents_OnDataAvailable(self, this):
        self.cook()
        self.status = "measuring"

    def _IGamryDtaqEvents_OnDataDone(self, this):
        self.cook()  # a final cook
        self.status = "done"
        # TODO:  indicate completion to enclosing code?


class gamry():
    # since the gamry connection uses one class and it can be switched on or off with handoff and everythong
    # I decided to put the gamry in a class ... this puts the logic into this class and not like in the motion server
    # where the logic is spread across the functions. TODO: Decide which way to implement this and streamline everywhere
    def __init__(self):
        self.GamryCOM = client.GetModule(setupd['path_to_gamrycom'])

        self.devices = client.CreateObject('GamryCOM.GamryDeviceList')
        # print(devices.EnumSections())

        self.pstat = client.CreateObject('GamryCOM.GamryPC6Pstat')

        # print(devices.EnumSections())
        try:
            self.pstat.Init(self.devices.EnumSections()[0])  # grab first pstat
        except IndexError:
            print('No potentiostat is connected! Have you turned it on?')
        self.temp = []

    def open_connection(self):
        # this just tries to open a connection with try/catch
        try:
            self.pstat.Open()
            return {'potentiostat_connection': 'connected'}
        except:
            return {'potentiostat_connection': 'error'}

    def close_connection(self):
        # this just tries to close a connection with try/catch
        try:
            self.pstat.Close()
            return {'potentiostat_connection': 'closed'}
        except:
            return {'potentiostat_connection': 'error'}

    def measurement_setup(self, gsetup='sweep'):
        self.open_connection()
        if gsetup == 'sweep':
            g = "GamryCOM.GamryDtaqCpiv"
        if gsetup == 'cv':
            g = "IGamryDtaqRcv"
        self.dtaqcpiv = client.CreateObject(g)
        self.dtaqcpiv.Init(self.pstat)

        self.dtaqsink = GamryDtaqEvents(self.dtaqcpiv)

    def measure(self, sigramp):
        print('Opening Connection')
        ret = self.open_connection()
        print(ret)
        # push the signal ramp over
        print('Pushing')
        self.pstat.SetSignal(sigramp)

        self.pstat.SetCell(self.GamryCOM.CellOn)
        self.measurement_setup()
        self.connection = client.GetEvents(self.dtaqcpiv, self.dtaqsink)
        try:
            self.dtaqcpiv.Run(True)
        except Exception as e:
            raise gamry_error_decoder(e)
        self.data = collections.defaultdict(list)
        client.PumpEvents(0.001)
        sink_status = self.dtaqsink.status
        while sink_status != "done":
            client.PumpEvents(0.001)
            sink_status = self.dtaqsink.status
            dtaqarr = self.dtaqsink.acquired_points
            self.data = dtaqarr
        self.pstat.SetCell(self.GamryCOM.CellOff)
        self.close_connection()

    def dump_data(self, data):
        pickle.dump(data, open(os.path.join(setupd['temp_dump'], self.instance_id)))

    def potential_ramp(self, Vinit: float, Vfinal: float, ScanRate: float, SampleRate: float):
        # setup the experiment specific signal ramp
        sigramp = client.CreateObject("GamryCOM.GamrySignalRamp")
        sigramp.Init(self.pstat, Vinit, Vfinal, ScanRate, SampleRate, self.GamryCOM.PstatMode)
        # measure ... this will do the setup as well
        self.measure(sigramp)
        return {'measurement_type': 'potential_ramp',
                'parameters': {'Vinit': Vinit, 'Vfinal': Vfinal, 'ScanRate': ScanRate, 'SampleRate': SampleRate},
                'data': self.data}

    def potential_cycle(self, Vinit: float, Vfinal: float,
                        Vapex1: float, Vapex2: float,
                        ScanInit: float, ScanApex: float, ScanFinal: float,
                        HoldTime0: float, HoldTime1: float, HoldTime2: float,
                        Cycles: int, SampleRate: float,
                        control_mode: str):
        if control_mode == 'galvanostatic':
            # do something
            pass
        else:
            # do something else
            pass
        # setup the experiment specific signal ramp
        sigramp = client.CreateObject("GamryCOM.GamrySignalRupdn")
        sigramp.Init(self.pstat, Vinit, Vapex1, Vapex2, Vfinal, ScanInit, ScanApex, ScanFinal, HoldTime0, HoldTime1,
                     HoldTime2, SampleRate, Cycles, self.GamryCOM.PstatMode)
        # measure ... this will do the setup as well
        self.measure(sigramp)
        return {'measurement_type': 'potential_ramp',
                'parameters': {},
                'data': self.data}

class return_class(BaseModel):
    measurement_type: str
    parameters: dict
    data: list


@app.get("/potentiostat/get/potential_ramp")
async def pot_potential_ramp_wrap(Vinit: float, Vfinal: float, ScanRate: float, SampleRate: float):
    poti = gamry()
    return return_class(**poti.potential_ramp(Vinit, Vfinal, ScanRate, SampleRate))



@app.get("/potentiostat/get/potential_cycle")
def pot_potential_ramp_wrap(Vinit: float, Vfinal: float, Vapex1: float, Vapex2: float, ScanInit: float,
                                  ScanApex: float, ScanFinal: float, HoldTime0: float, HoldTime1: float,
                                  HoldTime2: float, Cycles: int, SampleRate: float, control_mode: str):
    poti = gamry()
    return_msg = poti.potential_cycle(Vinit, Vfinal, Vapex1, Vapex2, ScanInit, ScanApex, ScanFinal, HoldTime0,
                                            HoldTime1, HoldTime2, Cycles, ScanRate, SampleRate, control_mode)
    return return_msg


@app.on_event("shutdown")
def shutdown_event():
    # this gets called when the server is shut down or reloaded to ensure a clean
    # disconnect ... just restart or terminate the server
    poti.close_connection()
    loop.close()
    return {'shutdown'}


if __name__ == "__main__":
    # makes this runnable and debuggable in VScode
    # letters of the alphabet GAMRY => G6 A0 M12 R17 Y24
    uvicorn.run(app, host="127.0.0.1", port=8003)

# http://127.0.0.1:8003/potentiostat/get/potential_ramp?Vinit=0&Vfinal=0.2&ScanRate=0.01&SampleRate=0.01
