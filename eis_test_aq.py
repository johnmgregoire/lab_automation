# -*- coding: utf-8 -*-
# Get comtypes from:
# sourceforge -- http://sourceforge.net/projects/comtypes/files/comtypes/
# or
# PyPI -- https://pypi.python.org/pypi/comtypes
from __future__ import print_function
import comtypes
import comtypes.client as client
import numpy as np
from tqdm import tqdm
GamryCOM = client.GetModule(['{BD962F0D-A990-4823-9CF5-284D1CDD9C6D}', 1, 0])


# Alternatively:
# GamryCOM=client.GetModule(r'C:\Program Files\Gamry Instruments\Framework 6\GamryCOM.exe')

# utilities: #####################
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

    def cook(self):
        count = 1
        while count > 0:
            count, points = self.dtaq.Cook(10)
            # The columns exposed by GamryDtaq.Cook vary by dtaq and are
            # documented in the Toolkit Reference Manual.
            self.acquired_points.extend(zip(*points))

    def _IGamryDtaqEvents_OnDataAvailable(self, this):
        self.cook()

    def _IGamryDtaqEvents_OnDataDone(self, this):
        self.cook()  # a final cook
        # TODO:  indicate completion to enclosing code?


###############################

devices = client.CreateObject('GamryCOM.GamryDeviceList')
print(devices.EnumSections())

pstat = client.CreateObject('GamryCOM.GamryPC6Pstat')
pstat.Init(devices.EnumSections()[0])  # grab first pstat

################################ OCV

dtaqcpiv = client.CreateObject('GamryCOM.GamryDtaqOcv')
pstat.Open()
dtaqcpiv.Init(pstat)
pstat.SetCell(GamryCOM.CellOn)
dtaqsink = GamryDtaqEvents(dtaqcpiv)
connection = client.GetEvents(dtaqcpiv, dtaqsink)
try:
    dtaqcpiv.Run(True)
except Exception as e:
    raise gamry_error_decoder(e)
client.PumpEvents(3)
pstat.SetCell(GamryCOM.CellOff)
pstat.Close()


################################ EIS
from tqdm import tqdm
Zreal,Zimag,Zsig,Zphz,Zfreq = [],[],[],[],[]
is_on = False
pstat.Open()
for f in tqdm(np.logspace(0,5,60)):

    dtaqcpiv = client.CreateObject('GamryCOM.GamryDtaqEis')
    dtaqcpiv.Init(pstat,f,0.1,0.5,2)
    dtaqcpiv.SetCycleMin(10)
    dtaqcpiv.SetCycleMax(5000)

    if not is_on:
        pstat.SetCell(GamryCOM.CellOn)
        is_on = True
    dtaqsink = GamryDtaqEvents(dtaqcpiv)

    connection = client.GetEvents(dtaqcpiv, dtaqsink)

    try:
        dtaqcpiv.Run(True)
    except Exception as e:
        raise gamry_error_decoder(e)
    if f<10:
        client.PumpEvents(10)
    else:
        client.PumpEvents(1)

    Zreal.append(dtaqsink.dtaq.Zreal())
    Zimag.append(dtaqsink.dtaq.Zimag())
    Zsig.append(dtaqsink.dtaq.Zsig())
    Zphz.append(dtaqsink.dtaq.Zphz())
    Zfreq.append(dtaqsink.dtaq.Zfreq())
    print(dtaqsink.dtaq.Zfreq())
    del connection
pstat.SetCell(GamryCOM.CellOff)
pstat.Close()

import matplotlib.pyplot as plt
plt.scatter(np.array(Zreal),-np.array(Zimag),c=np.log(Zfreq))
plt.colorbar()
plt.axis('equal')
plt.show()


from impedance.circuits import CustomCircuit
frequencies = np.array(Zfreq)
Z = np.array(Zreal)+1j*np.array(Zimag)
circuit = 'R0-p(R1,C1)'
guess = [np.min(Z.real),np.max(Z.real),10**-6]
circuit_mod = CustomCircuit(circuit,initial_guess=guess)
circuit_mod.fit(frequencies, Z)

Z_fit = circuit_mod.predict(frequencies)

import matplotlib.pyplot as plt
from impedance.plotting import plot_nyquist

fig, ax = plt.subplots()
plot_nyquist(ax, frequencies, Z, fmt='o')
plot_nyquist(ax, frequencies, Z_fit, fmt='-')

plt.legend(['Data', 'Fit'])
plt.show()
